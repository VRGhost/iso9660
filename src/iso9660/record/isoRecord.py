class IsoDirectoryRecord(object):

    def __init__(self, inp):
        start = inp.tell()

        self.length = inp.unpackByte()
        self.extendedAttrLength = inp.unpackByte()
        self.extent = (inp.unpackBoth('I'), inp.unpackBoth('I')) # (location, length)
        self.timestamp = inp.unpackDirDatetime()
        self.flags = flags = inp.unpackByte()
        self.interleave = (inp.unpackByte(), inp.unpackByte()) # (file_unit_size, gap_size)
        self.volumeSeq = inp.unpackBoth('h')
        self.nameLen = nameLen = inp.unpackByte()
        self.rawName = name = inp.unpackString(nameLen)
        self.name = name.rsplit(';', 1)[0]
        if nameLen % 2 == 1:
            # padding
            inp.skip(1)

        self._totalLen = inp.tell() - start

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

    def __len__(self):
        return self._totalLen