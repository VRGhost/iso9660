import argparse

# from .
import iso9660

def get_parser():
    parser = argparse.ArgumentParser(description='Read ISO (ISO-9660 encoded) disk images.')
    parser.add_argument("target", help="Target ISO file")
    return parser

if __name__ == "__main__":
    parser = get_parser()
    print parser.parse_args()