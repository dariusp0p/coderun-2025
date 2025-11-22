## Documentatie Backend
## Descriere

Serverul este realizat in Node.js utilizand doar `http`.

Backend-ul expune doua endpoint-uri HTTP de tip POST, folosite de interfata React.

---

## Structura proiectului backend

```
backend/
  src/
    rle/
      compress.js       - functia de compresie
      decompress.js     - functia de decompresie
      segment.js        - segmentarea corecta a textului (suport emoji/Unicode)
    utils/
      cors.js           - configurare antete CORS
      json.js           - utilitare pentru parsare si trimitere JSON
    server.js           - serverul HTTP si routarea cererilor
  package.json
```

---

## Pornirea serverului

In folderul `backend`:

```
pnpm install
pnpm dev
```

Serverul ruleaza pe:

```
http://localhost:8000
```

---

## Endpoint-uri HTTP

### POST `/api/compress`

Primeste text brut si intoarce varianta comprimata.

**Request JSON:**

```json
{
  "text": "aaabbc"
}
```

**Response JSON:**

```json
{
  "result": "a3b2c1",
  "inputLength": 6,
  "outputLength": 6,
  "ratio": 1,
  "timeMs": 0.25,
  "status": "ok"
}
```

**Erori:**

```json
{ "error": "Invalid JSON", "status": "error" }
```

---

### POST `/api/decompress`

Primeste text in format RLE si intoarce textul decomprimat.

**Request JSON:**

```json
{
  "text": "a3b2c1"
}
```

**Response JSON:**

```json
{
  "result": "aaabbc",
  "inputLength": 6,
  "outputLength": 6,
  "ratio": 1,
  "timeMs": 0.17,
  "status": "ok"
}
```

**Erori:**

```json
{ "error": "Format invalid: missing count", "status": "error" }
```

---

## Implementare RLE

### Segmentarea textului

Pentru suport complet Unicode, se foloseste:

```
Intl.Segmenter("en", { granularity: "grapheme" })
```

### Compresie

Parcurge textul, numara caracterele consecutive si genereaza perechi de forma:

```
<caracter><numar>
```

Exemplu: `aaaabb` → `a4b2`.

### Decompresie

Reconstruieste textul extinzand fiecare pereche caracter-numar.

Exemplu: `a4b2` → `aaaabb`.

---

## CORS

Frontend-ul ruleaza pe portul 5173, iar backend-ul pe portul 8000.

## Documentatie Frontend

## Componente principale

### TextAreas.jsx
- Afiseaza doua zone de text:
  - *Input*: Pentru introducerea textului manual sau prin incarcarea unui fisier.
  - *Output*: Afiseaza rezultatul procesarii (doar citire).

### FileDropZone.jsx
- Permite incarcarea fisierelor .txt prin drag-and-drop sau click.

### Controls.jsx
- Afiseaza butoane pentru:
  - *Compress*: Comprimarea textului introdus.
  - *Decompress*: Decomprimarea textului introdus.
  - *Clear*: Stergerea tuturor datelor.

### Metrics.jsx
- Afiseaza:
  - Lungimea textului de intrare.
  - Lungimea textului de iesire.
  - Raportul de compresie.
  - Timpul de executie.

### StatusBar.jsx
- Afiseaza mesaje de stare in functie de rezultatul operatiunilor.

---

## Servicii

### api.js
- Functii pentru comunicarea cu backend-ul:
  - compressRemote(text): Trimite textul catre server pentru comprimare.
  - decompressRemote(text): Trimite textul catre server pentru decomprimare.

---

## Pornire

In folderul `frontend`:

```
pnpm install
pnpm dev
```

## Note

- Aplicatia functioneaza doar cu fisiere .txt.
- Asigura-te ca serverul backend este pornit inainte de a utiliza aplicatia.