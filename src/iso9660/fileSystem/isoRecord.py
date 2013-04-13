from .. import exceptions

class IsoDirectoryRecord(object):

    def __init__(self, inp):
        start = inp.tell()

        self.declaredLength = inp.unpackByte()
        if self.declaredLength < 33:
            # If declared length is smaller than minimum possible size of this
            # structure, than something is not good
            if self.declaredLength == 0:
                raise exceptions.NullIsoDirectoryRecordParseError(self.declaredLength)
            else:
                raise exceptions.IsoDirectoryRecordParseError(self.declaredLength)

        self.extendedAttrLength = inp.unpackByte()
        self.extent = (inp.unpackBoth('I'), inp.unpackBoth('I')) # (location, length)
        self.timestamp = inp.unpackDirDatetime()
        self.flags = flags = inp.unpackByte()
        self.interleave = (inp.unpackByte(), inp.unpackByte()) # (file_unit_size, gap_size)
        self.volumeSeq = inp.unpackBoth('h')
        self.nameLen = nameLen = inp.unpackByte()
        self.rawName = name = inp.unpackString(nameLen)
        self.name = name.rsplit(';', 1)[0]
        if nameLen % 2 == 0:
            # padding
            inp.skip(1)

        realLength = inp.tell() - start

        systemUseLen = self.declaredLength - realLength
        assert systemUseLen >= 0, systemUseLen
        if systemUseLen > 0:
            inp.skip(systemUseLen)

        # Optional padding byte may be added
        parsed = inp.tell() - start
        if parsed % 2 == 1:
            inp.skip(1)

        self.fsRecordSize = inp.tell() - start

        for (pos, name) in enumerate([
            "hidden", "isDir", "associatedFile",
            "extendedAttrRecordHasInfoOnThis",
            "permsInExtendedAttribute",
            None, None,
            "recordContinues",
        ]):
            if not name:
                # Reserved bit
                continue
            mask = 1 << pos
            val = bool(flags & mask)
            setattr(self, name, val)