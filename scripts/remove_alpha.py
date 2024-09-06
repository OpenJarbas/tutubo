"""
on merge to master -> declare stable (remove alpha)
"""
import fileinput
from os.path import join, dirname

# TODO - read from env var to allow script to be reused
VERSION_FILE = f"{dirname(dirname(__file__))}/tutubo/version.py"

alpha_var_name = "VERSION_ALPHA"

for line in fileinput.input(VERSION_FILE, inplace=True):
    if line.startswith(alpha_var_name):
        print(f"{alpha_var_name} = 0")
    else:
        print(line.rstrip('\n'))
