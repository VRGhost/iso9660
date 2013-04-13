class ISO9660IOError(IOError):
    def __init__(self, path):
        self.path = path

    def __str__(self):
        return "Path not found: {}".format(self.path)

class EndOfSectorError(Exception):
    pass

class IsoDirectoryRecordParseError(Exception):
    pass

class NullIsoDirectoryRecordParseError(IsoDirectoryRecordParseError):
    pass