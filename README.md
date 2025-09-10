# USB-UIRT IR Receiver(64bit)

A Python script to capture IR signals using the USB-UIRT device and display Pronto codes. Supports any IR protocol (SONY SIRC, NEC, RC5, etc.) compatible with USB-UIRT.

## Features
- Initializes USB-UIRT with LED indicators and legacy receive mode.
- Outputs unique Pronto codes to the console, ignoring duplicates.
- Logs initialization and errors to `uuirtlog.txt`.

## Requirements
- Python 3.13+
- USB-UIRT device (VID=0x0403, PID=0xF850)
- `uuirtdrv.dll` and `ftd2xx.dll` (place in the script directory)
- FTDI D2XX drivers ([download](https://ftdichip.com/drivers/d2xx-drivers/))
- Windows 10/11 (other OS untested)

## Setup
1. Install FTDI D2XX drivers from [ftdichip.com](https://ftdichip.com/drivers/d2xx-drivers/).
2. Obtain `uuirtdrv.dll`:
   - Download SageTV Windows binary(SageTVSetupx64_xxxx.exe) from [OpenSageTV releases](https://github.com/OpenSageTV/sagetv-windows/releases)
   - Extract the installer and locate the DLL at `C:\Program Files\SageTV\redist\usbuirt\amd64\uuirtdrv.dll`
   - Copy this file to your script directory
     
   OR Obtain `uuirtdrv.dll` from usbuirt.com:
   - Go to the [Support](http://www.usbuirt.com/support.htm) and download the driver
   - Extract the installer and locate the DLL at `C:\Program Files\SageTV\redist\usbuirt\amd64\uuirtdrv.dll`
   - Copy this file to your script directory
3. Place `ftd2xx.dll` in the same directory as `usb_receiver.py`.
4. Install Python dependencies:
   ```bash
   pip install pyftd2xx
   ```

## Usage

- Run the script:
   ```bash
   python usb_receiver.py
   ```
- Press buttons on your IR remote to capture Pronto codes.
- Check uuirtlog.txt for initialization and error logs.

## Example Output
   ```bash
   2025-07-11 09:56:53.365399: Waiting for IR signals...
   2025-07-11 09:56:55.803926: Pronto code: 19000220A0E2
   2025-07-11 09:56:58.203791: Pronto code: 190002A0A2E2
   2025-07-11 09:56:59.372199: Pronto code: 1900022088EA
   ```

## Notes
- **Pronto Code Format**: Codes (e.g., `19000220A0E2`) may be USB-UIRT-specific. Refer to [USB-UIRT documentation](http://www.usbuirt.com/) for details.

## License
MIT License

## Contributing

Issues and pull requests are welcome! For bug reports or feature requests, include logs from `uuirtlog.txt` and details of your IR remote.
