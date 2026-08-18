# PROMPT_CARGA_FECHA — Procesamiento de una fecha del MGT (v3 — Jul 2026)

**Cómo se usa**: en un chat nuevo del proyecto, pegar el mini-prompt de abajo con los datos de la fecha + las screenshots de las tarjetas (shagolf.com.ar o golf.cuba.org.ar). Claude devuelve los 4 outputs. Diseñado para funcionar desde el teléfono (solo chat, sin Cowork).

---

## ▶️ PRÓXIMA FECHA — F7 (listo para copiar)

```
Fecha 7 MGT — 12/09/2026 — CUBA Fátima — Fourball 2v2
Organizadores: Scapparone + Benegas
Ausentes: [lista o "ninguno"]
Suplentes: [Nombre completo, equipo, a quién reemplaza — o "ninguno"]
Matchs y resultados: [los paso acá o al final]

Te adjunto las tarjetas. Seguí PROMPT_CARGA_FECHA.md y devolveme los 4 outputs.
```

Contexto que trae la F7: Medal líder Elizalde 1220 · Copa Match Play **Gris 17.5 – Rojo 14.5**
(tablero: Gris +3 pts, dif hoyos +3) · Fourball 2v2 aleatorio → 4 matchs.
Par CUBA Fátima `[5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5]` = 72.

---

## 📱 MINI-PROMPT (copiar, completar y pegar con las tarjetas)

```
Fecha [N] MGT — [DD/MM/AAAA] — [Cancha] — [Individual 1v1 / Fourball 2v2]
Organizadores: [Apellido + Apellido]
Ausentes: [lista o "ninguno"]
Suplentes: [Nombre completo, equipo, a quién reemplaza — o "ninguno"]
Matchs y resultados: [los paso acá o al final]

Te adjunto las tarjetas. Seguí PROMPT_CARGA_FECHA.md y devolveme los 4 outputs.
```

---

## EXTRACCIÓN (reglas para Claude)

De cada tarjeta:

- Nombre → mapear al ID canónico de `CLAUDE.md`. Display siempre `"Apellido, Nombre"` completo.
- Hdcp del día (campo HCP de la tarjeta, sin cap ni redondeo).
- Score por hoyo (18 valores) + par por hoyo (18 valores, igual en todas las tarjetas de la fecha).
- Gross = suma de los 18 hoyos. Si no coincide con el total impreso → ⚠️ mostrar ambos.
- Neto = Gross − min(hdcp_día, 26).

Obligatorio:

- "Gatto" sin primer nombre → preguntar (Mariano `gatto` / Alejandro `gatto_ale` / Hector `hector_gatto`).
- Cancha ≠ CUBA Fátima → leer el par de la tarjeta, NO asumir.
- Hoyo ilegible → `null` + avisar en discrepancias. No inventar.
- Jugador que jugó match pero sin tarjeta → incluir en scorecard con `hdcp/hoyos/gross/neto: null`.
- Jugador ausente → NO incluir en scorecard.
- Nombre no reconocido → `"_unknown"` + avisar.
- NO calcular pts medal ni vacante (lo hace el backoffice). NO inventar matchs (los pasa el usuario).

---

## 📤 LOS 4 OUTPUTS (en este orden, siempre)

### 1️⃣ RESUMEN EJECUTIVO (texto plano)

```
FECHA N — DD-MM-AAAA — CANCHA
Modalidad · Organizadores · Par total
Jugadores: N oficiales + N suplentes

🏆 PODIO MEDAL (por neto, con empates)
🎯 Ganador de fecha: [nombre] ó VACANTE
🏌️ Mejor Gross / 📈 Peor Gross
🦅 Stats: eagles, birdies, pares, bogeys, dobles+ · avg gross · avg neto
⚔️ MATCH PLAY: resultado por match + total Gris vs Rojo + dif hoyos
📝 Narrativa 3-5 oraciones (rioplatense, nombres completos)
⚠️ Discrepancias: [lista o "ninguna"]
```

### 2️⃣ JSON PARA BACKOFFICE

Un solo bloque ```json``` listo para pegar en "📋 Pegar JSON" del backoffice:

```json
{
  "num": 5,
  "fecha": "04 Jul 2026",
  "cancha": "CUBA Fátima",
  "par": [5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5],
  "organizadores": "Benegas + Guevara",
  "comentario": "Misma narrativa del resumen.",
  "medal": [],
  "scorecard": [
    {"id": "benegas", "hdcp": 21, "hoyos": [6,4,4,6,5,5,3,5,5, 4,6,5,5,4,5,5,4,6], "gross": 91, "neto": 70},
    {"id": "gonzalez", "hdcp": null, "hoyos": null, "gross": null, "neto": null}
  ],
  "suplentes": [
    {"id": "gatto_ale", "name": "Gatto, Alejandro", "equipo": "g", "reemplaza": "zunino"},
    {"id": "sup_alfonso", "name": "Alfonso, Juan Ignacio", "equipo": "r", "reemplaza": "scapparone"}
  ],
  "matchs": [
    {"tipo": "ind", "gris": ["benegas"], "rojo": ["elizalde"], "ganador": "r", "difHoyos": 2},
    {"tipo": "fb", "gris": ["pannullo","benegas"], "rojo": ["molinario","mendez"], "ganador": "g", "difHoyos": 3}
  ]
}
```

Reglas del JSON:

- `fecha`: `"DD MMM AAAA"` en español. `organizadores`: string `"Apellido + Apellido"`.
- `medal`: **incluir siempre**, vacío `[]` (el backoffice lo calcula; el validador lo exige presente).
- `hdcp`: el del día, sin cap. `neto` sí va con cap aplicado (gross − min(hdcp,26)).
- `suplentes[].id`: `gatto_ale` para el oficial; externos `sup_apellido` (minúsculas, sin acentos). `equipo`/`ganador`: `"g"` / `"r"` (o `"empate"` en ganador).
- `difHoyos`: entero **positivo** — el campo `ganador` define el signo.
- Match 2v1 por ausencia → completar la dupla con `"sin_suplente"`.
- NO incluir `pts_g`, `pts_r`, `stats`, `medal_pos`.

### 3️⃣ TSV PARA EXCEL MASTER (excel-first)

Bloque tabular para la hoja `F[N]` del `MGT_2026_Master.xlsx`. **Dos sub-bloques** (para no pisar las columnas de fórmulas U/W/X):

**Bloque A — pegar en `A8` (Jugador → H18, columnas A:T):**
```
Jugador	Equipo	H1	H2	…	H18
Gatto, Mariano	ROJO	4	3	…	5
```
- Orden: los 8 Gris primero, después los 8 Rojo, suplentes al final (mismo orden que hojas F1–F3).
- Jugador sin tarjeta: fila con nombre y equipo, hoyos vacíos.

**Bloque B — pegar en `V8` (hdcp del día, columna V, mismo orden de filas):**
```
21
11
…
```

- Gross (U), Hdcp aplic (W) y Neto (X) son fórmulas de la hoja: no incluirlos.
- Si la cancha no es Fátima: agregar una línea aparte con el par por hoyo para pegar en `C6:T6` y el stroke index en `C5:T5`.

### 4️⃣ HTML DEL PDF

`F[N]_PDF_REPORT.html` standalone (styles inline, Playfair Display + DM Sans, paleta navy + dorado): podio, ranking de la fecha, stats, match play, narrativa. 1-2 páginas A4 → abrir en navegador y Cmd/Ctrl+P → PDF.

---

## ⚠️ IMPORTANTE

- No inventar datos. Dudas → preguntar antes de generar los outputs.
- El JSON del output 2 es la **fuente única** para el update del Master el lunes (Cowork lee este JSON y reconstruye la hoja F[N] con fórmulas). Guardarlo.
- No mezclar Medal (individual) con Match Play (equipos) en el resumen.

---

## ✅ DESPUÉS DE PEGAR EL JSON — verificar que se publicó

Este paso no es opcional: en la F6 la fecha estuvo 10 días cargada pero sin publicar.

1. Backoffice → **📋 Pegar JSON** → revisar el grid → **Guardar**.
2. **Refrescar la página.**
   - Sin banner amarillo → ✅ publicado.
   - Banner **"⚠ Sin publicar"** → quedó solo en ese navegador. Tocar **"Publicar ahora"**;
     si pide el token, cargarlo en **Admin → 🔑 Publicación** y repetir.
3. Si querés estar seguro: abrir la web en **incógnito**. Lo que se ve ahí es lo que está publicado.

> Por qué pasa: sin token, `repoSaveJson` falla y el cambio queda en localStorage. La web mergea
> lo del repo con lo local y **nunca borra**, así que se ve idéntica a una fecha publicada.

## 📋 Cierre de la fecha

- **Multas**: USD 12 por oficial ausente, con o sin suplente. El que jugó el match pero no entregó
  tarjeta NO es ausente. Se guardan en `data/recaudacion.json`. La fecha no está cerrada sin esto.
- **Lunes en Cowork**: *"Actualizá el Master con la FN, el JSON está en el chat de la fecha"* →
  hoja FN, columnas en Match / Gross_Historial / Medal_Fechas / Medal_Consolidado, Fixture,
  `ESTADO_2026.md` regenerado y `git push`. Procedimiento completo en
  `COCKPITS/MGT/core/runbook-fecha.md`.
