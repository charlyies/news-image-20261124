// main.ts - entrypoint for the news-image-20261124 program.
//
// The front page is drawn at authoring time (see compose.py) and shipped
// in this repository as entry.png. This program's whole job is to carry
// that fixed image into the grader's output directory, unchanged, so both
// grader runs write byte-identical output.
//
// Before copying, it validates the image against the competition caps: a
// real PNG (magic bytes + IHDR + IEND), at most 1024 x 1024 px and at
// most 1 MiB. Anything off fails loudly instead of shipping a bad image.
// After writing, it reads the copy back and compares it byte for byte
// with the source, so a truncated write can never slip through.
//
// Node 22 standard library only. No network, no dependencies.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const SOURCE_NAME = "entry.png";
const OUTPUT_NAME = "entry.png";
const MAX_BYTES = 1024 * 1024;
const MAX_SIDE = 1024;

// The eight PNG magic bytes every PNG file starts with.
const PNG_MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function fail(message) {
  console.error("main.ts: " + message);
  process.exit(1);
}

// Where does entry.png live? Next to this script first; the working
// directory is the fallback, so the program still works when it is run
// from the repository root with a different script location.
function findSource() {
  const here = dirname(fileURLToPath(import.meta.url));
  const candidates = [join(here, SOURCE_NAME), join(process.cwd(), SOURCE_NAME)];
  for (const candidate of candidates) {
    try {
      return { path: candidate, bytes: readFileSync(candidate) };
    } catch (err) {
      if (err.code !== "ENOENT") {
        fail("cannot read " + candidate + ": " + err.message);
      }
    }
  }
  fail("could not find " + SOURCE_NAME + " next to main.ts or in " + process.cwd());
}

// Parse the PNG header out of the buffer: magic, then the IHDR chunk that
// carries the width and height. Returns { width, height }.
function readPngSize(bytes) {
  if (bytes.length < 33) {
    fail(SOURCE_NAME + " is too short to be a PNG (" + bytes.length + " bytes)");
  }
  for (let i = 0; i < PNG_MAGIC.length; i++) {
    if (bytes[i] !== PNG_MAGIC[i]) {
      fail(SOURCE_NAME + " does not start with the PNG magic bytes");
    }
  }
  const chunkType = bytes.toString("latin1", 12, 16);
  if (chunkType !== "IHDR") {
    fail(SOURCE_NAME + " has no IHDR chunk where one belongs (found " + chunkType + ")");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  // A PNG ends with a 12-byte IEND chunk: 4 zero length bytes, the four
  // letters IEND, then a 4-byte CRC. The letters sit 8 bytes from the end.
  const tail = bytes.toString("latin1", bytes.length - 8, bytes.length - 4);
  if (tail !== "IEND") {
    fail(SOURCE_NAME + " does not end with an IEND chunk (found " + tail + ")");
  }
  return { width, height };
}

function main() {
  const source = findSource();
  const bytes = source.bytes;

  if (bytes.length > MAX_BYTES) {
    fail(SOURCE_NAME + " is " + bytes.length + " bytes, over the 1 MiB cap");
  }
  const size = readPngSize(bytes);
  if (size.width > MAX_SIDE || size.height > MAX_SIDE) {
    fail(
      SOURCE_NAME + " is " + size.width + "x" + size.height +
      ", over the 1024x1024 cap"
    );
  }
  if (size.width < 1 || size.height < 1) {
    fail(
      SOURCE_NAME + " declares an impossible size " + size.width +
      "x" + size.height
    );
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const outPath = join(outDir, OUTPUT_NAME);
  mkdirSync(outDir, { recursive: true });
  writeFileSync(outPath, bytes);

  // Read the copy back and prove it matches the source byte for byte.
  const written = readFileSync(outPath);
  if (!written.equals(bytes)) {
    fail("wrote " + outPath + " but the copy does not match " + SOURCE_NAME);
  }

  console.log(
    "wrote " + outPath + " (" + bytes.length + " bytes, " +
    size.width + "x" + size.height + ")"
  );
}

main();
