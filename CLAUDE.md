# Milicia Golf Tour — Contexto del Proyecto

**Leer este archivo antes de cualquier tarea sobre este proyecto.** Acá están las reglas, datos canónicos y convenciones. No asumir conocimiento general de golf ni de cómo "debería" estructurarse — seguir lo que dice este doc.

---

## 1. QUÉ ES EL PROYECTO

Webapp single-file (`index.html`) que administra el torneo anual **Milicia Golf Tour**: 10 fechas, 16 jugadores oficiales divididos en 2 equipos (Gris vs Rojo), competencias paralelas Medal (individual) y Match Play (equipos). Datos viven en Supabase + localStorage; archivos Excel históricos (`RESUMEN de Resultados YYYY.xlsx`) son la fuente original para 2016-2025.

Desplegado en GitHub Pages desde repo `DevelopFB/MiliciaGolfTour`.

---

## 2. JUGADORES — LISTA CANÓNICA (NO CONFUNDIR)

**Formato display siempre `"Apellido, Nombre"` con acentos correctos.** Coincide con las tarjetas/scorecards que llegan por foto.

### Oficiales del Tour 2026 (16)

| ID interno | Display | Equipo |
|---|---|---|
| `gonzalez` | Gonzalez, Agus | Gris |
| `tarasido` | Tarasido, Gonzalo | Gris |
| `zunino` | Zunino, Javi | Gris |
| `basaldua` | Basaldua, Ignacio | Gris |
| `pannullo` | Pannullo, Tincho | Gris |
| `benegas` | Benegas, Pancho | Gris |
| `guevara` | Guevara, Franki | Gris |
| `dipaola` | Dipaola, Martin | Gris |
| `gatto` | **Gatto, Mariano** | Rojo |
| `elizalde` | Elizalde, Juancho | Rojo |
| `canonico` | Canónico, Agus | Rojo |
| `vogelius` | Vogelius, Nico | Rojo |
| `mendez` | Mendez, Pato | Rojo |
| `molinario` | Molinario, Andy | Rojo |
| `scapparone` | Scapparone, Nico | Rojo |
| `fernandez` | Fernandez, Lucas | Rojo |

> **Nota Hdcp**: el hdcp de cada jugador es **dinámico** y cambia de fecha a fecha según evolución. Se lee de la tarjeta del día. Lo que figura en `PLAYERS[].hdc` del `index.html` son valores semilla (default) usados solo si no hay tarjeta cargada todavía; se sobrescriben al cargar cada fecha.

### Suplente Oficial (única excepción permitida en match)

| ID | Display | Notas |
|---|---|---|
| `gatto_ale` | **Gatto, Alejandro** | Suplente oficial especial. Acumula pts de match para el equipo que representa cuando entra. Hdcp también dinámico por tarjeta. |

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

### Par

- El **par** es **específico de cada hoyo**, no un número fijo. Cada hoyo tiene par 3, 4 ó 5.
- Cancha CUBA Fátima 2026: `[5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5]` → front 36 + back 36 = **72 par total**.
- Para otras canchas (GIRA, etc.) el par cambia. Siempre verificar contra tarjeta.

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

### Empates en posición
- **Si hay empate**, los puntos de los puestos ocupados se **suman y promedian** entre los empatados. Ej: si 3 empatan en pos 1, recibirán `(500+300+200)/3 = 333` puntos cada uno.
- **Para fechas ganadas (stats)**: todos los oficiales empatados en pos 1 suman +1 fecha ganada.

### Fecha vacante
- Si el ganador de una fecha (neto mínimo) es **suplente** o **jugador no-oficial / invitado**, la fecha queda **vacante**: ningún oficial suma fecha ganada, aunque haya un oficial que salió "primero entre oficiales".
- **Excepción**: el suplente oficial especial (`gatto_ale`) acumula match para el equipo que representa, pero NO suma medal personal (su puesto en medal es ignorado para fechas ganadas).

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
