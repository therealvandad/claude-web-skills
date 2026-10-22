---
name: arduino-serial
description: Talk to an Arduino or other microcontroller over USB serial from a Windows desktop app: a line-based ASCII protocol (PING/PONG, VER, SET, GET), a non-blocking sketch, C# SerialPort and Python pyserial clients with port discovery, background reader and reconnect. Use for "COM port", "SerialPort", "pyserial", "read or set fan speed", "test without hardware".
---

# Arduino serial

A serial link is just a stream of bytes, so the first job is agreeing on where a message ends. This skill uses **one command per line, plain ASCII, ending in `\n`**: you can type it in the Arduino IDE Serial Monitor, log it, and test it with a fake device. The running example is a PC app that reads and sets fan speeds. The complete runnable files are in `templates/` (`fanctl/fanctl.ino`, `csharp/`, `fanlink.py`, `fake_device.py`); the key parts are below.

## Pattern

Protocol v1, 115200 baud. Verbs are upper case, fields separated by single spaces, lines at most 39 characters.

| PC sends | Device answers | Meaning |
|---|---|---|
| `PING` | `PONG` | is anyone there, and is it ours |
| `VER` | `VER 1` | protocol version; refuse a different number |
| `SET <fan> <percent>` | `OK` or `ERR args` / `ERR range` | fan 0, 1... to 0-100 % |
| `GET` | `RPM <fan> <value>`, one line per fan | read speeds |
| any bad line | `ERR unknown` / `ERR long` | never silence, never a crash |

`RPM` lines may also be pushed unprompted. The host does not pair requests with replies: it reads lines as they come and updates the latest value per fan. The device answers with `println`, so lines end in `\r\n`; the host trims.

**Arduino side** (`templates/fanctl/fanctl.ino`). Non-blocking means `loop()` takes only the bytes that already arrived and returns, so the 64-byte receive buffer never overflows. No `delay()`, no `String`.

```cpp
void handle(char* line) {
  char* verb = strtok(line, " ");
  if (!verb) return;                            // blank line: ignore
  if (!strcmp(verb, "PING")) Serial.println(F("PONG"));
  else if (!strcmp(verb, "VER")) { Serial.print(F("VER ")); Serial.println(PROTOCOL); }
  else if (!strcmp(verb, "GET")) {
    for (uint8_t f = 0; f < FANS; f++) { Serial.print(F("RPM ")); Serial.print(f); Serial.print(' '); Serial.println(rpmOf(f)); }
  } else if (!strcmp(verb, "SET")) {
    long fan, pct;
    if (!toInt(strtok(NULL, " "), fan) || !toInt(strtok(NULL, " "), pct) || strtok(NULL, " ")) Serial.println(F("ERR args"));
    else if (fan < 0 || fan >= FANS || pct < 0 || pct > 100) Serial.println(F("ERR range"));
    else { percent[fan] = pct; apply(fan); Serial.println(F("OK")); }
  } else Serial.println(F("ERR unknown"));
}
...
void loop() {
  while (Serial.available() > 0) {              // take only what has already arrived
    char c = Serial.read();
    if (c == '\r') continue;                    // accept \r\n as well as \n
    if (c != '\n') {
      if (len < sizeof buf - 1) buf[len++] = c; else tooLong = true;
      continue;
    }
    buf[len] = 0;
    if (tooLong) Serial.println(F("ERR long")); else handle(buf);
    len = 0;
    tooLong = false;
  }
  // other non-blocking work goes here (count tach pulses, update a display); never delay()
}
```

**C# side** (`templates/csharp/FanLink.cs`, .NET 8, `dotnet add package System.IO.Ports --version 8.0.0`). A `SerialPort` is **opened by name** (`COM5`); `GetPortNames()` lists the names. One long-running thread owns the port: it connects, blocks in `ReadLine`, and pushes each line into a `ConcurrentQueue` (a thread-safe queue) that the UI drains. When the cable is pulled it falls out of the loop, disposes the port and starts again.

```csharp
    void Run()                                                // background thread: connect, read, reconnect
    {
        var ct = _cts.Token;
        while (!ct.IsCancellationRequested)
        {
            var port = Connect();
            if (port == null) { ct.WaitHandle.WaitOne(1000); continue; }
            lock (_gate) _port = port;
            Lines.Enqueue("# connected " + port.PortName);
            try
            {
                while (!ct.IsCancellationRequested)
                {
                    try { Lines.Enqueue(port.ReadLine().Trim()); }          // Trim() drops the \r of println
                    catch (TimeoutException)                                // quiet line: check the cable instead
                    {
                        if (!SerialPort.GetPortNames().Contains(port.PortName, StringComparer.OrdinalIgnoreCase))
                            throw new IOException("port vanished");
                    }
                }
            }
            catch (Exception e) when (e is IOException or InvalidOperationException or UnauthorizedAccessException) { }
            lock (_gate) _port = null;
            try { port.Dispose(); } catch { }                // Dispose can throw on a dead USB device
            Lines.Enqueue("# disconnected");
        }
    }
...
    SerialPort? Connect()
    {
        var names = _preferred != null ? new[] { _preferred } : SerialPort.GetPortNames();
        foreach (var name in names)
        {
            SerialPort? p = null;
            try
            {
                p = new SerialPort(name, Baud) { NewLine = "\n", ReadTimeout = 500, WriteTimeout = 500, DtrEnable = true };
                p.Open();                                    // DTR going high resets most Arduinos...
                Thread.Sleep(2000);                          // ...so wait for the bootloader to start the sketch
                p.DiscardInBuffer();
                if (Ask(p, "PING") == "PONG" && Ask(p, "VER") == "VER 1") return p;
            }
            catch (Exception e) when (e is IOException or UnauthorizedAccessException or InvalidOperationException
                                          or TimeoutException or ArgumentException) { }   // busy, silent or not ours
            try { p?.Dispose(); } catch { }
        }
        return null;
    }
```

`Ask` is `Write(cmd + "\n")` then `ReadLine().Trim()`. `DtrEnable` is the DTR line (data terminal ready): opening a port raises it, which **auto-resets** most Arduinos, hence the 2 s wait.

**Python side** (`templates/fanlink.py`, `pip install pyserial==3.5`). `list_ports.comports()` gives name, description and USB vendor/product ids; `find_device` tries a saved port first, else each port with `probe`.

```python
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
...
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
```

### Test without hardware

- `python templates/fake_device.py --selftest` checks the protocol logic and prints `OK`.
- **Python host**: terminal A `python templates/fake_device.py --tcp 7777 --drop-after 10`, terminal B `python templates/fanlink.py socket://127.0.0.1:7777`. You see `# connected`, `RPM` lines, `# disconnected` after 10 s and a reconnect. pyserial opens `socket://` URLs like a port.
- **C# host**: install the free **com0com** virtual null-modem driver (it asks for admin rights), create a pair such as COM10 and COM11, run `python templates/fake_device.py --serial COM11`, then `dotnet run -- COM10`. Without a driver, put `Write`/`ReadLine` behind a small interface and unit-test `FanLink` against a fake.
- **Real board, no code**: Arduino IDE Serial Monitor, 115200 baud, line ending "Newline", type `PING`.

## Variations

- **WPF or WinForms**: never touch controls from the reader thread. Drain the queue on the UI thread:
  `var t = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(50) }; t.Tick += (_, _) => { while (_link.Lines.TryDequeue(out var l)) Handle(l); }; t.Start();` (tkinter: `root.after(50, drain)`).
- **Heartbeat**: send `PING` every 2 s and treat 3 s without `PONG` as dead; this also catches a hung sketch.
- **Noisy cable or long runs**: append a checksum (`SET 0 60*3F`, XOR of the text) before moving to a binary format.
- **Other boards**: Pico and ESP32 speak the same protocol; ESP32 boards may reset on RTS as well as DTR.

## Pitfalls

- **Auto-reset**: opening the port reboots the board for about 2 s; talk before that and the first commands are lost. A 10 uF capacitor from RESET to GND disables it (remove it to upload).
- **`DataReceived` is a trap**: it fires on a thread-pool thread with partial lines. Use your own thread and `ReadLine`.
- **Port busy**: `UnauthorizedAccessException` or "Access denied" means another program (Serial Monitor, another copy of your app) holds it. Only one process can open a port.
- **Unplug is quiet**: a read may just keep timing out, so check `GetPortNames()`; pyserial raises `SerialException`. `Dispose` can throw too: wrap it.
- **COM numbers move** between boards and USB sockets. Save the choice, fall back to discovery, and never send text to ports you did not pick; it may be a modem or GPS.
- **Python**: install `pyserial`, not `serial` (a different package). Pin it.
- **Fans**: 4-pin PC fans want 25 kHz PWM (see the `TCCR1B` line in the sketch), 12 V from the fan supply, ground shared with the Arduino; never power a fan from a pin.

## Related skills

- `windows-tray-app` for the tray icon, port setting and autostart around this link
- `readme-and-release` for documenting the protocol and shipping the app
