import sys
import argparse
from .api import init_db

parser = argparse.ArgumentParser()
parser.add_argument("command")


if len(sys.argv) == 1:
    print("help")
    print("init_db")
    exit()


cmd = parser.parse_args().command


if cmd == "help":
    print("help")
    print("init_db")
elif cmd == "init_db":
    init_db()
else:
    raise Exception("Unknown command")
