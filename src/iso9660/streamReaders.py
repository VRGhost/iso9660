import os
import urllib

from .sector import SectorReader

class StreamReader(object):
    """An object that performs source iso seek operations."""

    def __init__(self, location):
        self.source = location

    def getSector(self, id, len):
        raise NotImplementedError

class FileReader(StreamReader):
    """Reading iso from local file system."""

    def __init__(self, location):
        super(FileReader, self).__init__(location)
        self._fobj = open(location, "rb")

    def getSector(self, id, len):
        return SectorReader(self, _ReadSlice(self._fobj, id * 2048, len))

class HttpReader(StreamReader):
    """Reading iso trough http connection."""

    def getSector(self, id, len):
        start = id * 2048
        opener = urllib.FancyURLopener()
        opener.http_error_206 = lambda *a, **k: None
        opener.addheader("Range", "bytes=%d-%d" % (start, start+length-1))
        return opener.open(self.source)

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
