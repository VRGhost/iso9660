from .dir import Dir
from .file import File
from .isoRecord import IsoDirectoryRecord

class RootDir(Dir):

    path = property(lambda s: s._pp.sep)

    def __init__(self, pvd, inputStream, record):
        super(RootDir, self).__init__(None, inputStream, record)
        assert self.name == "\x00", repr(self.name)
        self.pvd = pvd

    def _recordClasses(self):
        # Return classes to be used for Dir and File records
        return (Dir, File)

    @classmethod
    def fromStream(cls, pvd, inputStream):
        rec = IsoDirectoryRecord(inputStream)
        return cls(pvd, inputStream, rec)