from .fsRecord import IsoRecord

from .file import File
from .isoRecord import IsoDirectoryRecord

class Dir(IsoRecord):
    """Directory Record."""

    path = property(lambda s: super(Dir, s).path + s._pp.sep)
    uid = property(lambda s: "|".join(str(el) for el in s._data.extent))
    isDir = True

    def list(self):
        """Iterate over contents of this directory."""
        return self.children

    def walk(self):
        for el in self.list():
            yield el
            if el.isDir:
                for child in el.walk():
                    yield child

    def find(self, absPath):
        absPath = absPath.upper()
        myPath = self.path.upper()
        if not absPath.startswith(myPath):
            return None
        elif absPath == myPath:
            return self
        else:
            for ch in self.list():
                chPath = ch.path.upper()
                if absPath.startswith(chPath):
                    if chPath == absPath:
                        return ch
                    else:
                        if ch.isDir:
                            return ch.find(absPath)

    _children = None
    @property
    def children(self):
        if not self._children:
            out = []
            secLen = self._data.extent[1]
            sector = self._inputStream.getSector(*self._data.extent)
            parsed = 0
            (dirCls, fileCls) = self._recordClasses()

            omitDirUids = [self.uid]
            if self.parent:
                omitDirUids.append(self.parent.uid)

            while parsed < secLen:
                rec = IsoDirectoryRecord(sector)
                parsed += len(rec)
                if rec.isDir:
                    obj = dirCls(self, self._inputStream, rec)
                    if obj.uid in omitDirUids:
                        # It is ether '.' or '..' directory
                        continue
                else:
                    obj = fileCls(self, self._inputStream, rec)
                out.append(obj)

            self._children = tuple(out)
        return self._children

    def _recordClasses(self):
        # Return classes to be used for Dir and File records
        return (type(self), File)