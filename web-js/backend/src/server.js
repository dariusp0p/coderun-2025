import http from "http";
import { readJson, sendJson } from "./utils/json.js";
import { setCors } from "./utils/cors.js";
import { compress } from "./rle/compress.js";
import { decompress } from "./rle/decompress.js";

const server = http.createServer(async (req, res) => {
  setCors(res);

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    return res.end();
  }

  if (req.url === "/api/compress" && req.method === "POST") {
    try {
      const { text = "" } = await readJson(req);
      const start = process.hrtime.bigint();
      const result = compress(String(text));
      const end = process.hrtime.bigint();

      const inputLength = Array.from(String(text)).length;
      const outputLength = Array.from(result).length;

      return sendJson(res, 200, {
        result,
        inputLength,
        outputLength,
        ratio: inputLength ? outputLength / inputLength : 0,
        timeMs: Number(end - start) / 1e6,
        status: "ok"
      });
    } catch (e) {
      return sendJson(res, 400, { error: e.message, status: "error" });
    }
  }

  if (req.url === "/api/decompress" && req.method === "POST") {
    try {
      const { text = "" } = await readJson(req);
      const start = process.hrtime.bigint();
      const result = decompress(String(text));
      const end = process.hrtime.bigint();

      const inputLength = Array.from(String(text)).length;
      const outputLength = Array.from(result).length;

      return sendJson(res, 200, {
        result,
        inputLength,
        outputLength,
        ratio: inputLength ? outputLength / inputLength : 0,
        timeMs: Number(end - start) / 1e6,
        status: "ok"
      });
    } catch (e) {
      return sendJson(res, 400, { error: e.message, status: "error" });
    }
  }

  sendJson(res, 404, { error: "Not found" });
});

server.listen(8000, () => {
  console.log("RLE backend running on http://localhost:8000");
});
