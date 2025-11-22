import React from "react";

export default function Controls({ onCompress, onDecompress, onClear, busy }) {
  return (
    <div className="controls">
      <button onClick={onCompress} disabled={busy}>
        Compress
      </button>
      <button onClick={onDecompress} disabled={busy}>
        Decompress
      </button>
      <button className="secondary" onClick={onClear} disabled={busy}>
        Clear
      </button>
    </div>
  );
}
