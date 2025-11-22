import { segmentText } from "./segment.js";

export function decompress(text) {
  const chars = segmentText(text);
  let out = "";

  let i = 0;
  while (i < chars.length) {
    const symbol = chars[i++];
    if (i >= chars.length) throw new Error("Format invalid: missing count");

    let numStr = "";
    while (i < chars.length && /^[0-9]$/.test(chars[i])) {
      numStr += chars[i++];
    }
    if (numStr === "") throw new Error("Format invalid: count not found");

    const count = Number(numStr);
    if (!Number.isFinite(count) || count < 0) throw new Error("Format invalid: bad count");

    out += symbol.repeat(count);
  }

  return out;
}
