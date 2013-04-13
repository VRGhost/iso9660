import os
import urllib

from .sector import SectorReader

class StreamReader(object):
    """An object that performs source iso seek operations."""

    sectorSize = 2048

    def __init__(self, location):
        self.source = location

    def getSector(self, id, len, size=None):
        raise NotImplementedError

    def getSectorHeadBytes(self, id, bytes):
        sectorLen = self.bytesToSectorLen(bytes)
        sector = self.getSector(id, sectorLen)
        sector.setMaxBytes(bytes)
        return sector

    def bytesToSectorLen(self, cnt, size=None):
        if not size:
            size = self.sectorSize
        # Return number of sectors rounded up
        return (cnt + size - 1) // size

class FileReader(StreamReader):
    """Reading iso from local file system."""

    def __init__(self, location):
        super(FileReader, self).__init__(location)
        self._fobj = open(location, "rb")

    def getSector(self, id, len, size=None):
        if not size:
            size = self.sectorSize
        startByte = id * size
        byteCnt = len * size
        slice = _ReadSlice(self._fobj, startByte, byteCnt)
        return SectorReader(self, slice, id, len, size)

class HttpReader(StreamReader):
    """Reading iso trough http connection."""

    def getSector(self, id, len, size=None):
        if not size:
            size = self.sectorSize
        startByte = id * size
        byteCnt = len * size
        opener = urllib.FancyURLopener()
        opener.http_error_206 = lambda *a, **k: None
        opener.addheader("Range", "bytes={}-{}".format(
            startByte, startByte + byteCnt - 1))
        slice = opener.open(self.source)
        return SectorReader(self, slice, id, len, size)

class _ReadSlice(object):
    """A file-like object that draws source information from the seekable input file-like object."""

    def __init__(self, fobj, start, len):
        self._fobj = fobj
        self.start = start
        self.len = len
        self.readPos = start

    def read(self, byteCount):
        self._fobj.seek(self.readPos, 0)
        out = self._fobj.read(byteCount)
        if not out:
            raise EOFError()
        assert len(out) == byteCount, (out, byteCount)
        self.readPos += byteCount
        return out
