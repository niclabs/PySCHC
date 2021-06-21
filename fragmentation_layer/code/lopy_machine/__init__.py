"""
machine: Package implementing PyCom machine modules (
https://docs.pycom.io/firmwareapi/pycom/machine/
). Not to be used in production
"""

if sys.implementation.name != "mycropython":
    from lopy_machine.timer import Timer
