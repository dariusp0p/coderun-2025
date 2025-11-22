import { useMemo, useState } from "react";
import TextAreas from "./components/TextAreas";
import Controls from "./components/Controls";
import Metrics from "./components/Metrics";
import FileDropZone from "./components/FileDropZone";
import StatusBar from "./components/StatusBar";

import { compressRemote, decompressRemote } from "./services/api";

export default function App() {
const [input, setInput] = useState("");
const [output, setOutput] = useState("");
const [status, setStatus] = useState("");
const [statusKind, setStatusKind] = useState("info");
const [timeMs, setTimeMs] = useState(null);
const [busy, setBusy] = useState(false);

const inputLen = useMemo(() => Array.from(input).length, [input]);
const outputLen = useMemo(() => Array.from(output).length, [output]);

const ratio = useMemo(() => {
 if (inputLen === 0) return NaN;
 return outputLen / inputLen;
}, [inputLen, outputLen]);

async function runWithTimer(fn) {
 const t0 = performance.now();
 const res = await fn();
 const t1 = performance.now();
 setTimeMs(t1 - t0);
 return res;
}

  async function handleCompress() {
    setBusy(true);
    setStatus("");
    try {
      const res = await runWithTimer(async () => {
        return await compressRemote(input);
      });

      setOutput(res);
      setStatus("Compression successful.");
      setStatusKind("success");
    } catch (e) {
      setOutput("");
      setStatus(e.message || "Error during compression.");
      setStatusKind("error");
    } finally {
      setBusy(false);
    }
  }

  async function handleDecompress() {
    setBusy(true);
    setStatus("");
    try {
      const res = await runWithTimer(async () => {
        return await decompressRemote(input);
      });

      setOutput(res);
      setStatus("Decompression successful.");
      setStatusKind("success");
    } catch (e) {
      setOutput("");
      setStatus(e.message || "Error during decompression.");
      setStatusKind("error");
    } finally {
      setBusy(false);
    }
  }

function handleClear() {
 setInput("");
 setOutput("");
 setStatus("");
 setTimeMs(null);
}

  return (
    <div className="app">
      <header className="header">
        <h1>RLE Text Utility</h1>
        <p>Compression / Decompression Run-Length Encoding</p>
      </header>

   <FileDropZone onTextLoaded={(text) => setInput(text)} />

   <TextAreas input={input} output={output} onInputChange={setInput} />

   <Controls
     onCompress={handleCompress}
     onDecompress={handleDecompress}
     onClear={handleClear}
     busy={busy}
   />

   <Metrics
     inputLen={inputLen}
     outputLen={outputLen}
     ratio={ratio}
     timeMs={timeMs}
   />

      <StatusBar status={status} kind={statusKind} />
    </div>
  );
}
