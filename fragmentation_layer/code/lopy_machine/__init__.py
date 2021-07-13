"""
machine: Package implementing PyCom machine modules (
https://docs.pycom.io/firmwareapi/pycom/machine/
). Not to be used in production
"""

import sys

if sys.implementation.name == "micropython":
    from machine import Timer
else:
    from lopy_machine.timer import Timer
