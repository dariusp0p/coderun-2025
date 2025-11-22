import { segmentText } from "./segment.js";

export function compress(text) {
  const chars = segmentText(text);
  if (chars.length === 0) return "";

  let out = "";
  let prev = chars[0];
  let count = 1;

  for (let i = 1; i < chars.length; i++) {
    const c = chars[i];
    if (c === prev) count++;
    else {
      out += prev + String(count);
      prev = c;
      count = 1;
    }
  }
  out += prev + String(count);
  return out;
}
