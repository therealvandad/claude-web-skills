"""Pretend Arduino speaking fanctl protocol v1, so the desktop side can be tested without hardware.

  python fake_device.py --selftest          # check the protocol logic, prints OK
  python fake_device.py --tcp 7777          # host connects with serial_for_url("socket://127.0.0.1:7777")
  python fake_device.py --tcp 7777 --drop-after 8   # hang up every 8 s, to test reconnect
  python fake_device.py --serial COM11      # one end of a com0com virtual pair (needs pyserial==3.5)
"""
import argparse
import socket
import time


class FakeFans:
    """The protocol brain: one line in, a list of reply lines out. No I/O, so it is easy to test."""

    def __init__(self, fans=2):
        self.percent = [40] * fans

    def handle(self, line):
        parts = line.strip().split()
        if not parts:
            return []                                    # blank line: ignore, like the sketch
        verb, args = parts[0], parts[1:]
        if verb == "PING":
            return ["PONG"]
        if verb == "VER":
            return ["VER 1"]
        if verb == "GET":
            return [f"RPM {i} {p * 30}" for i, p in enumerate(self.percent)]   # same stub as the sketch
        if verb == "SET":
            try:
                if len(args) != 2:
                    raise ValueError
                fan, pct = int(args[0]), int(args[1])
            except ValueError:
                return ["ERR args"]
            if not (0 <= fan < len(self.percent) and 0 <= pct <= 100):
                return ["ERR range"]
            self.percent[fan] = pct
            return ["OK"]
        return ["ERR unknown"]


def pump(read, write, device, deadline=None):
    """Read bytes, split on newline, answer each line. read() returns None for "nothing yet", b"" for closed."""
    buf = b""
    while deadline is None or time.time() < deadline:
        chunk = read(256)
        if chunk is None:
            continue
        if not chunk:
            return
        buf += chunk
        while b"\n" in buf:
            line, buf = buf.split(b"\n", 1)
            for reply in device.handle(line.decode("ascii", "replace")):
                write((reply + "\r\n").encode("ascii"))     # real Arduino println() sends \r\n


def serve_tcp(port, drop_after):
    device = FakeFans()
    with socket.create_server(("127.0.0.1", port)) as srv:
        print(f"fake device on socket://127.0.0.1:{port}", flush=True)
        while True:
            conn, _ = srv.accept()
            print("host connected", flush=True)
            conn.settimeout(0.2)
            end = time.time() + drop_after if drop_after else None

            def read(n):
                while True:
                    try:
                        return conn.recv(n)
                    except socket.timeout:
                        if end and time.time() > end:
                            return b""

            with conn:
                try:
                    pump(read, conn.sendall, device, end)
                except OSError:
                    pass
            print("host gone", flush=True)


def selftest():
    d = FakeFans()
    assert d.handle("PING") == ["PONG"] and d.handle("VER") == ["VER 1"]
    assert d.handle("SET 1 60") == ["OK"] and d.handle("GET") == ["RPM 0 1200", "RPM 1 1800"]
    assert d.handle("SET 5 10") == ["ERR range"] and d.handle("SET 0 101") == ["ERR range"]
    assert d.handle("SET x 10") == ["ERR args"] and d.handle("SET 0") == ["ERR args"]
    assert d.handle("") == [] and d.handle("DANCE") == ["ERR unknown"]
    print("OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tcp", type=int, metavar="PORT")
    ap.add_argument("--serial", metavar="COMx")
    ap.add_argument("--drop-after", type=float, default=0, metavar="SECONDS")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    elif a.tcp:
        serve_tcp(a.tcp, a.drop_after)
    elif a.serial:
        import serial                                        # pip install pyserial==3.5
        with serial.Serial(a.serial, 115200, timeout=0.5) as s:
            print(f"fake device on {a.serial}", flush=True)
            dev = FakeFans()
            while True:
                pump(lambda n: s.read(n) or None, s.write, dev)   # None = timed out, keep going
    else:
        ap.print_help()
