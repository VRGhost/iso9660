import os
import itertools

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .exceptions import ISO9660IOError
from .streamReaders import FileReader, HttpReader
from . import volumeDescriptors as vd

class ISO9660(object):

    # PVDs
    bootRecord = primary = None

    root = property(lambda s: s.primary.rootDir)
    formatVersion = property(lambda s: s.primary.fileStructureVersion)

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
        while True:
            sector = self._ds.getSector(sectorId.next(), 2048)
            typ = sector.unpackByte()
            if typ == 255:
                # Type 255 is "Volume Descriptor Set Terminator"
                break
            if typ == 0:
                self.bootRecord = vd.Boot(sector)
            elif typ == 1:
                self.primary = vd.Primary(sector)
            elif typ == 2:
                # Supplementary volume descriptor
                1/0
                pass
            elif typ == 3:
                # Volume Partition Descriptor
                2/0
                pass 
            else:
                 raise Exception("Unexpected PVD type {!r}".format(typ))

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