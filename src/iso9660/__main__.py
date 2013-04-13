import argparse
import os
import sys
import logging
import posixpath

#logging.basicConfig(level=logging.DEBUG)

def get_parser():
    parser = argparse.ArgumentParser(description='Read ISO (ISO-9660 encoded) disk images.')
    parser.add_argument("target", help="Target ISO file")
    parser.add_argument("--list", nargs='*', help="List contents of the ISO")
    parser.add_argument("--recursive", action="store_true", default=False, help="Perform directory listing recursively.")
    parser.add_argument("--list_dirs", action="store_true", default=False, help="List directories.")
    parser.add_argument("--cat", nargs='+', default=(), help="Print contents of a file to stdout.")
    return parser

def inject_module_to_namespace():
    myDir = os.path.abspath(os.path.dirname(__file__))
    moduleDir = os.path.realpath(os.path.join(myDir, ".."))
    if os.path.abspath(sys.path[0]) == myDir:
        sys.path.pop(0)
    sys.path.insert(0, moduleDir)

if __name__ == "__main__":
    parser = get_parser()
    inject_module_to_namespace()

    import iso9660

    args = parser.parse_args()

    reader = iso9660.ISO9660(args.target)

    if args.list_dirs:
        for el in reader.primary.pathTable:
            print el.path

    if args.list is not None:
        dirList = list(args.list)
        if not dirList:
            dirList.append(posixpath.sep)
        for rootName in dirList:
            el = reader.find(rootName)
            if not el:
                logging.warning("Failed to locate directory {!r}".format(rootName))
                continue
            if args.recursive:
                it = el.walk()
            else:
                it = el.list()
            for rec in it:
                print rec.path

    for fname in args.cat:
        obj = reader.find(fname)
        if obj:
            if obj.isDir:
                logging.warning("{!r} is a directory".format(obj.path))
            else:
                print obj.read()
        else:
            logging.warning("File {!r} not found.".format(fname))