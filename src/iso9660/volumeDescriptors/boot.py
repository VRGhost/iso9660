class Boot(object):
    """Boot volume descriptor object."""

    type = 1

    def __init__(self, inputStream):
        self._inputStream = inp = inputStream
        self.id = inp.unpackString(5)
        assert self.id == "CD001", "Expecting static ID for boot record."
        self.version = inp.unpackByte()
        assert self.version == 1, "Boot record is expected to have version 1"
    
    _data = None
    @property
    def data(self):
        """Read 'data' in lazy mode as it is big and not necessary needed."""
        if not self._data:
            self._data = self._inputStream.unpackRaw(2041)
        return self._data