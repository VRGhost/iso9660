import posixpath as pp

class IsoRecord(object):
    """Iso fs record."""

    name = property(lambda s: s._data["name"])
    path = property(lambda s: pp.join(s.parent.path, s.name))
    isDir = False

    def __init__(self, parent, inputStream, data):
        self.parent = parent
        self._inputStream = inputStream
        self._data = data

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.path)