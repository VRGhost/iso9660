from .isoRecord import IsoDirectoryRecord
from . import record

class Index(object):
    """File system index object."""

    def __init__(self, root):
        self.root = root
        self._cache = {}

    def parseExtent(self, vd, dataSrc, extent, parent):
        sector = dataSrc.getSectorHeadBytes(*extent)
        while True:
            sector.skipZeroes()
            if not sector.bytesLeft():
                break
            yield self.getFsObject(vd, sector, parent)

    def getFsObject(self, vd, sec, parentDir=None):
        pos = sec.getAbsolutePos()
        if pos not in self._cache:
            isoRec = IsoDirectoryRecord(sec)
            if isoRec.isDir:
                cls = record.Dir
            else:
                cls = record.File
            obj = self._mkFsObject(cls, vd, sec.getStream(), isoRec, parentDir)
            self._cache[pos] = rv = obj
        else:
            rv = self._cache[pos]
            sec.skip(rv.directoryRecord.fsRecordSize)
        return rv

    def locationOf(self, obj):
        for (loc, myObj) in self._cache.iteritems():
            if myObj == obj:
                return loc
        raise IndexError()

    def _mkFsObject(self, cls, vd, stream, record, parent):
        return cls(self.root, vd, stream, record, parent)