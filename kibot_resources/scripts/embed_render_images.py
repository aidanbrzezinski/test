#!/usr/bin/env python3
"""Permanently embed the top/bottom PCB render PNGs into the schematic's
"kibot_image_png_3d_viewer_top/bottom" placeholder spots.

KiBot's own kibot_image_<output> mechanism only pastes images into a
schematic PRINT/EXPORT output (PDF, SVG, ...) and restores the placeholder
afterwards -- it never writes a permanent (image ...) into the .kicad_sch
file. This script does that permanently, using the same PNG-parsing and
scale/position formula KiBot itself uses internally (see
INTI-CMNB/KiBot: misc.read_png() and out_base.py: sch_replace_one_image()),
re-implemented here with no dependency on KiBot's internal Python API, so
it keeps working even if that internal API changes.

Run from the repository root, after the render PNGs have been generated:
    python3 kibot_resources/scripts/embed_render_images.py

Safe by design: only ever touches the exact, uniquely-named block for each
slot (found by exact text search + balanced-parenthesis scanning, never a
whole-file reparse/rewrite), and only writes a file back to disk after ALL
of that file's replacements succeeded -- any error aborts with a non-zero
exit code and leaves every file untouched.
"""
import glob
import re
import struct
import sys
import uuid
from base64 import b64encode
from pathlib import Path

# Width (mm) the rendered image is scaled to. Matches the current cover
# page placeholder text boxes (69.85mm). Height follows from the PNG's
# aspect ratio, same as KiBot's own behavior. Update this if the cover
# page layout is resized.
TARGET_WIDTH_MM = 69.85

SLOTS = ("top", "bottom")


def read_png_size_and_dpi(data):
    """Return (width_px, height_px, dpi), parsing IHDR/pHYs chunks directly.

    Mirrors kibot.misc.read_png(): defaults to 300 dpi if there's no pHYs
    chunk, exactly like KiBot does.
    """
    if data[0:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG file")
    offset = 8
    dpi = 300
    w = h = None
    while offset < len(data):
        size, ctype = struct.unpack(">L4s", data[offset:offset + 8])
        if ctype == b"IHDR":
            w, h = struct.unpack(">LL", data[offset + 8:offset + 16])
        elif ctype == b"pHYs":
            dpi_w, dpi_h, units = struct.unpack(">LLB", data[offset + 8:offset + 17])
            if units == 1 and dpi_w == dpi_h:
                dpi = dpi_w / (100 / 2.54)
            break
        elif ctype == b"IEND":
            break
        offset += size + 12
    if w is None:
        raise ValueError("broken PNG: no IHDR chunk")
    return w, h, dpi


def find_matching_paren(text, open_idx):
    """Return the index of the ')' matching the '(' at open_idx, honoring
    double-quoted strings (with backslash escapes) so parens inside them
    don't affect the depth count."""
    depth = 0
    i = open_idx
    in_quote = False
    while i < len(text):
        c = text[i]
        if in_quote:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_quote = False
        else:
            if c == '"':
                in_quote = True
            elif c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
                if depth == 0:
                    return i
        i += 1
    raise ValueError("unbalanced parentheses")


def find_block_containing(text, needle):
    """Find the smallest top-level '(image ...)' block containing `needle`."""
    search_from = 0
    while True:
        idx = text.find("(image", search_from)
        if idx == -1:
            return None
        end = find_matching_paren(text, idx)
        if needle in text[idx:end + 1]:
            return idx, end
        search_from = end + 1


def line_start_of(text, idx):
    return text.rfind("\n", 0, idx) + 1


def extract_at(block):
    m = re.search(r"\(at\s+([-\d.]+)\s+([-\d.]+)", block)
    if not m:
        raise ValueError("no (at x y) found")
    return float(m.group(1)), float(m.group(2))


def build_image_block(indent, pos_x, pos_y, scale, img_uuid, png_bytes):
    b64 = b64encode(png_bytes).decode("ascii")
    chunks = [b64[i:i + 76] for i in range(0, len(b64), 76)]
    lines = [
        f"{indent}(image",
        f"{indent}\t(at {pos_x:.6f} {pos_y:.6f})",
        f"{indent}\t(scale {scale:.6f})",
        f"{indent}\t(uuid \"{img_uuid}\")",
        f"{indent}\t(data",
    ]
    lines += [f"{indent}\t\t{c}" for c in chunks]
    lines.append(f"{indent}\t)")
    lines.append(f"{indent})")
    return "\n".join(lines)


def find_render_png(slot):
    """Find Images/*-top.png or Images/*-bottom.png, without assuming the
    exact %f/%I/%v-derived filename prefix KiBot used."""
    pattern = re.compile(rf"-{slot}\.png$")
    for f in sorted(glob.glob("Images/*.png")):
        if pattern.search(f):
            return f
    return None


def process_schematic(sch_path):
    text = Path(sch_path).read_text(encoding="utf-8")
    original = text
    for slot in SLOTS:
        marker_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"kibot_image_png_3d_viewer_{slot}:{sch_path}"))
        span = find_block_containing(text, marker_uuid)
        is_update = span is not None
        if not is_update:
            marker = f'(text_box "kibot_image_png_3d_viewer_{slot}"'
            idx = text.find(marker)
            if idx == -1:
                continue  # no placeholder and nothing embedded yet: nothing to do
            span = (idx, find_matching_paren(text, idx))

        png_path = find_render_png(slot)
        if png_path is None:
            print(f"WARNING: no Images/*-{slot}.png found, skipping {slot} in {sch_path}", file=sys.stderr)
            continue

        start, end = span
        block = text[start:end + 1]
        png_bytes = Path(png_path).read_bytes()
        w, h, dpi = read_png_size_and_dpi(png_bytes)
        img_w_mm = w / dpi * 25.4
        img_h_mm = h / dpi * 25.4
        scale = TARGET_WIDTH_MM / img_w_mm

        if is_update:
            pos_x, pos_y = extract_at(block)
        else:
            box_x, box_y = extract_at(block)
            pos_x = box_x + TARGET_WIDTH_MM / 2
            pos_y = box_y + (img_h_mm * scale) / 2

        # Splice from the start of the LINE (not the token), and give the
        # replacement its own explicit indent on every line -- this avoids
        # relying on "carry-over" whitespace already present before `start`,
        # which would otherwise double up on each successive run.
        line_start = line_start_of(text, start)
        new_block = build_image_block("\t", pos_x, pos_y, scale, marker_uuid, png_bytes)
        text = text[:line_start] + new_block + text[end + 1:]
        print(f"{'Updated' if is_update else 'Embedded'} {slot} render ({png_path}) in {sch_path}")

    if text != original:
        Path(sch_path).write_text(text, encoding="utf-8")
        return True
    return False


def main():
    changed = False
    for sch_path in sorted(glob.glob("*.kicad_sch")):
        changed |= process_schematic(sch_path)
    if not changed:
        print("Nothing to do: no placeholders found and embedded renders already up to date.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
