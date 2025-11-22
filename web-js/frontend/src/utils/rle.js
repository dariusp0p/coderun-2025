// RLE compression that supports unicode (emoji etc).
export function compressRLE(input) {
  const chars = Array.from(input); // unicode-safe split
  if (chars.length === 0) return "";

  let out = [];
  let curr = chars[0];
  let count = 1;

  for (let i = 1; i < chars.length; i++) {
    if (chars[i] === curr) count++;
    else {
      out.push(curr + String(count));
      curr = chars[i];
      count = 1;
    }
  }
  out.push(curr + String(count));
  return out.join("");
}

// Decompression expects format like a3b2🙂4 etc.
// We parse: <char><number+> repeated.
export function decompressRLE(input) {
  const chars = Array.from(input);
  if (chars.length === 0) return "";

  let out = [];
  let i = 0;

  while (i < chars.length) {
    const ch = chars[i++];
    if (i >= chars.length) {
      throw new Error("Format invalid: lipseste numarul dupa caracter.");
    }

    let numStr = "";
    while (i < chars.length && /[0-9]/.test(chars[i])) {
      numStr += chars[i++];
    }

    if (numStr === "") {
      throw new Error("Format invalid: lipseste numarul dupa caracter.");
    }

    const n = Number(numStr);
    if (!Number.isFinite(n) || n < 0) {
      throw new Error("Format invalid: numar incorect.");
    }

    out.push(ch.repeat(n));
  }

  return out.join("");
}
