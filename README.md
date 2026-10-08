# USB-UIRT Pronto Hex Learner (64-bit)

A Python script for learning infrared signals with USB-UIRT and saving Pronto Hex codes.

## Features

- Uses the 64-bit USB-UIRT API.
- Displays learning progress, signal quality, and carrier frequency.
- Supports infrared protocols compatible with USB-UIRT, including SONY SIRC, NEC, and RC5.
- Saves the learned Pronto Hex code to `learned_pronto.txt`.
- Requires no additional Python packages.

## Requirements

- Python 3.13 or later, 64-bit
- Windows 10 or Windows 11
- USB-UIRT device (`VID_0403`, `PID_F850`)
- FTDI D2XX driver or the signed USB-UIRT driver package
- 64-bit `uuirtdrv.dll`

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

Create an installer layout:

```bash
./SageTVSetupx64_x.x.x.exe /layout "$(cygpath -w "$PWD/SageTV_layout")" /quiet /norestart
```

Locate the DLL at:

```text
SageTV_layout\redist\usbuirt\amd64\uuirtdrv.dll
```

Copy `uuirtdrv.dll` to the script directory.

The USB-UIRT software or API package may also be available from [USB-UIRT Support](http://www.usbuirt.com/support.htm).

## Directory Layout

```text
py-usb-uirt_receiver/
├── README.md
├── usb_uirt_learn_pronto.py
└── uuirtdrv.dll
```

## Usage

```bash
python -u usb_uirt_learn_pronto.py
```

Aim the remote control at the USB-UIRT from close range. Press and hold one button until learning reaches 100 percent. Do not release and press the button repeatedly during learning.

Example output:

```text
CALLBACK Progress=100%  Quality=97%  Carrier=39887 Hz

Pronto Hex:
0000 0067 0000 000D 0060 0019 0030 0019 0018 0019 0030 0019 0018 0019 0030 0019 0018 0018 0018 0018 0031 0019 0018 0019 0018 0019 0018 0019 0018 040D
```

The learned code is saved to:

```text
learned_pronto.txt
```

## License

MIT License
