#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3
import argparse
import sys

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('kindle', help='Path to kindle db file (usually vocab.db)', default='vocab.db')
    args = parser.parse_args()
    
    conn = sqlite3.connect(args.kindle)
    conn.execute("delete from WORDS;")
    conn.execute("delete from LOOKUPS;")
    conn.commit()
    conn.close()

    sys.exit(0)