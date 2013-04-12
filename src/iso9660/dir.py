import posixpath as pp

from .fsRecord import IsoRecord

from .file import File

class Dir(IsoRecord):
    """Directory Record."""

    path = property(lambda s: super(Dir, s).path + pp.sep)
    uid = property(lambda s: "|".join(str(s._data[el]) for el in ("ex_loc", "ex_len")))
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
            secId = self._data["ex_loc"]
            secLen = self._data["ex_len"]
            sector = self._inputStream.getSector(secId, secLen)
            parsed = 0
            (dirCls, fileCls) = self._recordClasses()

            omitDirUids = [self.uid]
            if self.parent:
                omitDirUids.append(self.parent.uid)

            while parsed < secLen:
                (len, data) = self._unpackRecord(sector)
                parsed += len
                if data:
                    if data["flags"] & 2:
                        # This is directory
                        obj = dirCls(self, self._inputStream, data)
                        if obj.uid in omitDirUids:
                            # It is ether '.' or '..' directory
                            continue
                    else:
                        obj = fileCls(self, self._inputStream, data)
                    out.append(obj)

            self._children = tuple(out)
        return self._children

    def _recordClasses(self):
        # Return classes to be used for Dir and File records
        return (type(self), File)

    @classmethod
    def _unpackRecord(cls, stream):
        recordLen = stream.unpackByte()
        totalRecordLen = recordLen + 1 # For the byte we had read above

        if recordLen == 0:
            return (totalRecordLen, None)

        l1 = stream.unpackByte()

        d = {}
        d['ex_loc']               = stream.unpackBoth('I')
        d['ex_len']               = stream.unpackBoth('I')
        d['datetime']             = stream.unpackDirDatetime()
        d['flags']                = stream.unpackByte()
        d['interleave_unit_size'] = stream.unpackByte()
        d['interleave_gap_size']  = stream.unpackByte()
        d['volume_sequence']      = stream.unpackBoth('h')

        nameLen = stream.unpackByte()
        d['name'] = stream.unpackString(nameLen).split(';')[0].strip("\x00")
        if nameLen % 2 == 0:
            stream.unpackByte()

        # Skip padding
        t = 34 + nameLen - (nameLen % 2)
        e = recordLen - t
        if e > 0:
            stream.unpackRaw(e)

        return (totalRecordLen, d)

class RootDir(Dir):

    path = property(lambda s: pp.sep)

    def __init__(self, pvd, inputStream, record):
        super(RootDir, self).__init__(None, inputStream, record)
        assert not self.name, repr(self.name)
        self.pvd = pvd

    def _recordClasses(self):
        # Return classes to be used for Dir and File records
        return (Dir, File)

    @classmethod
    def fromStream(cls, pvd, inputStream):
        rec = cls._unpackRecord(inputStream)
        return cls(pvd, inputStream, rec[1])