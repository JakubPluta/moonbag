import sys
import os
from sys import stdin, stdout

def reconfigure_sys():
    try:
        if os.name == "nt":
            sys.stdin.reconfigure(encoding="utf-8")
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as e:
        print(e, "\n")