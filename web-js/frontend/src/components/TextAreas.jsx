import React from "react";

export default function TextAreas({ input, output, onInputChange }) {
  return (
    <div className="grid">
      <div className="panel">
        <label>Input</label>
        <textarea
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder="Scrie aici sau încarcă un fișier..."
          rows={10}
        />
      </div>

      <div className="panel">
        <label>Output (read-only)</label>
        <textarea
          value={output}
          readOnly
          placeholder="Rezultatul va apărea aici..."
          rows={10}
        />
      </div>
    </div>
  );
}
