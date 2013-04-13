from .fsRecord import IsoRecord

class File(IsoRecord):
    """An ISO file."""

    def stream(self):
        return self._inp.getSectorHeadBytes(*self.extent)

    def read(self):
        return self.stream().unpackRaw(len(self))

    def __len__(self):
        return self._data.extent[1]