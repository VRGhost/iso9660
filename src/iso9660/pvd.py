from .dir import RootDir

class PVD(object):
    """Primary volume descriptor object."""
  
    def __init__(self, inputStream):

        self._inputStream = inp = inputStream

        inputs = (
            ("type_code", inp.unpackString(5)),
            ("standard_identifier", inp.unpack('B')),
            (None, inp.unpackRaw(1)),                        #discard 1 byte
            ("system_identifier", inp.unpackString(32)),
            ("volume_identifier", inp.unpackString(32)),
            (None, inp.unpackRaw(8)),                        #discard 8 bytes
            ("volume_space_size", inp.unpackBoth('i')),
            (None, inp.unpackRaw(32)),                       #discard 32 bytes
            ("volume_set_size", inp.unpackBoth('h')),
            ("volume_seq_num", inp.unpackBoth('h')),
            ("logical_block_size", inp.unpackBoth('h')),
            ("path_table_size", inp.unpackBoth('i')),
            ("path_table_l_loc", inp.unpack('<i')),
            ("path_table_opt_l_loc", inp.unpack('<i')),
            ("path_table_m_loc", inp.unpack('>i')),
            ("path_table_opt_m_loc", inp.unpack('>i')),
            ("root_directory", RootDir.fromStream(self, inp)),      #root directory record
            ("volume_set_identifer", inp.unpackString(128)),
            ("publisher_identifier", inp.unpackString(128)),
            ("data_preparer_identifier", inp.unpackString(128)),
            ("application_identifier", inp.unpackString(128)),
            ("copyright_file_identifier", inp.unpackString(38)),
            ("abstract_file_identifier", inp.unpackString(36)),
            ("bibliographic_file_identifier", inp.unpackString(37)),
            ("volume_datetime_created", inp.unpackVdDatetime()),
            ("volume_datetime_modified", inp.unpackVdDatetime()),
            ("volume_datetime_expires", inp.unpackVdDatetime()),
            ("volume_datetime_effective", inp.unpackVdDatetime()),
            ("file_structure_version", inp.unpack('B')),
        )
        
        self._data = data = {}
        for (name, value) in inputs:
            if name:
                data[name] = value
        self.rootDir = data["root_directory"]

    _pathTable = None
    @property
    def pathTable(self):
        if not self._pathTable:
            self._pathTable = PathTable(
                self._inputStream,
                self._data['path_table_l_loc'],
                self._data['path_table_size'],
            )
        return self._pathTable

class PathTable(object):

    data = property(lambda s: tuple(s._data))

    def __init__(self, stream, sector, length):

        inp = stream.getSector(sector, length)
        toRead = length
        self._data = data = []

        while toRead > 0:
            p = {}
            l1 = inp.unpack('B')
            l2 = inp.unpack('B')
            p['ex_loc'] = inp.unpack('<I')
            p['parent'] = inp.unpack('<H')
            p['name']   = inp.unpackString(l1)

            if l1%2 == 1:
                inp.unpack('B')

            data.append(p)

            toRead -= 8 + l1 + (l1 % 2)

        assert toRead == 0

    def __iter__(self):
        return iter(self._data)