import imp
import os

this_dir = os.path.abspath(os.path.dirname(__file__))
name = "iso9660"

actual_module = imp.find_module(name, [os.path.join(this_dir, "src")])
assert actual_module
imp.load_module(name, *actual_module)
from iso9660 import *