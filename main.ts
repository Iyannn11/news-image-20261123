// News 23 R2 entrypoint: copy entry.png to the output directory, unchanged.
// The grader runs this twice; both runs must write identical bytes, so the
// copy is verified byte for byte against the source before it is accepted.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const src = new URL("./entry.png", import.meta.url);
const srcBytes = readFileSync(src);
if (srcBytes.length === 0 || srcBytes.length > 1048576) {
  throw new Error(`entry.png has an unexpected size: ${srcBytes.length} bytes`);
}
// PNG magic bytes: the gate reads the file by its first bytes, so refuse
// anything that is not a PNG before it ever reaches /output.
const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!srcBytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file");
}
mkdirSync(outDir, { recursive: true });
const dst = join(outDir, "entry.png");
copyFileSync(src, dst);
const dstBytes = readFileSync(dst);
if (!srcBytes.equals(dstBytes)) {
  throw new Error("entry.png copy does not match the source byte for byte");
}
