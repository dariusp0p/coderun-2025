export function segmentText(text) {
  if (typeof Intl !== "undefined" && Intl.Segmenter) {
    const seg = new Intl.Segmenter("en", { granularity: "grapheme" });
    return Array.from(seg.segment(text), s => s.segment);
  }
  // fallback: code points (for..of)
  return Array.from(text);
}
