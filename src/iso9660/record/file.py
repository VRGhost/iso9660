from .fsRecord import IsoRecord

class File(IsoRecord):
    """An ISO file."""

    def stream(self):
        secId = self._data["ex_loc"]
        secLen = self._data["ex_len"]
        return self._inputStream.getSector(secId, secLen)

    def read(self):
        return self.stream().unpackRaw(len(self))

    def __len__(self):
        return self._data["ex_len"]