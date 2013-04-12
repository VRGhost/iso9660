from ..record import RootDir

class Primary(object):
    """Primary volume descriptor object."""
  
    def __init__(self, inputStream):

        self._inputStream = inp = inputStream

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
        self.rootDir = RootDir.fromStream(self, inp)
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
                self._inputStream.getSector(*self.pathTableL),
                "<"
            )
        return self._pathTable

class PathTable(object):

    data = property(lambda s: tuple(s._data))

    def __init__(self, inp, direction):

        toRead = len(inp)
        self._data = data = []

        while toRead > 0:
            el = PathTableRecord(inp, direction)
            toRead -= len(el)
            data.append(el)
        assert toRead == 0

    def __iter__(self):
        return iter(self._data)

class PathTableRecord(object):

    def __init__(self, inp, direction):
        startAddr = inp.tell()

        self.dirIdLength = inp.unpackByte()
        self.extAttrRecordLen = inp.unpackByte()
        self.extendLocation = inp.unpack(direction + "I")
        self.parentDirId = inp.unpack(direction + "H")
        self.name = inp.unpackString(self.dirIdLength)
        # Padding byte
        if self.dirIdLength % 2 == 1:
            inp.skip(1)

        self._byteLen = inp.tell() - startAddr

    def __len__(self):
        return self._byteLen