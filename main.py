#!/usr/bin/env python3
"""Copy entrypoint for news-image-20261124 (round 3).

Stdlib only. Validates the source PNG (magic bytes, IHDR 1024x1024,
per-chunk CRC32 through IEND, 1 MiB size guard) and copies entry.png
to <output>/entry.png. The output directory is cleared of its contents
first (contents only, never the directory itself). Output defaults to
/output and honours MAKEFUN_OUTPUT_DIR. Result is mode 0644.
No network, no clock, no randomness: the copy is byte-identical.
"""
import os
import struct
import sys
import zlib

MAX_BYTES = 1 << 20
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SOURCE_NAME = "entry.png"


def fail(message):
    print("error: " + message, file=sys.stderr)
    return 1


def validate_png(data):
    """Return None if data is a valid 1024x1024 PNG, else an error string."""
    if len(data) > MAX_BYTES:
        return "source image exceeds 1 MiB (%d bytes)" % len(data)
    if len(data) < 8 or data[:8] != PNG_MAGIC:
        return "not a PNG file (bad magic)"
    pos = 8
    seen_ihdr = False
    while True:
        if pos + 8 > len(data):
            return "truncated PNG chunk header"
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 12 + length
        if end > len(data):
            return "truncated PNG chunk %r" % ctype.decode("latin-1")
        stored_crc = struct.unpack(">I", data[pos + 8 + length:pos + 12 + length])[0]
        actual_crc = zlib.crc32(ctype + data[pos + 8:pos + 8 + length]) & 0xFFFFFFFF
        if stored_crc != actual_crc:
            return "PNG chunk %r has a bad CRC" % ctype.decode("latin-1")
        if ctype == b"IHDR":
            if length != 13:
                return "IHDR chunk has wrong length"
            width, height = struct.unpack(">II", data[pos + 8:pos + 16])
            if (width, height) != (1024, 1024):
                return "image is %dx%d, expected 1024x1024" % (width, height)
            seen_ihdr = True
        if ctype == b"IEND":
            if pos + 12 + length != len(data):
                return "trailing data after IEND"
            break
        pos = end
    if not seen_ihdr:
        return "missing IHDR chunk"
    return None


def clear_output_dir(path):
    """Remove everything inside path; leave path itself in place."""
    for name in os.listdir(path):
        target = os.path.join(path, name)
        if os.path.isdir(target) and not os.path.islink(target):
            clear_output_dir(target)
            os.rmdir(target)
        else:
            os.unlink(target)


def main(argv):
    source = os.path.join(os.path.dirname(os.path.abspath(__file__)), SOURCE_NAME)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        with open(source, "rb") as fh:
            data = fh.read()
    except OSError as exc:
        return fail("cannot read %s: %s" % (source, exc))
    problem = validate_png(data)
    if problem is not None:
        return fail(problem)
    try:
        os.makedirs(out_dir, exist_ok=True)
        clear_output_dir(out_dir)
        dest = os.path.join(out_dir, SOURCE_NAME)
        with open(dest, "wb") as fh:
            fh.write(data)
        os.chmod(dest, 0o644)
    except OSError as exc:
        return fail("cannot write output: %s" % exc)
    print("wrote %s (%d bytes)" % (dest, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
