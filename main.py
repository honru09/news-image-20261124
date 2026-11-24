#!/usr/bin/env python3
"""news-image-20261124 entrypoint.

Copies the pre-built infographic entry.png (1024x1024, one page summing up
the world news of Tuesday 24 November 2026) to <output dir>/entry.png.

Deterministic: the output is a byte-for-byte copy of the committed image,
so repeated runs always produce identical bytes. No network, no randomness,
no clock reads.
"""

import os
import shutil
import struct
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
EXPECTED_WIDTH = 1024
EXPECTED_HEIGHT = 1024


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


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    source = os.path.join(here, "entry.png")
    target_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    target = os.path.join(target_dir, "entry.png")

    if not os.path.isfile(source):
        return fail("missing expected image file: %s" % source)

    with open(source, "rb") as handle:
        data = handle.read()

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

    os.makedirs(target_dir, exist_ok=True)
    clear_contents(target_dir)

    with open(target, "wb") as handle:
        handle.write(data)
    os.chmod(target, 0o644)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
