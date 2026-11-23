// News 23 image entry (Node 22, standard library only): the image is the
// entry.png beside this file, rendered by render.py, and the program copies
// it to /output/entry.png. The gate takes a whole PNG of at most 1 MiB and
// 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const botDir = new URL('.', import.meta.url).pathname;
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(botDir, 'output');
mkdirSync(outDir, { recursive: true });
const src = join(botDir, 'entry.png');
const dst = join(outDir, 'entry.png');
const size = statSync(src).size;
if (size > 1048576) throw new Error('entry.png exceeds 1 MiB: ' + size);
copyFileSync(src, dst);
// Verify the copy is byte-identical: the judge sees exactly these bytes.
const a = readFileSync(src);
const b = readFileSync(dst);
if (a.length !== b.length || !a.equals(b)) {
  throw new Error('entry.png copy mismatch');
}
console.log('entry.png copied: ' + a.length + ' bytes');
