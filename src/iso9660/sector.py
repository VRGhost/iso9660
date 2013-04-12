import struct
import datetime

class SectorReader(object):
    """An iso sector."""

    _length = _read = 0

    def __init__(self, parent, stream, len):
        self.input = stream
        self.getSector = parent.getSector
        self._length = len
        self._read = 0

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
        txt = self.unpackRaw(17)
        print repr(txt)
        return txt

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

    def skip(self, l):
        # Just a shorthand
        self.unpackRaw(l)

    def unpackRaw(self, l):
        self._read += l
        return self.input.read(l)

    def tell(self):
        return self._read

    def __len__(self):
        return self._length - self._read