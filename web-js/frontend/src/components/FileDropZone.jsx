import React, { useRef, useState } from "react";

export default function FileDropZone({ onTextLoaded }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  function readFile(file) {
    if (!file) return;
    if (!file.type.startsWith("text/") && !file.name.endsWith(".txt")) {
      alert("Please upload a text file (.txt).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => onTextLoaded(String(e.target.result || ""));
    reader.readAsText(file);
  }

  return (
    <div
      className={`dropzone ${dragging ? "dragging" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragging(false);
        readFile(e.dataTransfer.files?.[0]);
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".txt,text/plain"
        hidden
        onChange={(e) => readFile(e.target.files?.[0])}
      />
      <div className="dropzone-inner">
        <div className="drop-title">Drag & drop file here</div>
        <div className="drop-sub">or click to upload</div>
      </div>
    </div>
  );
}
