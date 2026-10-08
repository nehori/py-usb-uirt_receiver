# coding: utf-8
"""Learn an IR signal with USB-UIRT and save it as Pronto Hex."""

import ctypes
import sys
import threading
import time
from pathlib import Path

DLL_NAME = "uuirtdrv.dll"
OUTPUT_NAME = "learned_pronto.txt"
IRFMT_PRONTO = 0x0010
BUFFER_SIZE = 65536
BOOL = ctypes.c_int


class UUINFO(ctypes.Structure):
    _fields_ = [
        ("fwVersion", ctypes.c_uint),
        ("protVersion", ctypes.c_uint),
        ("fwDateDay", ctypes.c_ubyte),
        ("fwDateMonth", ctypes.c_ubyte),
        ("fwDateYear", ctypes.c_ubyte),
    ]


def main() -> int:
    base_dir = Path(__file__).resolve().parent
    dll_path = base_dir / DLL_NAME
    output_path = base_dir / OUTPUT_NAME

    print(f"DLL: {dll_path}", flush=True)
    print(f"Python: {sys.version}", flush=True)
    print(f"Python bitness: {ctypes.sizeof(ctypes.c_void_p) * 8}-bit", flush=True)
    print("Learn mode: pronto (0x0010)", flush=True)

    if not dll_path.exists():
        print(f"ERROR: DLL not found: {dll_path}", flush=True)
        return 1

    driver = ctypes.WinDLL(str(dll_path), use_last_error=True)

    LEARN_CALLBACK = ctypes.WINFUNCTYPE(
        None,
        ctypes.c_uint,
        ctypes.c_uint,
        ctypes.c_ulong,
        ctypes.c_void_p,
    )

    driver.UUIRTOpen.argtypes = []
    driver.UUIRTOpen.restype = ctypes.c_void_p
    driver.UUIRTClose.argtypes = [ctypes.c_void_p]
    driver.UUIRTClose.restype = BOOL
    driver.UUIRTGetDrvInfo.argtypes = [ctypes.POINTER(ctypes.c_uint)]
    driver.UUIRTGetDrvInfo.restype = BOOL
    driver.UUIRTGetUUIRTInfo.argtypes = [ctypes.c_void_p, ctypes.POINTER(UUINFO)]
    driver.UUIRTGetUUIRTInfo.restype = BOOL
    driver.UUIRTGetUUIRTConfig.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_uint32),
    ]
    driver.UUIRTGetUUIRTConfig.restype = BOOL
    driver.UUIRTLearnIR.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int,
        ctypes.POINTER(ctypes.c_char),
        LEARN_CALLBACK,
        ctypes.c_void_p,
        ctypes.POINTER(BOOL),
        ctypes.c_uint,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    driver.UUIRTLearnIR.restype = BOOL

    version = ctypes.c_uint()
    if driver.UUIRTGetDrvInfo(ctypes.byref(version)):
        print(f"Driver API version: 0x{version.value:04X}", flush=True)

    invalid_handle = ctypes.c_void_p(-1).value
    handle = driver.UUIRTOpen()
    if not handle or handle == invalid_handle:
        print(f"ERROR: UUIRTOpen failed. WinError={ctypes.get_last_error()}", flush=True)
        return 1

    print(f"USB-UIRT opened: 0x{handle:X}", flush=True)

    info = UUINFO()
    if driver.UUIRTGetUUIRTInfo(ctypes.c_void_p(handle), ctypes.byref(info)):
        print(
            f"Firmware: 0x{info.fwVersion:04X}, "
            f"Protocol: 0x{info.protVersion:04X}, "
            f"Date: {info.fwDateYear:02d}-{info.fwDateMonth:02d}-{info.fwDateDay:02d}",
            flush=True,
        )

    config = ctypes.c_uint32()
    if driver.UUIRTGetUUIRTConfig(ctypes.c_void_p(handle), ctypes.byref(config)):
        print(f"Config: 0x{config.value:08X}", flush=True)

    ir_buffer = ctypes.create_string_buffer(BUFFER_SIZE)
    abort_flag = BOOL(0)
    outcome = {"result": None, "error": None}

    @LEARN_CALLBACK
    def learn_callback(progress, quality, carrier, user_data):
        print(
            f"CALLBACK Progress={progress}%  Quality={quality & 0xFF}%  "
            f"Carrier={carrier} Hz",
            flush=True,
        )

    def learn_worker():
        try:
            outcome["result"] = driver.UUIRTLearnIR(
                ctypes.c_void_p(handle),
                IRFMT_PRONTO,
                ctypes.cast(ir_buffer, ctypes.POINTER(ctypes.c_char)),
                learn_callback,
                ctypes.c_void_p(0x5A5A5A5A),
                ctypes.byref(abort_flag),
                0,
                None,
                None,
            )
        except BaseException as error:
            outcome["error"] = repr(error)

    try:
        print("", flush=True)
        print("Learning started.", flush=True)
        print("Aim the remote at USB-UIRT from close range.", flush=True)
        print("Press the same button repeatedly until learning reaches 100%.", flush=True)

        worker = threading.Thread(target=learn_worker, daemon=True)
        worker.start()

        try:
            while worker.is_alive():
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("Ctrl+C received. Requesting abort...", flush=True)
            abort_flag.value = 1
            worker.join(timeout=5.0)

        if worker.is_alive():
            print("ERROR: UUIRTLearnIR did not stop after abort.", flush=True)
            return 2
        if outcome["error"]:
            print(f"ERROR: {outcome['error']}", flush=True)
            return 1
        if not outcome["result"]:
            print("ERROR: UUIRTLearnIR failed or was aborted.", flush=True)
            return 1

        pronto = ir_buffer.value.decode("ascii", errors="replace").strip()
        if not pronto:
            print("ERROR: UUIRTLearnIR returned an empty code.", flush=True)
            return 1

        print("", flush=True)
        print("Pronto Hex:", flush=True)
        print(pronto, flush=True)
        output_path.write_text(pronto + "\n", encoding="ascii")
        print(f"Saved: {output_path}", flush=True)
        return 0
    finally:
        result = driver.UUIRTClose(ctypes.c_void_p(handle))
        print(f"USB-UIRT closed. Result={result}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
