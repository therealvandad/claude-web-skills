"""Desktop side of fanctl protocol v1 in Python: find the board, read in a thread, reconnect on unplug.

  pip install pyserial==3.5
  python fanlink.py                              # auto-detect the board
  python fanlink.py COM5                         # use one port
  python fanlink.py socket://127.0.0.1:7777      # talk to fake_device.py --tcp 7777, no hardware
Type SET 0 60 or GET and press Enter; an empty line quits.
"""
import queue
import sys
import threading
import time

import serial                                   # pyserial
from serial.tools import list_ports

BAUD, PROTOCOL = 115200, "VER 1"


def ask(ser, command):
    """Send one line, return the next reply line ('' if the device stayed silent)."""
    ser.write(command.encode("ascii") + b"\n")
    return ser.readline().decode("ascii", "replace").strip()


def probe(name):
    """Open a port and return it if a fanctl device answers; else close it and return None."""
    try:
        ser = serial.Serial(name, BAUD, timeout=0.5, write_timeout=0.5)   # opening sets DTR: most Arduinos reset
        time.sleep(2.0)                                                   # wait for bootloader -> sketch
        ser.reset_input_buffer()
        if ask(ser, "PING") == "PONG" and ask(ser, "VER") == PROTOCOL:
            return ser
        ser.close()
    except (serial.SerialException, OSError):                             # busy, vanished, not a serial device
        pass
    return None


def find_device(preferred=None):
    if preferred:                                                         # a saved choice: never poke other ports
        return probe(preferred)
    for info in list_ports.comports():                                    # .device 'COM5', .description, .vid/.pid
        ser = probe(info.device)
        if ser:
            return ser
    return None


class FanLink:
    def __init__(self, port=None):
        self.port = port                         # None = auto-detect, 'COM5', or a URL such as socket://host:7777
        self.lines = queue.Queue()               # replies; lines starting with '#' are status messages
        self._ser, self._lock, self._stop = None, threading.Lock(), threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def start(self):
        self._thread.start()

    def stop(self):
        self._stop.set()
        self._thread.join(timeout=3)

    def send(self, command):
        with self._lock:
            if self._ser is None:
                return False
            try:
                self._ser.write(command.encode("ascii") + b"\n")
                return True
            except (serial.SerialException, OSError):
                return False

    def _connect(self):
        try:
            if self.port and "://" in self.port:                          # test URL: no DTR reset, no probing
                return serial.serial_for_url(self.port, BAUD, timeout=0.5)
            return find_device(self.port)
        except (serial.SerialException, OSError):
            return None

    def _run(self):
        while not self._stop.is_set():
            ser = self._connect()
            if ser is None:
                self._stop.wait(1.0)                                      # retry once a second
                continue
            with self._lock:
                self._ser = ser
            self.lines.put("# connected " + str(ser.port))
            buf = b""
            try:
                while not self._stop.is_set():
                    buf += ser.read(ser.in_waiting or 1)                  # waits up to the timeout for a byte
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        self.lines.put(line.decode("ascii", "replace").strip())
            except (serial.SerialException, OSError, TypeError):          # unplugged: reads raise
                pass
            with self._lock:
                self._ser = None
            try:
                ser.close()
            except (serial.SerialException, OSError):
                pass
            self.lines.put("# disconnected")


if __name__ == "__main__":
    link = FanLink(sys.argv[1] if len(sys.argv) > 1 else None)
    link.start()

    def printer():                                    # stand-in for your UI: drain the queue
        while True:
            try:
                print("<", link.lines.get(timeout=0.2))
            except queue.Empty:
                pass

    def poller():                                     # ask for RPM once a second
        while True:
            link.send("GET")
            time.sleep(1)

    threading.Thread(target=printer, daemon=True).start()
    threading.Thread(target=poller, daemon=True).start()
    for typed in iter(input, ""):
        if not link.send(typed):
            print("not connected")
    link.stop()
