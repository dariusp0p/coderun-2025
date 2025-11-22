import React from "react";

export default function Metrics({ inputLen, outputLen, ratio, timeMs }) {
  return (
    <div className="metrics">
      <div className="metric">
        <div className="metric-title">Input length</div>
        <div className="metric-val">{inputLen}</div>
      </div>

      <div className="metric">
        <div className="metric-title">Output length</div>
        <div className="metric-val">{outputLen}</div>
      </div>

      <div className="metric">
        <div className="metric-title">Compression ratio</div>
        <div className="metric-val">
          {Number.isFinite(ratio) ? ratio.toFixed(3) : "-"}
        </div>
      </div>

      <div className="metric">
        <div className="metric-title">Execution time</div>
        <div className="metric-val">
          {timeMs != null ? `${timeMs.toFixed(2)} ms` : "-"}
        </div>
      </div>
    </div>
  );
}
