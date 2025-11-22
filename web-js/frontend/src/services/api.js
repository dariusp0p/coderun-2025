const BASE = "http://localhost:8000"; // schimbă după backend-ul vostru

export async function compressRemote(text) {
  const res = await fetch(`${BASE}/compress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Eroare la compresie (server).");
  return (await res.json()).result;
}

export async function decompressRemote(text) {
  const res = await fetch(`${BASE}/decompress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text }),
  });
  if (!res.ok) throw new Error("Eroare la decompresie (server).");
  return (await res.json()).result;
}
