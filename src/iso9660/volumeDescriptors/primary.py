import posixpath

class Primary(object):
    """Primary volume descriptor object."""

    inputStream = property(lambda s: s._inputStream)
  
    def __init__(self, root, sector):

        inp = sector
        self._inputStream = inp.getStream()
        self.root = root

        # See http://users.telenet.be/it3.consultants.bvba/handouts/ISO9960.html
        self.id = inp.unpackString(5)
        self.version = inp.unpackByte()
        inp.skip(1) # unused1
        self.systemId = inp.unpackString(32)
        self.volumeId = inp.unpackString(32)
        inp.skip(8) # unused2
        self.volumeSpaceSize = inp.unpack733()
        inp.skip(32) # unused3
        self.volumeSetSize = inp.unpack723()
        self.volumeSeqNum = inp.unpack723()
        self.logicalBlockSize = inp.unpack723()
        self.pathTableSize = inp.unpack733()
        self.pathTableL = (inp.unpack("<i"), inp.unpack("<i")) # (location, optional_location)
        self.pathTableM = (inp.unpack(">i"), inp.unpack(">i"))
        self.rootDir = self.root.fs.getFsObject(self, inp)
        self.volumeSetId = inp.unpackString(128)
        self.publisherId = inp.unpackString(128)
        self.applicationId = inp.unpackString(128)
        self.copyrightFileId = inp.unpackString(38)
        self.abstractFileId = inp.unpackString(36)
        self.bibliographicFileId = inp.unpackString(37)
        self.volumeCreated = inp.unpackVdDatetime()
        self.volumeModified = inp.unpackVdDatetime()
        self.volumeExpires = inp.unpackVdDatetime()
        self.volumeEffective = inp.unpackVdDatetime()
        self.fileStructureVersion = inp.unpackByte()
        
    _pathTable = None
    @property
    def pathTable(self):
        if not self._pathTable:
            self._pathTable = PathTable(
                self,
                self._inputStream.getSectorHeadBytes(
                    self.pathTableL[0], self.pathTableSize),
                "<"
            )
        return self._pathTable

class PathTable(object):

    data = property(lambda s: tuple(s._data))

    def __init__(self, vd, inp, direction):
        self.vd = vd
        self._data = data = []

        while inp.bytesLeft() > 0:
            el = PathTableRecord(self, inp, direction)
            data.append(el)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, idx):
        return self._data[idx]

class PathTableRecord(object):

    def __init__(self, table, inp, direction):
        self.table = table

        startAddr = inp.tell()

        self.dirIdLength = inp.unpackByte()
        self.extAttrRecordLen = inp.unpackByte()
        self.extentLocation = inp.unpack(direction + "I")
        self.parentDirId = inp.unpack(direction + "H")
        self.name = inp.unpackString(self.dirIdLength)
        # Padding byte
        if self.dirIdLength % 2 == 1:
            inp.skip(1)

        self._byteLen = inp.tell() - startAddr

    _parentRec = None
    @property
    def parent(self):
        if not self._parentRec:
            pos = self.parentDirId
            assert pos > 0, "Indexes are starting with 1"
            self._parentRec = self.table[pos - 1]
        return self._parentRec

    @property
    def path(self):
        if self.parent == self:
            rv = posixpath.sep
        else:
            rv = posixpath.join(self.parent.path, self.name) + posixpath.sep
        return rv

    def __len__(self):
        return self._byteLen

    def __repr__(self):
        return "<{} {!r}>".format(
            self.__class__.__name__, self.path
        )