# Prompt — Extracción de Tarjetas (Carga de Fecha)

**Cómo usarlo**: copiá este prompt completo en un nuevo chat del proyecto "La Milicia", pegá las N tarjetas (screenshots o fotos) en el mismo mensaje, y Claude devolverá los 3 outputs listos para usar.

---

## 📋 PROMPT (copiar desde acá ↓)

Antes de responder, leé el archivo `CLAUDE.md` del proyecto para contexto completo (jugadores canónicos, reglas, formato).

Te paso las tarjetas (screenshots / fotos) de **Fecha [N]** del Milicia Golf Tour, jugada el **[DD/MM/AAAA]**. Cancha: **[NOMBRE CANCHA]** (par a confirmar viendo las tarjetas).

Hay [N] jugadores oficiales + [N] suplentes (si aplica).

Extraé de cada tarjeta:
- Nombre del jugador → mapear al ID canónico de `CLAUDE.md` (formato `"Apellido, Nombre"`).
- Hdcp del día (el que figura en la tarjeta — antes del cap del tour).
- Gross total (suma de los 18 hoyos).
- Neto total.
- Score por hoyo (18 valores).
- Par por hoyo (18 valores) — sale de la tarjeta también. Tiene que ser el mismo para todas las tarjetas de esa fecha.

**Reglas obligatorias**:
- Si ves "Gatto" sin primer nombre, pediime aclaración. Hay 3 Gatto distintos (Mariano = `gatto`, Alejandro = `gatto_ale`, Hector = `hector_gatto`).
- El gross debe coincidir con la suma de los 18 hoyos. Si no coincide, marcá ⚠️ y mostrá ambos valores.
- Neto = Gross − Hdcp del día (sin cap todavía). Si tampoco coincide, marcá ⚠️.
- Hdcp aplicado al tour = `min(hdcp_día, 26)` — esto lo calcula el backoffice, no lo apliques vos.
- Si un jugador no figura en la lista canónica de `CLAUDE.md`, marcalo como `"_unknown"` y avisame en el resumen.

---

## 📤 OUTPUTS — devolveme estos 3 bloques exactos, en este orden

### 1. RESUMEN EJECUTIVO

Texto plano corto:
```
Fecha [N] — [DD/MM/AAAA] — [Cancha]
Par total: [N]
Jugadores: [N] oficiales [+ N suplentes]

Top 5 Neto:
1° [Apellido, Nombre] — Neto [N] (Gross [N] / Hcp [N])
2° ...

Ganador de fecha: [Apellido, Nombre]   ó   VACANTE (si ganó suplente/no-oficial)

Mejor Gross: [Apellido, Nombre] — [N]
Eagles: [N]   Birdies: [N]
Discrepancias: [lista si hubo, sino "ninguna"]
Tarjetas no reconocidas: [lista si hubo]
```

### 2. JSON PARA BACKOFFICE

Bloque JSON listo para pegar en el campo de admin de la web. Estructura exacta:

```json
{
  "num": 0,
  "fecha": "DD MMM AAAA",
  "cancha": "...",
  "par": [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0],
  "par_total": 0,
  "scorecard": [
    {
      "id": "...",
      "name": "Apellido, Nombre",
      "hdcp": 0,
      "hoyos": [0,0,0,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0],
      "gross": 0,
      "neto": 0
    }
  ]
}
```

- `fecha`: formato `"DD MMM AAAA"` en español ("10 May 2026").
- `par`: 18 enteros.
- `hoyos`: 18 enteros por jugador.
- `hdcp`: el del día, sin redondear ni capear.
- No incluyas `medal`, `matchs`, `suplentes` ni `comentario` — esos los carga el usuario manualmente en el backoffice.

### 3. FILAS PARA EXCEL MASTER

Bloque tabular pegable en la hoja `F[N]` del Excel maestro. 2 filas por jugador (score + diff vs par) más el header. Formato TSV (tab-separated) para pegar directo en Excel:

```
Jugador	Hcp	H1	H2	H3	H4	H5	H6	H7	H8	H9	OUT	H10	H11	H12	H13	H14	H15	H16	H17	H18	IN	Gross	Neto
Par		[par H1]	[par H2]	...			...		[par_out]	...			...		[par_in]	[par_total]
Apellido, Nombre	[hcp]	[score1]	...		[out]		...		[in]	[gross]	[neto]
(repetir por jugador)
```

(En el Excel master las fórmulas calculan diff vs par automáticamente; el TSV solo necesita scores.)

---

## ⚠️ IMPORTANTE

- **No inventes datos.** Si una tarjeta es borrosa o falta un hoyo, marcalo con `null` y avisá en el resumen.
- **No apliques reglas de tour** (pts medal, vacante, etc.). Eso lo hace el backoffice. Tu único trabajo acá es extraer datos crudos correctamente.
- **No proceses los matchs.** Los carga el usuario aparte (sabe quién jugó con quién).

(fin del prompt ↑)
