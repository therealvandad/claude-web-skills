using System.Collections.Concurrent;
using System.IO.Ports;

public sealed class FanLink : IDisposable
{
    const int Baud = 115200;
    public ConcurrentQueue<string> Lines { get; } = new();   // device lines; "# ..." lines are status messages
    readonly CancellationTokenSource _cts = new();
    readonly object _gate = new();
    readonly string? _preferred;                              // null = probe every COM port
    SerialPort? _port;

    public FanLink(string? preferredPort = null) => _preferred = preferredPort;
    public void Start() => Task.Factory.StartNew(Run, TaskCreationOptions.LongRunning);
    public void Dispose() => _cts.Cancel();                   // the reader thread closes the port itself

    public bool Send(string command)
    {
        lock (_gate)
        {
            if (_port is not { IsOpen: true }) return false;
            try { _port.Write(command + "\n"); return true; }
            catch (Exception e) when (e is IOException or InvalidOperationException or UnauthorizedAccessException or TimeoutException)
            { return false; }                                 // unplugged mid-write: Run() notices and reconnects
        }
    }

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

    static string Ask(SerialPort p, string command)
    {
        p.Write(command + "\n");
        return p.ReadLine().Trim();                          // TimeoutException if the device stays silent
    }
}
