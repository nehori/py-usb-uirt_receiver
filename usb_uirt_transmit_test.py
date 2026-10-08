# coding: utf-8
"""Transmit a Pronto Hex code from a text file through USB-UIRT."""

import argparse
import ctypes
import sys
from pathlib import Path

DLL_NAME = "uuirtdrv.dll"
DEFAULT_CODE_FILE = "learned_pronto.txt"
IRFMT_PRONTO = 0x0010
BOOL = ctypes.c_int


def parse_args():
    parser = argparse.ArgumentParser(
        description="Transmit a Pronto Hex code from a text file through USB-UIRT."
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=Path,
        default=Path(DEFAULT_CODE_FILE),
        help=f"Text file containing one Pronto Hex code. Default: {DEFAULT_CODE_FILE}",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=3,
        help="Transmission repeat count. Default: 3.",
    )
    parser.add_argument(
        "--wait",
        type=int,
        default=0,
        help="Inactivity wait time in milliseconds. Default: 0.",
    )
    return parser.parse_args()


def normalize_pronto(value: str) -> str:
    words = value.replace("\r", " ").replace("\n", " ").split()
    if len(words) < 6:
        raise ValueError("The Pronto Hex code is too short.")

    normalized = []
    for word in words:
        if len(word) != 4:
            raise ValueError(f"Invalid Pronto word: {word}")
        int(word, 16)
        normalized.append(word.upper())

    if normalized[0] != "0000":
        raise ValueError("Only raw Pronto Hex codes beginning with 0000 are supported.")

    intro_pairs = int(normalized[2], 16)
    repeat_pairs = int(normalized[3], 16)
    expected_words = 4 + 2 * (intro_pairs + repeat_pairs)
    if len(normalized) != expected_words:
        raise ValueError(
            "Pronto length mismatch: "
            f"header expects {expected_words} words, got {len(normalized)}."
        )

    return " ".join(normalized)


def main() -> int:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    dll_path = base_dir / DLL_NAME
    code_path = args.file

    if not code_path.is_absolute():
        code_path = Path.cwd() / code_path

    if args.repeat < 0:
        print("ERROR: --repeat must be zero or greater.", flush=True)
        return 2
    if args.wait < 0:
        print("ERROR: --wait must be zero or greater.", flush=True)
        return 2
    if not dll_path.exists():
        print(f"ERROR: DLL not found: {dll_path}", flush=True)
        return 1
    if not code_path.exists():
        print(f"ERROR: Pronto file not found: {code_path}", flush=True)
        return 1

    try:
        pronto = normalize_pronto(code_path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", flush=True)
        return 2

    print(f"DLL: {dll_path}", flush=True)
    print(f"Pronto file: {code_path}", flush=True)
    print(f"Python: {sys.version}", flush=True)
    print(f"Python bitness: {ctypes.sizeof(ctypes.c_void_p) * 8}-bit", flush=True)
    print(f"Repeat count: {args.repeat}", flush=True)
    print(f"Pronto words: {len(pronto.split())}", flush=True)

    try:
        driver = ctypes.WinDLL(str(dll_path), use_last_error=True)
    except OSError as error:
        print(f"ERROR: Failed to load DLL: {error}", flush=True)
        print("Ensure that Python and uuirtdrv.dll have the same bitness.", flush=True)
        return 1

    driver.UUIRTOpen.argtypes = []
    driver.UUIRTOpen.restype = ctypes.c_void_p
    driver.UUIRTClose.argtypes = [ctypes.c_void_p]
    driver.UUIRTClose.restype = BOOL
    driver.UUIRTTransmitIR.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_void_p,
    ]
    driver.UUIRTTransmitIR.restype = BOOL

    invalid_handle = ctypes.c_void_p(-1).value
    handle = driver.UUIRTOpen()
    if not handle or handle == invalid_handle:
        print(f"ERROR: UUIRTOpen failed. WinError={ctypes.get_last_error()}", flush=True)
        return 1

    print(f"USB-UIRT opened: 0x{handle:X}", flush=True)
    try:
        result = driver.UUIRTTransmitIR(
            ctypes.c_void_p(handle),
            pronto.encode("ascii"),
            IRFMT_PRONTO,
            args.repeat,
            args.wait,
            None,
            None,
            None,
        )
        if not result:
            print(
                "ERROR: UUIRTTransmitIR failed. "
                f"WinError={ctypes.get_last_error()}",
                flush=True,
            )
            return 1
        print("IR transmission completed.", flush=True)
        return 0
    finally:
        close_result = driver.UUIRTClose(ctypes.c_void_p(handle))
        print(f"USB-UIRT closed. Result={close_result}", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
