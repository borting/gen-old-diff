#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright 2020, Borting Chen <bortingchen@gmail.com>
#
# This file is licensed under the GPL v2.
#

import sys
import window
import cmdline

def parseConfig():
    pass

if __name__ == "__main__":
    if sys.stdin.isatty():
        cmdline.main(sys.argv)
    else:
        window.main()
