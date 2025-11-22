import React from "react";

export default function TextAreas({ input, output, onInputChange }) {
  return (
    <div className="grid">
      <div className="panel">
        <label>Input</label>
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Write here or upload a file..."
          rows={10}
        />
      </div>

      <div className="panel">
        <label>Output (read-only)</label>
        <textarea
          value={output}
          readOnly
          placeholder="The result will appear here..."
          rows={10}
        />
      </div>
    </div>
  );
}
