// usage: node scripts/bench.mjs <scale> '<inputProps json>' : per-frame cost = (t(12 frames) - t(2 frames)) / 10
import { bundle } from "@remotion/bundler";
import { renderMedia, selectComposition } from "@remotion/renderer";
import path from "node:path";
const [scale = "1", props = "{}"] = process.argv.slice(2);
const inputProps = JSON.parse(props);
const browserExecutable = "/opt/pw-browsers/chromium", chromiumOptions = { gl: "swangle" };
const serveUrl = await bundle({ entryPoint: path.resolve("src/index.ts") });
const composition = await selectComposition({ serveUrl, id: "MincemeatShort", inputProps, browserExecutable, chromiumOptions });
const run = async (n) => { const t0 = Date.now(); await renderMedia({ composition, serveUrl, codec: "h264", outputLocation: `out/test/bench_${n}.mp4`, frameRange: [600, 600 + n - 1], scale: Number(scale), inputProps, concurrency: 1, browserExecutable, chromiumOptions, timeoutInMilliseconds: 900000 }); return (Date.now() - t0) / 1000; };
const a = await run(2), b = await run(8);
console.log(`scale ${scale} ${props}: ${((b - a) / 6).toFixed(2)} s/frame (setup ~${(a - 2 * (b - a) / 6).toFixed(1)} s)`);
