import os
import itertools

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .exceptions import ISO9660IOError
from .streamReaders import FileReader, HttpReader
from .pvd import PVD

class ISO9660(object):

    root = property(lambda s: s._pvd.rootDir)

    def __init__(self, dataSource):
        if isinstance(dataSource, basestring):
            if dataSource.startswith("http"):
                dataSource = HttpReader(dataSource)
            elif os.path.isfile(dataSource):
                dataSource = FileReader(dataSource)
            else:
                raise Exception("Unknown data source {!r}".format(dataSource))

        self._ds = dataSource


        ### Volume Descriptors
        sectorId = itertools.count(0x10)
        typ = 42
        while typ != 255:
            sector = self._ds.getSector(sectorId.next(), 2048)
            typ = sector.unpack('B')
            if typ == 1:
                self._pvd = PVD(sector)

    def walk(self):
        """Recursively walk over all fs records in the ISO."""
        yield self.root
        for el in self.root.walk():
            yield el

    def listNames(self):
        """Return list of fs record names."""
        return (el.path for el in self.walk())

    def find(self, path):
        """Find and return object for the given path."""
        return self.root.find(path)

    def get(self, path):
        """Same as `find` but raises exception if object can not be found."""
        rv = self.find(path)
        if not rv:
            raise ISO9660IOError(path)
        return rv