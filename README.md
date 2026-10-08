# USB-UIRT Pronto Hex Tools (64-bit)

Python scripts for learning infrared signals with USB-UIRT and transmitting saved Pronto Hex codes.

## Features

- Learns Pronto Hex codes from an infrared remote control.
- Displays learning progress, signal quality, and carrier frequency.
- Saves learned codes to a text file.
- Transmits long Pronto Hex codes directly from a text file.
- Uses the 64-bit USB-UIRT API without `uutx.exe`.
- Requires no additional Python packages.

## Requirements

- Python 3.13 or later, 64-bit
- Windows 10 or Windows 11
- USB-UIRT device (`VID_0403`, `PID_F850`)
- FTDI D2XX driver or the signed USB-UIRT driver package
- 64-bit `uuirtdrv.dll`

Python and `uuirtdrv.dll` must have the same bitness.

## Setup

### 1. Install the device driver

Install either of the following drivers:

- [FTDI D2XX Drivers](https://ftdichip.com/drivers/d2xx-drivers/)
- [Win7_Win8_Vista_v20601_signed.zip](http://www.usbuirt.com/Win7_Win8_Vista_v20601_signed.zip)

When using `Win7_Win8_Vista_v20601_signed.zip`, extract the package and install `ftdibus.inf`.

```cmd
pnputil /add-driver "C:\path\to\Win7_Win8_Vista_v20601_signed\ftdibus.inf" /install
```

Alternatively, update the USB-UIRT driver from Device Manager and select the extracted `Win7_Win8_Vista_v20601_signed` directory.

Disconnect and reconnect the USB-UIRT device after installation.

### 2. Obtain the 64-bit `uuirtdrv.dll`

Download a SageTV Windows x64 installer from [OpenSageTV Windows Releases](https://github.com/OpenSageTV/sagetv-windows/releases).

#### Cygwin or Git Bash

```bash
./SageTVSetupx64_x.x.x.exe /layout "$(cygpath -w "$PWD/SageTV_layout")" /quiet /norestart
```

#### Windows Command Prompt

```cmd
SageTVSetupx64_x.x.x.exe /layout "%CD%\SageTV_layout" /quiet /norestart
```

#### Windows PowerShell

```powershell
.\SageTVSetupx64_x.x.x.exe /layout "$PWD\SageTV_layout" /quiet /norestart
```

Locate the DLL at:

```text
SageTV_layout\redist\usbuirt\amd64\uuirtdrv.dll
```

Copy `uuirtdrv.dll` to the same directory as the Python scripts.

The USB-UIRT software or API package may also be available from [USB-UIRT Support](http://www.usbuirt.com/support.htm).

## Directory Layout

```text
py-usb-uirt_receiver/
├── README.md
├── usb_uirt_learn_pronto.py
├── usb_uirt_transmit.py
└── uuirtdrv.dll
```

## Learn a Pronto Hex Code

```bash
python -u usb_uirt_learn_pronto.py
```

Aim the remote control at the USB-UIRT from close range. Press and hold one button until learning reaches 100 percent. Do not release and press the button repeatedly during learning.

The learned code is displayed in the console and saved to `learned_pronto.txt`.

## Transmit a Pronto Hex Code

By default, the script reads `learned_pronto.txt` from the current directory:

```bash
python -u usb_uirt_transmit.py
```

Specify a file only when transmitting a different command:

```bash
python -u usb_uirt_transmit.py command_1.txt
```

A file in another directory can also be specified:

```bash
python -u usb_uirt_transmit.py "C:\path\to\commands\command_2.txt"
```

Set the repeat count when required:

```bash
python -u usb_uirt_transmit.py command_3.txt --repeat 5
```

Each input file must contain one raw Pronto Hex code beginning with `0000`. Long codes may span multiple lines.

## License

MIT License
