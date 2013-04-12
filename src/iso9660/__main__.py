import argparse
import os
import sys

def get_parser():
    parser = argparse.ArgumentParser(description='Read ISO (ISO-9660 encoded) disk images.')
    parser.add_argument("target", help="Target ISO file")
    parser.add_argument("--list", action="store_true", default=False, help="List contents of the ISO")
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
    print args

    reader = iso9660.ISO9660(args.target)
    print reader.primary.pathTable

    if args.list:
        for el in reader.walk():
            print el.path