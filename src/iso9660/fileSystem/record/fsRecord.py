import posixpath as pp

class IsoRecord(object):
    """Iso fs record."""

    name = property(lambda s: s._data.name)
    directoryRecord = property(lambda s: s._data)
    isDir = property(lambda s: s._data.isDir)
    extent = property(lambda s: s._data.extent)

    def __init__(self, root, myVolumeDescriptor, inputStream, data, parentDir):
        self.root = root
        self.parentDir = parentDir
        self.vd = myVolumeDescriptor
        assert root
        self._inp = inputStream
        self._data = data

    @property
    def path(self):
        if self.parentDir:
            parentPath = self.parentDir.path
        else:
            parentPath = ""
        return pp.join(parentPath, self.name)

    _myAbsLocation = None
    @property
    def absoluteLocation(self):
        if not self._myAbsLocation:
            self._myAbsLocation = self.root.fs.locationOf(self)
        return self._myAbsLocation
        
    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.path)