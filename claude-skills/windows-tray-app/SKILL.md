---
name: windows-tray-app
description: Scaffold a small Windows tray utility: icon with right-click menu, settings window, JSON settings in %APPDATA%, single instance, "start with Windows", one exe or installer, in C# (.NET 8 WinForms) or Python (pystray). Use when a user says "tray icon", "notification area", "runs in the background", "minimize to tray", or "autostart".
---

# Windows tray app

A tray app is a program with no main window: it shows an icon in the notification area (bottom right, next to the clock), does its job in the background and opens a small settings window on demand. Five things make it feel finished: one instance only (a named **mutex**, a system-wide lock, stops a second copy), settings that survive updates (`%APPDATA%\<App>\settings.json`, never next to the exe), autostart through the per-user **Run key** in the registry (no admin rights needed), a crisp icon that is removed on exit, and one file to hand out.

## Pattern

The C# version (.NET 8 WinForms). Layout: `FanTray/FanTray.csproj`, `Program.cs`, `TrayContext.cs`, `Settings.cs`, `SettingsForm.cs`, `app.ico` (multi-size 16/20/24/32/48 px; make one with any icon editor). Start with `dotnet new winforms -n FanTray`, delete `Form1*`, then:

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>            <!-- WinExe: no console window -->
    <TargetFramework>net8.0-windows</TargetFramework>
    <UseWindowsForms>true</UseWindowsForms>
    <Nullable>enable</Nullable><ImplicitUsings>enable</ImplicitUsings>
    <ApplicationIcon>app.ico</ApplicationIcon>
    <ApplicationHighDpiMode>PerMonitorV2</ApplicationHighDpiMode>
  </PropertyGroup>
  <ItemGroup><EmbeddedResource Include="app.ico" LogicalName="app.ico" /></ItemGroup>
</Project>
```

```csharp
// Program.cs
namespace FanTray;
static class Program
{
    public const string MutexName = "FanTray-7f3c2a";   // unique per app; Inno Setup uses it too
    [STAThread]
    static void Main()
    {
        using var mutex = new Mutex(true, MutexName, out bool first);
        if (!first) return;                               // already running
        ApplicationConfiguration.Initialize();            // applies the DPI mode from the csproj
        Application.Run(new TrayContext());               // a message loop with no main form
    }
}

// TrayContext.cs
namespace FanTray;
sealed class TrayContext : ApplicationContext
{
    readonly Icon _icon;
    readonly NotifyIcon _tray;
    readonly Settings _settings = Settings.Load();
    SettingsForm? _form;

    public TrayContext()
    {
        using var stream = typeof(Program).Assembly.GetManifestResourceStream("app.ico")!;
        _icon = new Icon(stream, SystemInformation.SmallIconSize);   // picks the size for this DPI
        var menu = new ContextMenuStrip();
        menu.Items.Add("Settings...", null, (_, _) => ShowSettings());
        menu.Items.Add(new ToolStripSeparator());
        menu.Items.Add("Exit", null, (_, _) => ExitThread());
        _tray = new NotifyIcon { Icon = _icon, Text = "FanTray", ContextMenuStrip = menu, Visible = true };
        _tray.MouseClick += (_, e) => { if (e.Button == MouseButtons.Left) ShowSettings(); };
    }

    void ShowSettings()
    {
        if (_form is { IsDisposed: false }) { _form.Activate(); return; }
        _form = new SettingsForm(_settings);
        _form.Show();
    }

    protected override void ExitThreadCore()
    {
        _tray.Visible = false;   // without this a ghost icon stays until the mouse passes over it
        _tray.Dispose();
        _icon.Dispose();
        base.ExitThreadCore();
    }
}

// Settings.cs
using System.Text.Json;
using Microsoft.Win32;
namespace FanTray;
public class Settings
{
    public string Port { get; set; } = "COM3";
    public int DefaultPercent { get; set; } = 40;
    public bool StartWithWindows { get; set; }

    static readonly string Dir = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData), "FanTray");
    static readonly string FilePath = Path.Combine(Dir, "settings.json");
    const string RunKey = @"Software\Microsoft\Windows\CurrentVersion\Run";

    public static Settings Load()
    {
        try { return JsonSerializer.Deserialize<Settings>(File.ReadAllText(FilePath)) ?? new(); }
        catch (Exception e) when (e is IOException or JsonException) { return new(); }   // first run or corrupt
    }

    public void Save()
    {
        Directory.CreateDirectory(Dir);
        File.WriteAllText(FilePath + ".tmp", JsonSerializer.Serialize(this, new JsonSerializerOptions { WriteIndented = true }));
        File.Move(FilePath + ".tmp", FilePath, overwrite: true);   // never leaves a half-written file
        using var key = Registry.CurrentUser.OpenSubKey(RunKey, writable: true)!;
        if (StartWithWindows) key.SetValue("FanTray", $"\"{Environment.ProcessPath}\"");
        else key.DeleteValue("FanTray", throwOnMissingValue: false);
    }
}

// SettingsForm.cs
namespace FanTray;
sealed class SettingsForm : Form
{
    public SettingsForm(Settings s)
    {
        Text = "FanTray settings"; FormBorderStyle = FormBorderStyle.FixedDialog; MaximizeBox = MinimizeBox = false;
        StartPosition = FormStartPosition.CenterScreen; AutoScaleMode = AutoScaleMode.Dpi;
        AutoSize = true; AutoSizeMode = AutoSizeMode.GrowAndShrink; Padding = new Padding(12);
        var port = new TextBox { Text = s.Port };
        var pct = new NumericUpDown { Minimum = 0, Maximum = 100, Value = Math.Clamp(s.DefaultPercent, 0, 100) };
        var auto = new CheckBox { Text = "Start with Windows", Checked = s.StartWithWindows, AutoSize = true };
        var ok = new Button { Text = "OK" };
        var cancel = new Button { Text = "Cancel" };
        var grid = new TableLayoutPanel { ColumnCount = 2, AutoSize = true };
        grid.Controls.Add(new Label { Text = "Serial port", AutoSize = true, Anchor = AnchorStyles.Left });
        grid.Controls.Add(port);
        grid.Controls.Add(new Label { Text = "Default fan %", AutoSize = true, Anchor = AnchorStyles.Left });
        grid.Controls.Add(pct);
        grid.Controls.Add(auto); grid.SetColumnSpan(auto, 2);
        grid.Controls.Add(ok); grid.Controls.Add(cancel);
        Controls.Add(grid);
        AcceptButton = ok; CancelButton = cancel;   // Enter and Esc
        ok.Click += (_, _) =>
        {
            s.Port = port.Text.Trim(); s.DefaultPercent = (int)pct.Value; s.StartWithWindows = auto.Checked;
            s.Save(); Close();
        };
        cancel.Click += (_, _) => Close();
    }
}
```

Build one self-contained exe (no .NET install needed on the target; large, 100 MB or more, `-p:EnableCompressionInSingleFile=true` shrinks it):

```bash
dotnet publish -c Release -r win-x64 --self-contained true -p:PublishSingleFile=true -p:IncludeNativeLibrariesForSelfExtract=true
# -> bin\Release\net8.0-windows\win-x64\publish\FanTray.exe
```

Use `--self-contained false` for a 200 KB exe that needs the ".NET 8 Desktop Runtime" installed.

## Variations

- **Installer (Inno Setup, free)**: save as `FanTray.iss`, compile with `iscc FanTray.iss`. `PrivilegesRequired=lowest` installs per user without a UAC prompt; `AppMutex` makes setup ask the user to close a running copy; the uninstall step removes the autostart value the app may have written.
  ```ini
  [Setup]
  AppName=FanTray
  AppVersion=1.0.0
  DefaultDirName={autopf}\FanTray
  PrivilegesRequired=lowest
  AppMutex=FanTray-7f3c2a
  OutputBaseFilename=FanTray-Setup-1.0.0
  [Files]
  Source: "bin\Release\net8.0-windows\win-x64\publish\FanTray.exe"; DestDir: "{app}"
  [Icons]
  Name: "{autoprograms}\FanTray"; Filename: "{app}\FanTray.exe"
  [UninstallRun]
  Filename: "reg.exe"; Parameters: "delete HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v FanTray /f"; Flags: runhidden; RunOnceId: "DelAutostart"
  [Run]
  Filename: "{app}\FanTray.exe"; Description: "Launch FanTray"; Flags: nowait postinstall skipifsilent
  ```
- **Python (pystray)**: `pip install pystray==0.19.5 Pillow==10.4.0 pyinstaller==6.10.0`. pystray runs its own message loop in a thread; tkinter must stay on the main thread, so menu clicks go through a queue.
  The complete script (settings, Run key, mutex, DPI, settings window) is `templates/tray.py` in this skill folder; copy it next to `app.ico`. Its shape:
  ```python
  self.icon = pystray.Icon(APP, icon_image(), APP, pystray.Menu(
      pystray.MenuItem("Settings...", lambda: self.jobs.put(self.settings), default=True),
      pystray.MenuItem("Exit", lambda: self.jobs.put(self.quit))))
  threading.Thread(target=self.icon.run, daemon=True).start()   # tray loop off the main thread
  self.root.after(100, self.poll); self.root.mainloop()          # poll() runs queued jobs on the tk thread
  ```
  Build: `pyinstaller --noconsole --onefile --name FanTray --icon app.ico --hidden-import pystray._win32 tray.py` (`--noconsole` hides the black window; the hidden import is needed because pystray picks its backend at runtime).

## Pitfalls

- **Ghost icons and leaks**: set `Visible = false` and dispose the `NotifyIcon` and `Icon` on exit; a crash still leaves a ghost, so catch exceptions in menu handlers.
- **Blurry icon or window**: ship a multi-size `.ico` and load it at `SystemInformation.SmallIconSize`; keep `PerMonitorV2` in the csproj. Do not set fixed pixel sizes on controls; use `AutoSize` and layout panels.
- **Defender or SmartScreen flags the exe**: unsigned single-file and PyInstaller exes often trip "Windows protected your PC" or a false-positive detection. Sign with a code-signing certificate, or publish the source and SHA-256 hash, and report false positives at Microsoft's submission portal. Do not tell users to turn Defender off.
- **Settings next to the exe**: Program Files is read-only for normal users and an update overwrites it. Always `%APPDATA%\<App>`.
- **Autostart path goes stale**: the Run value points at one exe path; rewrite it on every save, and let the installer remove it on uninstall.
- **Work on the UI thread**: serial I/O or polling in a menu handler freezes the tray menu. Use a background task (see `arduino-serial`).

## Related skills

- `arduino-serial`
- `readme-and-release`
