#!/usr/bin/env python3
"""news-image-20261124 entrypoint.

Copies the pre-built infographic entry.png (1024x1024, one page summing up
the world news of Tuesday 24 November 2026) to <output dir>/entry.png.

Deterministic: the output is a byte-for-byte copy of the committed image,
so repeated runs always produce identical bytes. Before copying, the
image is validated: PNG signature, IHDR 1024x1024 canvas, a 1 MiB size
guard, and a CRC32 check on every PNG chunk. No network, no randomness,
no clock reads.
"""

import os
import shutil
import struct
import sys
import zlib

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024
MAX_FILE_SIZE = 1024 * 1024  # 1 MiB size guard on the source image


def fail(message):
    sys.stderr.write("error: %s\n" % message)
    return 1


def clear_contents(target_dir):
    """Remove everything inside target_dir, leaving the directory itself."""
    for name in os.listdir(target_dir):
        path = os.path.join(target_dir, name)
        if os.path.isdir(path) and not os.path.islink(path):
            shutil.rmtree(path)
        else:
            os.remove(path)


def validate_chunk_crcs(data):
    """Walk every PNG chunk and verify its CRC32 (over type + data).

    Returns an error string, or None if the whole chunk stream is intact
    and ends in an IEND chunk. A truncated or mis-CRC'd chunk means the
    committed entry.png is corrupt and must not be shipped.
    """
    offset = 8  # skip the PNG signature
    seen_iend = False
    while offset < len(data):
        if offset + 8 > len(data):
            return "truncated PNG chunk header"
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        chunk_type = data[offset + 4:offset + 8]
        chunk_start = offset + 8
        chunk_end = chunk_start + length
        if chunk_end + 4 > len(data):
            return "truncated PNG chunk %r" % chunk_type.decode("ascii", "replace")
        stored_crc = struct.unpack(">I", data[chunk_end:chunk_end + 4])[0]
        actual_crc = zlib.crc32(chunk_type)
        actual_crc = zlib.crc32(data[chunk_start:chunk_end], actual_crc)
        if actual_crc != stored_crc:
            return "PNG chunk %r has a bad CRC" % chunk_type.decode("ascii", "replace")
        offset = chunk_end + 4
        if chunk_type == b"IEND":
            seen_iend = True
            break
    if not seen_iend:
        return "PNG file is missing its IEND chunk"
    if offset != len(data):
        return "trailing data after PNG IEND chunk"
    return None


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(target_dir, "entry.png")

    if not os.path.isfile(source):
        return fail("missing expected image file: %s" % source)

    with open(source, "rb") as handle:
        data = handle.read()

    # Guard against an unexpectedly large source image.
    if len(data) > MAX_FILE_SIZE:
        return fail("entry.png is %d bytes, over the %d-byte limit"
                    % (len(data), MAX_FILE_SIZE))

    # The file must be a real PNG: 8-byte signature followed by an IHDR
    # chunk declaring the expected 1024x1024 canvas. Anything else means
    # the committed entry.png is corrupt or was replaced by the wrong file.
    if len(data) < 24 or data[:8] != PNG_MAGIC:
        return fail("entry.png is not a valid PNG file "
                    "(bad or missing PNG signature)")

    if data[12:16] != b"IHDR":
        return fail("entry.png is not a valid PNG file "
                    "(first chunk is not IHDR)")

    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
        return fail("entry.png has wrong size %dx%d, expected %dx%d"
                    % (width, height, EXPECTED_WIDTH, EXPECTED_HEIGHT))

    # Every chunk's CRC must check out before the image is copied.
    crc_error = validate_chunk_crcs(data)
    if crc_error is not None:
        return fail("entry.png failed PNG integrity check: %s" % crc_error)

    os.makedirs(target_dir, exist_ok=True)
    clear_contents(target_dir)

    with open(target, "wb") as handle:
        handle.write(data)
    os.chmod(target, 0o644)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
