# Milicia Golf Tour — Contexto del Proyecto

**Leer este archivo antes de cualquier tarea sobre este proyecto.** Acá están las reglas, datos canónicos y convenciones. No asumir conocimiento general de golf ni de cómo "debería" estructurarse — seguir lo que dice este doc.

---

## 1. QUÉ ES EL PROYECTO

Webapp single-file (`index.html`) que administra el torneo anual **Milicia Golf Tour**: 10 fechas, 16 jugadores oficiales divididos en 2 equipos (Gris vs Rojo). Datos viven en Supabase + localStorage; archivos Excel históricos (`RESUMEN de Resultados YYYY.xlsx`) son la fuente original para 2016-2025.

### ⚠️ Dos competencias separadas — NO mezclar

1. **Medal** → ranking **individual** de los 16 jugadores. Cada fecha asigna pts por puesto (500/300/200/...). El equipo (Gris/Rojo) en este ranking es solo metadata informativa. **NO existe "ganador medal por equipo"**.

2. **Match Play** → competencia entre **equipos** Gris vs Rojo. Los pts entre equipos **solo** se acumulan por los matchs jugados cada fecha (1v1 individuales o 2v2 fourball). Cada match da 1 pt al equipo ganador o 0.5 en empate. **El medal no aporta NADA al match entre equipos**.

Cuando se reporta "estado del torneo" o "líder", siempre aclarar de qué competencia se habla. No combinar pts medal con team match pts.

Desplegado en GitHub Pages desde repo `DevelopFB/MiliciaGolfTour`.

---

## 2. JUGADORES — LISTA CANÓNICA (NO CONFUNDIR)

**Formato display siempre `"Apellido, Nombre"` con acentos correctos.** Coincide con las tarjetas/scorecards que llegan por foto.

### Oficiales del Tour 2026 (16)

**Regla de naming**: en **todos los reportes, dashboards, exports y PDFs** se usa siempre el **nombre completo** (`Apellido, NombreCompleto`). Los sobrenombres están solo para **matching de entrada** (cuando se pega texto/info del usuario que usa el sobrenombre).

| ID interno | Nombre completo (display) | Sobrenombre | Equipo |
|---|---|---|---|
| `gonzalez` | Gonzalez, Agustín | Agus | Gris |
| `tarasido` | Tarasido, Gonzalo | Gonzalo | Gris |
| `zunino` | Zunino, Javier | Javi | Gris |
| `basaldua` | Basaldua, Ignacio | Ignacio | Gris |
| `pannullo` | Pannullo, Martín | Tincho | Gris |
| `benegas` | Benegas, Francisco | Pancho | Gris |
| `guevara` | Guevara, Francisco | Franki | Gris |
| `dipaola` | Dipaola, Martín | Dipa | Gris |
| `gatto` | **Gatto, Mariano** | Gattait | Rojo |
| `elizalde` | Elizalde, Juan Pedro | Juancho | Rojo |
| `canonico` | Canónico, Agustín | Agus | Rojo |
| `vogelius` | Vogelius, Nicolás | Nico | Rojo |
| `mendez` | Méndez, Gastón | Pato | Rojo |
| `molinario` | Molinario, Andrés | Andy | Rojo |
| `scapparone` | Scapparone, Nicolás | Nico | Rojo |
| `fernandez` | Fernandez, Lucas | Lule | Rojo |

> **Nota Hdcp**: el hdcp de cada jugador es **dinámico** y cambia de fecha a fecha según evolución. Se lee de la tarjeta del día. Lo que figura en `PLAYERS[].hdc` del `index.html` son valores semilla (default) usados solo si no hay tarjeta cargada todavía; se sobrescriben al cargar cada fecha.

### Suplente Oficial (única excepción permitida en match)

| ID | Nombre completo | Sobrenombre | Notas |
|---|---|---|---|
| `gatto_ale` | **Gatto, Alejandro** | Ale | Suplente oficial especial. Acumula pts de match para el equipo que representa cuando entra. Hdcp también dinámico por tarjeta. |

### Jugadores históricos / no activos (no se ven en la web)

| ID | Display | Notas |
|---|---|---|
| `hector_gatto` | **Gatto, Hector** | Histórico. NO es activo. Datos sólo en JSON para completitud. |
| `basaldua_javi` | Basaldua, Javier | Hermano de Ignacio. Histórico. |
| `vigil` | Vigil, Tomas | Histórico. |
| `miceli` | Miceli, Julian | Histórico. |
| `alfonso` | Alfonso, Juani | Histórico. |
| `uribelarrea` | Uribelarrea, _ | Histórico (typo Uribellarea en algunos Excel). |

### ⚠️ Tres Gatto distintos — NUNCA mezclar

- **Gatto, Mariano** (`gatto`) → Oficial actual, equipo Rojo, jugador del tour.
- **Gatto, Alejandro** (`gatto_ale`) → Suplente oficial especial. NO es Mariano.
- **Gatto, Hector** (`hector_gatto`) → Histórico, no juega más.

Si en un Excel viejo ves "Gatto" sin primer nombre, mirá la fila completa o pregunta antes de asumir.

---

## 3. GOLF — CONCEPTOS BÁSICOS

### Par y cancha

- El **par** es **específico de cada hoyo**, no un número fijo. Cada hoyo tiene par 3, 4 ó 5.
- Cancha default CUBA Fátima 2026: `[5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5]` → front 36 + back 36 = **72 par total**.
- **Cada fecha tiene su propio `cancha` y `par[18]`**: cuando se juega en otra cancha (gira, otro club), se carga el par real al armar la fecha. La webapp tiene la cancha editable inline desde el detalle de fecha (botón ✏️) y el par editable desde el grid del backoffice.
- En reportes/charts: si se comparan varias fechas en distintas canchas, el par mostrado es **promedio por hoyo** entre canchas. Con 1 sola fecha → par exacto de esa cancha.
- Siempre verificar el par contra la tarjeta del día.

### Tipos de score (relativo al par del hoyo)

| Score | Nombre |
|---|---|
| par − 3 | Albatros |
| par − 2 | **Eagle** |
| par − 1 | **Birdie** |
| par     | **Par** |
| par + 1 | **Bogey** (Boggie en lenguaje local) |
| par + 2 | **Doble Bogey** (Doble Boggie) |
| par + 3 o más | **Más de Doble Bogey** |

### Gross / Hdcp / Neto

- **Gross**: suma cruda de strokes de los 18 hoyos.
- **Hdcp Index** (handicap): el handicap del jugador. **CAP a 26** para todos los cálculos del tour. Si el index real es 28, se usa 26.
- **Neto**: `Gross − Hdcp aplicado`. Define el ranking de Medal y de fecha.

---

## 4. REGLAS DEL TOUR

### Calendario
- **10 fechas por temporada** (típicamente Mar-Nov).
- **F1-F8**: medal + match en cancha propia (CUBA Fátima u otra).
- **F9**: gira (multiplicador medal **×1.5**), modalidad fourball inverso (1v8, 2v7, ...).
- **F10**: gira FINAL (multiplicador medal **×2**), individual #1 Gris vs #1 Rojo.

### Equipos
- **Gris vs Rojo**, 8 vs 8.
- Cada jugador tiene equipo fijo (ver tabla arriba).
- Match Play acumula pts por equipo a lo largo del año.

### Sistema de puntos Medal (individual)

Tabla por puesto:
```
1ro → 500     6to → 100
2do → 300     7mo → 90
3ro → 200     8vo → 80
4to → 150     9no → 75
5to → 120     10mo → 70
11mo a 14to → 20
15to a 16to → 0
```

Multiplicador F9 = ×1.5, F10 = ×2 (sobre los puntos base).

### Ranking de pts medal — TODOS los que jugaron ocupan puesto

- Las posiciones se asignan ordenando por neto a **todos los que jugaron** (oficiales + suplentes + invitados). Los suplentes **ocupan puestos** y reciben su parte de los pts si hay empate.
- En el resumen de fecha se muestran los pts del suplente entre paréntesis (visual).
- Pero los suplentes **NO acumulan** al tour: filtrado posterior en `buildAccum` por `esSuplente`.
- **Esto importa**: si un suplente está delante de un oficial, los oficiales reciben los pts de su posición REAL (que incluye al suplente). NO se "saltan" suplentes para premiar al oficial siguiente.

**Ejemplo 1** — Suplente solo en pos 1:
- Sup neto 70 → pos 1 → "se lleva" 500 pts (visual)
- Oficial neto 72 → pos 2 → 300 pts (NO 500)

**Ejemplo 2** — Suplente + Oficial empatados en pos 1:
- Ambos neto 70 → comparten pos 1-2 → `(500+300)/2 = 400` pts cada uno
- Oficial acumula 400 al tour; suplente muestra 400 visual

**Ejemplo 3** — Suplente + 2 Oficiales empatados en pos 10:
- 3 jugadores neto 80 → comparten pos 10-11-12 → `(70+20+20)/3 = 36.67` pts cada uno
- Los 2 oficiales acumulan ~37 al tour

### Empates entre oficiales
- Para **fechas ganadas (stats)**: todos los oficiales empatados en pos 1 (neto mínimo) suman +1 fecha ganada.

### Premio Gross — mejor promedio bruto

- Ranking paralelo al medal, basado en **gross** (no neto).
- Premio se calcula con el **promedio de las mejores 7 tarjetas** del año por jugador (`avgBestN`, BEST_N = 7).
- Si un jugador jugó menos de 7 fechas, queda como "falta N tarjetas" sin posibilidad de premio.
- Suplentes (incluido Gatto Alejandro) **no compiten** por el premio gross, aunque aparezcan integrados en el ranking visualmente para referencia.
- Mejor tarjeta individual del año se trackea aparte por jugador (marcada con ★).

### Fecha vacante
- Si **NINGÚN oficial** está en el neto mínimo de la fecha → fecha **vacante**: nadie suma fecha ganada.
- Si al menos UN oficial empata el neto mínimo (aunque haya suplentes también empatados ahí) → ese/esos oficiales SÍ ganan la fecha.
- **Excepción**: el suplente oficial especial (`gatto_ale`) puede ocupar pos 1 sin invalidarla — pero el oficial que esté empatado con él gana normalmente.

### Sustitutos (no oficiales) — Regla 2026

- Si un oficial no puede jugar una fecha, puede entrar un suplente externo en su lugar.
- **El suplente suma pts para el COLOR (equipo) que representa**, igual que un oficial. El resultado del match cuenta normalmente para Gris o Rojo.
- El suplente NO acumula medal individual personal para el tour.
- El oficial al que reemplaza tampoco recibe esos pts (jugó otro).
- **Excepción**: el suplente oficial especial (Gatto, Alejandro) acumula stats individuales en un cuadro separado (no compite con los 16 oficiales en el ranking principal pero sí tiene su propio totalizador).
- **Vacante del medal**: si el ganador de la fecha (neto mínimo) es un suplente, la fecha queda vacante para el medal individual y ningún oficial suma fecha ganada.

**Regla histórica (años anteriores a 2026)**: los pts de equipo con suplente se ajustaban (1v1: nadie suma si gana sup; 2v2: pts a la mitad). **Eliminado en 2026.**

### Marca `(*)` en Excel viejos
- En los Excel `RESUMEN de Resultados YYYY.xlsx`, algunos nombres aparecen con `(*)`.
- **NO significa invitado.** Significa "La Comisión" (Elizalde, Benegas, Guevara — los que administran).
- **No tiene efecto práctico en cálculos.** Tratar como oficial normal.

---

## 5. ESTRUCTURA DE DATOS

### `fechas[]` (array en index.html, sincronizado con Supabase tabla `fechas`)

```js
{
  num: 4,
  fecha: '06 Jun 2026',
  pendiente: false,
  cancha: 'CUBA Fátima',
  par: [5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5],
  organizadores: 'Pannullo + Basaldua',
  modalidad: 'Fourball 2v2',
  scorecard: [
    {id:'benegas', hdcp:21, hoyos:[5,4,4,6,5,5,3,5,5, 4,6,5,5,4,5,5,4,6], gross:91, neto:70},
    // ...
  ],
  medal: [ /* idem scorecard pero con pos/pts calculados */ ],
  matchs: [
    {tipo:'fb'|'ind', g:['benegas','guevara'], r:['canonico','elizalde'], hoyos_g:5, hoyos_r:3, ganador:'g', dif:2},
  ],
  suplentes: [{id:'externo1', name:'Pepe', team:'g'}],
  comentario: 'texto del recap',
}
```

### `jugadores_historico.json` (fuente de verdad histórica)

```json
{
  "_version": "2026-04-14-rebuild-v1",
  "players": {
    "benegas": {
      "nombre": "Benegas, Pancho",
      "foto": null,
      "años": {
        "2024": {
          "fechasJugadas": 10,
          "fechasGanadas": 1,
          "mejorPosicion": 1,
          "avgGross": 99.0,
          "avgNeto": 77.0,
          "posicionFinal": null
        }
      }
    }
  },
  "tourTotals": {
    "2024": {"avgGross": 95.0, "avgNeto": 72.5, "totalJugadores": 22}
  }
}
```

Cambiar `_version` cada vez que se actualiza para forzar re-sync en clientes.

### Tablas Supabase

| Tabla | Uso |
|---|---|
| `fechas` | scorecard + matchs + medal + recaudación de cada fecha (clave `num`) |
| `jugadores_historico` | foto + años por jugador (clave `id`) |
| `fixture` | fecha/modalidad/criterio/organizadores editables (clave `num`) |
| `recaudacion` | aportes pendientes (legacy, puede integrarse en `fechas`) |

---

## 6. CONVENCIONES DE CÓDIGO Y DATOS

### IDs internos
- Minúsculas, sin acentos, sin espacios, formato `apellido` o `apellido_primernombre` si hay ambigüedad.
- Los 3 Gatto: `gatto` (Mariano), `gatto_ale` (Alejandro), `hector_gatto` (Hector).
- **Recomendación futura**: migrar a `gatto_mariano` / `gatto_alejandro` / `gatto_hector` para máxima claridad (requiere migración de datos en Supabase y archivos).

### Parsing de Excels históricos
- Las hojas `FechaN` (2017-2025) tienen columnas: `Posición | Nombre | GROSS | HDC | NETO | PUNTOS`.
- 2016 es excepción: hojas `F4`-`F7` con formato distinto + tablas agregadas en hoja `F7` (POSICIONES, PUNTOS). NO tiene columna NETO.
- Nombres en Excel pueden tener: `(*)` (comisión, ignorar), `(invitado)` o `(Invitado)` (no-oficial real), variantes ortográficas (acentos, typos como `Uribellarea`).
- Mapeo de nombres → ID: por apellido + primer nombre. Aliases manuales necesarios para `Julian → miceli`, `Juani Alonso → alfonso`, `Tomi Vigil → vigil`, etc.

### Web — flujo de datos
1. Al cargar: fetch `./jugadores_historico.json` del repo → fuente de verdad.
2. Si `_version` cambió: pisa localStorage + sincroniza a Supabase.
3. Filtrado en UI: sólo se muestran los 16 oficiales + `gatto_ale`. Históricos no aparecen.

### Fórmula de pos en Medal (calcMedalPts)
1. Filtrar suplentes y no-oficiales.
2. Ordenar oficiales por neto ascendente.
3. Asignar pos por grupos de empate (todos los netos iguales comparten pos).
4. Pts = `Round((Σ pts_puestos_ocupados) / cantidad_empatados) × multiplicador`.
5. Aplicar regla de vacante: si neto min absoluto (incl. suplentes) lo tiene un suplente/no-oficial y ningún oficial empata con él → fecha vacante.

---

## 7. EXCEL MAESTRO (PLANEADO, NO IMPLEMENTADO AÚN)

Archivo `MGT_Master.xlsx` que será fuente única de verdad. Hojas previstas:

1. **Setup** — jugadores, hdcps, equipo, tabla de pts por puesto, cap hdcp = 26.
2. **Canchas** — par por hoyo para cada cancha usada.
3. **F1**…**F10** — una hoja por fecha. Por jugador, 2 filas:
   - Fila 1: score por hoyo (1-18).
   - Fila 2: diferencial vs par del hoyo (fórmula). Con formato condicional por color (eagle/birdie/par/bogey/+).
   - Cols finales: Total Gross | Hdcp Index | Hdcp aplicado (MIN(idx, 26)) | Neto | Pos | Pts Medal.
   - Sección Match: enfrentamientos, ganador, dif hoyos, pts equipo, color.
   - Marca "Vacante" automática si pos 1 es no-oficial.
4. **Match_Historico** — una fila por enfrentamiento, todas las fechas.
5. **Consolidado** — pivots para el dashboard.
6. **Dashboard** — selector Acumulado / Fecha N, KPIs, tablas filtradas.

La idea: cargar fecha = sólo llenar scores por hoyo. Todo lo demás se calcula con fórmulas.

---

## 8. CHECKLIST AL EDITAR EL PROYECTO

- [ ] ¿Mencioné a "Gatto" sin especificar Mariano/Alejandro/Hector? Aclarar.
- [ ] ¿Usé "par 4" como genérico? Usar el par del hoyo específico.
- [ ] ¿El neto mínimo de una fecha lo tiene un no-oficial? Aplicar vacante.
- [ ] ¿Hay empates en una posición? Repartir puntos.
- [ ] ¿Cambié el JSON histórico? Actualizar `_version`.
- [ ] ¿Cambié display names? Mantener formato `"Apellido, Nombre"`.

---

## 9. HISTORIAL DE DECISIONES IMPORTANTES

- **2026-04-14**: Rebuild completo del JSON histórico desde hojas Fecha de cada Excel (2017-2025). 2016 procesado aparte por formato distinto.
- **2026-04-14**: Confirmado que `(*)` = La Comisión, no invitado. Aliases nuevos: Julian→Miceli, Juani Alonso→Alfonso. Altas: Basaldua Javi, Tomas Vigil.
- **2026-04-14**: Fixture sincronizado via tabla Supabase `fixture`.
- **2026-04-14**: JSON del repo como fuente de verdad con versionado (`_version` field).
