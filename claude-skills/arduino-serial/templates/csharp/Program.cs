using var link = new FanLink(args.FirstOrDefault());         // "COM5", or no argument to auto-detect
link.Start();
_ = Task.Run(async () => { while (true) { link.Send("GET"); await Task.Delay(1000); } });
_ = Task.Run(async () =>
{
    while (true)
    {
        while (link.Lines.TryDequeue(out var line)) Console.WriteLine("< " + line);   // your UI would parse RPM here
        await Task.Delay(50);
    }
});
Console.WriteLine("Type SET 0 60 or GET; empty line quits.");
string? typed;
while (!string.IsNullOrWhiteSpace(typed = Console.ReadLine()))
    if (!link.Send(typed)) Console.WriteLine("not connected");
