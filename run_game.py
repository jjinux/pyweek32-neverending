#!/usr/bin/env python3.9

import sys

MIN_PYTHON_VERSION = (3, 9)
if sys.version_info[:2] < MIN_PYTHON_VERSION:
    sys.exit("This game requires Python %s" % ".".join(map(str, MIN_PYTHON_VERSION)))

from pw32n.game import main

main()
