#!/usr/bin/env python3
"""
Generate the English (US) dialog font for showfloor's English text option.

The glyphs are read from a user-supplied Super Mario 64 (USA) ROM and converted
into the same 8x16 1bpp format as the Japanese dialog font, so the existing
JP text renderer can draw them. No ROM data is stored in this repository.

Usage: extract_en_font.py <baserom.us.z64> <output.inc.c> [--preview out.png]
"""

import hashlib
import struct
import sys
import zlib

US_SHA1 = "9bef1128717f958171a4afac3ed78ee2bb4e86ce"

# ROM offset of the MIO0-compressed segment 2 in the US ROM
SEGMENT2_ROM_OFFSET = 0x108A40

# Dialog character code -> offset of its 16x8 IA4 glyph within segment 2
# (the layout of the US dialog font table, main_font_lut)
GLYPHS = {
    **{i: 0x5900 + i * 0x40 for i in range(0x00, 0x3E)},  # 0-9, A-Z, a-z
    0x3E: 0x6B80,  # '
    0x3F: 0x6A80,  # .
    0x50: 0x6F00,  # [C]-up
    0x51: 0x6F40,  # [C]-down
    0x52: 0x6F80,  # [C]-left
    0x53: 0x6FC0,  # [C]-right
    0x54: 0x6DC0,  # [A]
    0x55: 0x6E00,  # [B]
    0x56: 0x6E40,  # [C]
    0x57: 0x6E80,  # [Z]
    0x58: 0x6EC0,  # [R]
    0x6F: 0x6B40,  # ,
    0x9F: 0x6D40,  # -
    0xE1: 0x6980,  # (
    0xE2: 0x69C0,  # )(
    0xE3: 0x6A00,  # )
    0xE4: 0x6880,  # <->
    0xE5: 0x6D80,  # &
    0xE6: 0x6D00,  # :
    0xF2: 0x68C0,  # !
    0xF3: 0x6AC0,  # %
    0xF4: 0x6BC0,  # ?
    0xF5: 0x6C80,  # opening double quote
    0xF6: 0x6CC0,  # closing double quote
    0xF7: 0x6A40,  # ~
    0xF9: 0x6900,  # coin
    0xFA: 0x6C00,  # filled star
    0xFB: 0x6940,  # x
    0xFC: 0x6B00,  # interpunct
    0xFD: 0x6C40,  # hollow star
}


def mio0_decode(data, offset):
    if data[offset:offset + 4] != b"MIO0":
        raise ValueError("no MIO0 header at 0x%X" % offset)
    size, comp_off, uncomp_off = struct.unpack(">III", data[offset + 4:offset + 16])
    out = bytearray()
    layout = offset + 16
    comp = offset + comp_off
    raw = offset + uncomp_off
    bits = 0
    nbits = 0
    while len(out) < size:
        if nbits == 0:
            bits = struct.unpack(">I", data[layout:layout + 4])[0]
            layout += 4
            nbits = 32
        if bits & 0x80000000:
            out.append(data[raw])
            raw += 1
        else:
            v = struct.unpack(">H", data[comp:comp + 2])[0]
            comp += 2
            length = (v >> 12) + 3
            dist = (v & 0xFFF) + 1
            for _ in range(length):
                out.append(out[-dist])
        bits = (bits << 1) & 0xFFFFFFFF
        nbits -= 1
    return bytes(out[:size])


def ia4_pixel_on(glyph, col, row):
    """US glyphs are 16 wide x 8 tall IA4 images (4 bits per pixel)."""
    idx = row * 16 + col
    byte = glyph[idx // 2]
    nib = (byte >> 4) if idx % 2 == 0 else (byte & 0xF)
    intensity = nib >> 1
    alpha = nib & 1
    return alpha != 0 and intensity >= 4


def convert_glyph(glyph):
    """
    The US renderer draws its 16x8 glyphs rotated by 90 degrees; the JP
    renderer draws 8x16 1bpp glyphs upright. Pixel (row r, column c) of the
    upright glyph comes from texel (row 7 - c, column 15 - r) of the US glyph.
    """
    out = bytearray(16)
    for r in range(16):
        b = 0
        for c in range(8):
            if ia4_pixel_on(glyph, 15 - r, 7 - c):
                b |= 0x80 >> c
        out[r] = b
    return bytes(out)


def write_preview(path, glyphs):
    codes = sorted(glyphs)
    cols = 16
    rows = (len(codes) + cols - 1) // cols
    w, h = cols * 10, rows * 18
    pix = [[0] * w for _ in range(h)]
    for n, code in enumerate(codes):
        ox, oy = (n % cols) * 10 + 1, (n // cols) * 18 + 1
        for r in range(16):
            for c in range(8):
                if glyphs[code][r] & (0x80 >> c):
                    pix[oy + r][ox + c] = 255
    raw = b"".join(b"\x00" + bytes(row) for row in pix)

    def chunk(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)

    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 0, 0, 0, 0)))
        f.write(chunk(b"IDAT", zlib.compress(raw)))
        f.write(chunk(b"IEND", b""))


def main():
    args = sys.argv[1:]
    preview = None
    if "--preview" in args:
        i = args.index("--preview")
        preview = args[i + 1]
        del args[i:i + 2]
    if len(args) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)
    rom_path, out_path = args

    try:
        with open(rom_path, "rb") as f:
            rom = f.read()
    except OSError:
        print("error: the English text option needs a Super Mario 64 (USA) ROM at '%s'" % rom_path, file=sys.stderr)
        sys.exit(1)
    if hashlib.sha1(rom).hexdigest() != US_SHA1:
        print("error: '%s' is not an unmodified Super Mario 64 (USA) ROM in .z64 (big-endian) format" % rom_path,
              file=sys.stderr)
        sys.exit(1)

    seg2 = mio0_decode(rom, SEGMENT2_ROM_OFFSET)
    glyphs = {code: convert_glyph(seg2[off:off + 64]) for code, off in GLYPHS.items()}

    with open(out_path, "w") as f:
        f.write("// Generated by tools/extract_en_font.py from the Super Mario 64 (USA) ROM. Do not edit.\n\n")
        for code in sorted(glyphs):
            data = ",".join("0x%02X" % b for b in glyphs[code])
            f.write("ALIGNED8 static const Texture texture_font_char_en_%02X[] = { %s };\n" % (code, data))
        # Positional (C89-compatible) initializer list for the 256-entry font table
        f.write("\n#define FONT_EN_LUT \\\n")
        for code in range(256):
            entry = ("texture_font_char_en_%02X" % code) if code in glyphs else "0x0"
            f.write("    %s,%s\n" % (entry, " \\" if code != 255 else ""))
        f.write("\n")

    if preview:
        write_preview(preview, glyphs)


if __name__ == "__main__":
    main()
