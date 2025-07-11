# -*- coding: utf-8 -*-
import os
import time
import datetime
from ctypes import c_int, c_uint, c_ubyte, c_char_p, c_void_p, byref, WINFUNCTYPE, Structure, CDLL, POINTER
import ftd2xx

# Dynamically get the script's directory
LOCAL_DIR = os.path.dirname(os.path.abspath(__file__))
os.add_dll_directory(LOCAL_DIR)

FTD2XX_PATHS = [
    os.path.join(LOCAL_DIR, "ftd2xx.dll"),
    r"C:\Windows\System32\ftd2xx.dll"
]

VENDOR_ID = 0x0403
PRODUCT_ID = 0xF850
UUIRTDRV_CFG_LEDRX = 0x0001
UUIRTDRV_CFG_LEDTX = 0x0002
UUIRTDRV_CFG_LEGACYRX = 0x0004
INVALID_HANDLE_VALUE = -1

class UUINFO(Structure):
    _fields_ = (
        ('fwVersion', c_uint),
        ('protVersion', c_uint),
        ('fwDateDay', c_ubyte),
        ('fwDateMonth', c_ubyte),
        ('fwDateYear', c_ubyte),
    )

UUCALLBACKPROC = WINFUNCTYPE(c_int, c_char_p, c_void_p)

def log_to_file(message):
    with open("uuirtlog.txt", "a", encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now()}: {message}\n")

def check_ftd2xx_dll():
    for path in FTD2XX_PATHS:
        if os.path.exists(path):
            log_to_file(f"ftd2xx.dll found: {path}")
            return True
    log_to_file("ftd2xx.dll not found")
    return False

def find_usb_uirt_device():
    try:
        devices = ftd2xx.listDevices()
        for i, serial in enumerate(devices):
            dev = ftd2xx.open(i)
            info = dev.getDeviceInfo()
            dev.close()
            if info['id'] == ((VENDOR_ID << 16) | PRODUCT_ID):
                log_to_file(f"Detected device: serial={serial}")
                return f"USB-UIRT-{i+1}" if i > 0 else "USB-UIRT"
        log_to_file("USB-UIRT device not found")
        return None
    except Exception as e:
        log_to_file(f"Device search error: {e}")
        return None

class USB_UIRT:
    def __init__(self):
        self.dll = None
        self.hDrvHandle = None
        self.last_pronto_code = None  # Store last received Pronto code

    def initialize(self, led_rx=True, led_tx=True, legacy_rx=True):
        # Initialize log file (overwrite)
        with open("uuirtlog.txt", "w", encoding='utf-8') as f:
            f.write(f"{datetime.datetime.now()}: Log file initialized\n")

        device_str = find_usb_uirt_device()
        if not device_str:
            raise ValueError("USB-UIRT device not found")

        if not check_ftd2xx_dll():
            raise ValueError("ftd2xx.dll not found")

        try:
            self.dll = CDLL('uuirtdrv')
            log_to_file("uuirtdrv.dll loaded")
        except Exception as e:
            log_to_file(f"uuirtdrv.dll load error: {e}")
            raise

        self.dll.UUIRTOpen.restype = c_void_p
        self.dll.UUIRTGetUUIRTInfo.argtypes = [c_void_p, POINTER(UUINFO)]
        self.dll.UUIRTSetUUIRTConfig.argtypes = [c_void_p, c_uint]
        self.dll.UUIRTSetReceiveCallback.argtypes = [c_void_p, UUCALLBACKPROC, c_void_p]
        self.dll.UUIRTClose.argtypes = [c_void_p]

        self.hDrvHandle = self.dll.UUIRTOpen()
        if self.hDrvHandle in (INVALID_HANDLE_VALUE, 0xFFFFFFFFFFFFFFFF):
            log_to_file("UUIRTOpen error")
            raise ValueError("Device initialization failed")

        puuInfo = UUINFO()
        if not self.dll.UUIRTGetUUIRTInfo(self.hDrvHandle, byref(puuInfo)):
            log_to_file("Failed to get USB-UIRT info")
            raise ValueError

        firmware_version = f"{puuInfo.fwVersion >> 8}.{puuInfo.fwVersion & 0xFF}"
        log_to_file(f"Firmware version: {firmware_version}")

        config_value = 0
        if led_rx:
            config_value |= UUIRTDRV_CFG_LEDRX
        if led_tx:
            config_value |= UUIRTDRV_CFG_LEDTX
        if legacy_rx:
            config_value |= UUIRTDRV_CFG_LEGACYRX
        log_to_file(f"Config value: {hex(config_value)}")

        if not self.dll.UUIRTSetUUIRTConfig(self.hDrvHandle, c_uint(config_value)):
            log_to_file("USB-UIRT configuration failed")
            raise ValueError

        self.receive_proc = UUCALLBACKPROC(self.receive_callback)
        if not self.dll.UUIRTSetReceiveCallback(self.hDrvHandle, self.receive_proc, None):
            log_to_file("Failed to set receive callback")
            raise ValueError

        log_to_file("USB-UIRT initialized successfully")
        return True

    def receive_callback(self, ir_event_str, user_data):
        try:
            if ir_event_str:
                pronto_code = ir_event_str.decode('utf-8').strip()
                # Ignore duplicate codes
                if pronto_code == self.last_pronto_code:
                    return 0
                self.last_pronto_code = pronto_code

                print(f"{datetime.datetime.now()}: Pronto code: {pronto_code}")
            return 0
        except Exception as e:
            log_to_file(f"Receive callback error: {e}")
            return 0

    def close(self):
        if self.dll and self.hDrvHandle is not None and self.hDrvHandle != INVALID_HANDLE_VALUE:
            if not self.dll.UUIRTSetReceiveCallback(self.hDrvHandle, UUCALLBACKPROC(lambda x, y: 0), None):
                log_to_file("Failed to unset receive callback")
            else:
                log_to_file("Receive callback unset")
            if not self.dll.UUIRTClose(self.hDrvHandle):
                log_to_file("Failed to close USB-UIRT")
            log_to_file("USB-UIRT closed")
            self.dll = None
            self.hDrvHandle = None

def main():
    usb_uirt = USB_UIRT()
    try:
        usb_uirt.initialize(led_rx=True, led_tx=True, legacy_rx=True)
        print(f"{datetime.datetime.now()}: Waiting for IR signals...")
        while True:
            time.sleep(0.1)
    except Exception as e:
        log_to_file(f"Error: {e}")
        print(f"{datetime.datetime.now()}: Error: {e}")
    finally:
        usb_uirt.close()

if __name__ == "__main__":
    main()