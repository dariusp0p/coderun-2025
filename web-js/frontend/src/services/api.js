const BASE = "http://localhost:8000";

export async function compressRemote(text) {
  const res = await fetch(`${BASE}/api/compress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Error during compression (server).");
  const data = await res.json();
  return data.result;
}

export async function decompressRemote(text) {
  const res = await fetch(`${BASE}/api/decompress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Error during decompression (server).");
  const data = await res.json();
  return data.result;
}
