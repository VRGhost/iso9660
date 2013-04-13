import collections
import struct
import datetime
import logging

from . import exceptions

Sector = collections.namedtuple("Sector", ["id", "length", "blockSize"])
SectorPoint = collections.namedtuple("SectorPoint", ["sector", "byteOffset"])

class SectorReader(object):
    """An iso sector."""

    _length = _read = 0
    _pushedStr = ""

    def __init__(self, stream, dataSource, id, len, blockSize):
        assert len < 1000
        self.stream = stream
        self.input = dataSource
        self.id = Sector(id=id, length=len, blockSize=blockSize)
        self._read = 0
        self.setMaxBytes(len * blockSize)

    def unpack733(self):
        # 733 is "method 733" used in
        # http://users.telenet.be/it3.consultants.bvba/handouts/ISO9960.html
        return self.unpackBoth('i')

    def unpack723(self):
        # 723 is "method 723" used in
        # http://users.telenet.be/it3.consultants.bvba/handouts/ISO9960.html
        return self.unpackBoth('h')

    #both-endian
    def unpackBoth(self, st):
        a = self.unpack('<' + st)
        b = self.unpack('>' + st)
        assert a == b, (a, b)
        return a

    def unpackString(self, l):
        return self.unpackRaw(l).rstrip(' ')

    def unpackVdDatetime(self):
        txt = self.unpackRaw(17).strip()
        if not txt:
            return None
        else:
            raise NotImplementedError(txt)

    def unpackDirDatetime(self):
        (
            year, month, day,
            hour, minute, second,
            offset
        ) = self.unpackStruct("B" * 7)

        offset -= 48
        offset = datetime.timedelta(minutes=offset * 15)

        try:
            rv = datetime.datetime(
                1900 + year, month, day,
                hour, minute, second,
            )
        except ValueError:
            return None
        # convert to UTC
        return rv + offset

    def unpackByte(self):
        return ord(self.unpackRaw(1))

    def unpack(self, structDef):
        assert len(structDef) == 2, "Only primtive field parsing is supported."
        return self.unpackStruct(structDef)[0]

    def unpackStruct(self, structDef):
        size = struct.calcsize(structDef)
        data = self.unpackRaw(size)
        return struct.unpack(structDef, data)

    def skipZeroes(self):
        start = self.tell()
        spaceLeft = self.bytesLeft()
        while spaceLeft > 0:
            toRead = min(spaceLeft, 128)
            read = self.unpackRaw(toRead)
            spaceLeft -= len(read)
            read = read.lstrip('\x00')
            if read:
                break
        logging.debug("Skipped {} zero bytes.".format(self.tell() - start))
        self._pushedStr = read + self._pushedStr

    def skip(self, l):
        # Just a shorthand
        # Expecting for all skipped (reserved) bytes to be zero
        out = self.unpackRaw(l)
        if out.strip('\x00'):
            logging.debug("Skipping non-empty data {!r}".format(out))

    def unpackRaw(self, l):
        if self.tell() + l > self._length:
            raise exceptions.EndOfSectorError()

        out = self._pushedStr[:l]
        self._pushedStr = self._pushedStr[l:]
        toRead = l - len(out)
        if toRead:
            assert not self._pushedStr
            out += self.input.read(toRead)
            self._read += toRead
        assert len(out) == l
        return out

    def getStream(self):
        return self.stream

    def getAbsolutePos(self):
        return SectorPoint(sector=self.id, byteOffset=self.tell())

    def setMaxBytes(self, val):
        maxTheoreticalLen = self.id.length * self.id.blockSize
        assert val <= maxTheoreticalLen
        self._length = val

    def bytesLeft(self):
        return self._length - self.tell()

    def tell(self):
        rv = self._read - len(self._pushedStr)
        assert rv >= 0
        assert rv <= self._length, (rv, self._length)
        return rv