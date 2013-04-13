import posixpath

from iso9660 import exceptions

from .fsRecord import IsoRecord
from .file import File

_NULL_ = object()

class Dir(IsoRecord):
    """Directory Record."""

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
        sep = posixpath.sep
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

    @property
    def children(self):
        ignoreExtents = [self.extent]
        if self.parentDir:
            ignoreExtents.append(self.parentDir.extent)
        for el in self.contents:
            if el.extent in ignoreExtents:
                continue
            yield el

    _contents = None
    @property
    def contents(self):
        if not self._contents:
            self._contents = tuple(self.root.fs.parseExtent(
                self.vd, self._inp, self.extent, self
            ))
        return self._contents

    @property
    def name(self):
        if not self.parentDir:
            rv = posixpath.sep
        else:
            rv = super(Dir, self).name
        return rv

    @property
    def path(self):
        sep = posixpath.sep
        oldPath = super(Dir, self).path.rstrip(sep)
        return oldPath + sep

    _myPathRecord = _NULL_
    @property
    def pathTableRecord(self):
        if self._myPathRecord == _NULL_:
            myExtentLocation = self.extent[0]
            for rec in self.vd.pathTable:
                if rec.extentLocation == myExtentLocation:
                    n1 = self._data.name.upper()
                    n2 = rec.name.upper()
                    assert n1 == n2, (n1, n2)
                    self._myPathRecord = rec
                    break
            else:
                self._myPathRecord = None
        return self._myPathRecord