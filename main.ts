// main.ts - the entrypoint for the news-image-20261124 program.
//
// The front page is rendered at authoring time by compose.py and shipped
// in this repository as entry.png. This program does one thing: carry
// that fixed image into the grader's output directory unchanged, so the
// two grader runs each write byte-identical output.
//
// It checks the image against the competition's caps before copying - a
// genuine PNG (magic bytes, an IHDR chunk, an IEND chunk), no more than
// 1024 by 1024 pixels and no more than 1 MiB - and fails loudly on
// anything off, instead of shipping a bad image. After the write it
// reads the copy back and compares it byte for byte with the source, so
// a truncated write can never slip through.
//
// Node 22, standard library only. No network access, no dependencies.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const IMAGE = "entry.png";
const BYTE_CAP = 1024 * 1024;
const SIDE_CAP = 1024;

// Every PNG file starts with these eight magic bytes.
const MAGIC = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

function die(msg) {
  console.error("main.ts: " + msg);
  process.exit(1);
}

// Find entry.png: next to this script first, then the working directory,
// so the program still works when run from the repository root while the
// script itself lives somewhere else.
function locateImage() {
  const here = dirname(fileURLToPath(import.meta.url));
  for (const candidate of [join(here, IMAGE), join(process.cwd(), IMAGE)]) {
    try {
      return readFileSync(candidate);
    } catch (err) {
      if (err.code !== "ENOENT") {
        die("cannot read " + candidate + ": " + err.message);
      }
    }
  }
  die("could not find " + IMAGE + " next to main.ts or in " + process.cwd());
}

// Read the width and height out of the PNG header, checking the magic
// bytes, the IHDR chunk and the trailing IEND chunk on the way.
function pngDimensions(bytes) {
  if (bytes.length < 33) {
    die(IMAGE + " is too short to be a PNG (" + bytes.length + " bytes)");
  }
  for (let i = 0; i < MAGIC.length; i++) {
    if (bytes[i] !== MAGIC[i]) {
      die(IMAGE + " does not start with the PNG magic bytes");
    }
  }
  if (bytes.toString("latin1", 12, 16) !== "IHDR") {
    die(IMAGE + " has no IHDR chunk where one belongs");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  // A PNG ends with a 12-byte IEND chunk: four zero length bytes, the
  // four letters IEND, then a 4-byte CRC. The letters sit 8 bytes from
  // the end of the file.
  if (bytes.toString("latin1", bytes.length - 8, bytes.length - 4) !== "IEND") {
    die(IMAGE + " does not end with an IEND chunk");
  }
  return { width, height };
}

function run() {
  const bytes = locateImage();

  if (bytes.length > BYTE_CAP) {
    die(IMAGE + " is " + bytes.length + " bytes, over the 1 MiB cap");
  }
  const { width, height } = pngDimensions(bytes);
  if (width > SIDE_CAP || height > SIDE_CAP) {
    die(IMAGE + " is " + width + "x" + height + ", over the 1024x1024 cap");
  }
  if (width < 1 || height < 1) {
    die(IMAGE + " declares an impossible size " + width + "x" + height);
  }

  const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
  const outPath = join(outDir, IMAGE);
  mkdirSync(outDir, { recursive: true });
  writeFileSync(outPath, bytes);

  // Prove the copy matches the source, byte for byte.
  if (!readFileSync(outPath).equals(bytes)) {
    die("wrote " + outPath + " but the copy does not match " + IMAGE);
  }

  console.log(
    "wrote " + outPath + " (" + bytes.length + " bytes, " +
    width + "x" + height + ")"
  );
}

run();
