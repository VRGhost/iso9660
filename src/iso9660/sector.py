import struct

class SectorReader(object):
    """An iso sector."""

    def __init__(self, parent, stream):
        self.input = stream
        self.getSector = parent.getSector

    #both-endian
    def unpackBoth(self, st):
        a = self.unpack('<'+st)
        b = self.unpack('>'+st)
        assert a == b, (a, b)
        return a

    def unpackString(self, l):
        return self.unpackRaw(l).rstrip(' ')

    def unpackVdDatetime(self):
        return self.unpackRaw(17) #TODO

    def unpackDirDatetime(self):
        return self.unpackRaw(7) #TODO

    def unpackByte(self):
        return ord(self.unpackRaw(1))

    def unpack(self, structDef):
        assert structDef != "B"
        if structDef[0] not in ('<','>'):
            structDef = '<' + structDef

        size = struct.calcsize(structDef)
        data = self.unpackRaw(size)
        out = struct.unpack(structDef, data)

        if len(structDef) == 2:
            return out[0]
        else:
            return out

    def skip(self, l):
        # Just a shorthand
        self.unpackRaw(l)

    def unpackRaw(self, l):
        return self.input.read(l)