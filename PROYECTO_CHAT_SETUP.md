# Workflow del proyecto MGT — chat, cockpit y Cowork

> Reemplaza al setup de jul-2026 (que todavía hablaba de Supabase). Actualizado 18-Ago-2026.

**TL;DR**: la fuente de verdad son los JSON del repo `MiliciaGolfTour`. El sábado cargás la
fecha desde el teléfono con un chat del proyecto; el lunes Cowork actualiza el Master Excel
y regenera este contexto. No hay base de datos: publicar = commitear al repo.

---

## 1. Punto de entrada

| Dónde | Para qué |
|---|---|
| `COCKPITS/MGT/CONTRATO.md` | **Se lee primero** en cualquier sesión de Cowork sobre la Milicia. Después `core/overview.md` y `core/decisions-pending.md`. |
| `COCKPITS/MGT/core/agente-torneos.md` | Contrato del agente que carga y cierra una fecha (incluye multas). |
| `COCKPITS/MGT/core/agente-cronista.md` | Contrato del agente que escribe la historia/libro. |
| Repo `MiliciaGolfTour/CLAUDE.md` | Reglas canónicas del torneo. El cockpit gobierna el trabajo; esto gobierna el juego. |
| Repo `MiliciaGolfTour/PROMPT_CARGA_FECHA.md` | Procedimiento de extracción de tarjetas y los 4 outputs. |

## 2. Project Knowledge — qué tiene que estar arriba

| Archivo | Estado |
|---|---|
| `CLAUDE.md` | Reglas canónicas. Reemplazar cuando cambie en el repo. |
| `PROMPT_CARGA_FECHA.md` | v3 — 4 outputs (resumen, JSON, TSV Master, HTML del PDF). |
| `ESTADO_2026.md` | Snapshot acumulado. **Regenerar después de CADA fecha** y volver a subirlo. |
| `jugadores_historico.json` | Sólo para consultas históricas 2016-2025. |

Fuera: el reglamento genérico de golf, los ~20 `.xlsx` históricos y el `index.html`
(450 KB) — compiten por contexto en cada chat y no aportan a la carga de fecha.

## 3. Workflow

**Sábado — teléfono, sólo chat:**

1. Chat nuevo en el proyecto → pegar el mini-prompt de `PROMPT_CARGA_FECHA.md` completado
   + fotos de las tarjetas.
2. Pasar matchs, suplentes y cancha cuando el agente los pida (de a una pregunta por vez).
3. Revisar el resumen y las ⚠️ discrepancias → copiar el JSON → backoffice de la web →
   **📋 Pegar JSON** → validar el grid → **Guardar**.
   Guardar **comitea `data/fechas.json` al repo** vía GitHub Contents API; GitHub Pages
   republica en ~1 min. Requiere el token cargado en ese navegador (Admin → 🔑 Publicación).
   Sin token, el cambio queda sólo en el localStorage de ese teléfono.
4. Cerrar las **multas** de la fecha (USD 12 por ausente, con o sin suplente). El backoffice
   las sugiere al aplicar; se guardan en `data/recaudacion.json`. Una fecha no está cerrada
   hasta que las multas estén resueltas.
5. No borrar el chat: el JSON queda ahí para el lunes.

**Lunes — PC, Cowork:**

1. Abrir Cowork en este proyecto: *"Actualizá el Master con la FN, el JSON está en el chat"*.
2. Cowork crea la hoja `FN` con fórmulas (layout F1–F3), actualiza `Match`,
   `Gross_Historial`, `Medal_Consolidado`, `Fixture` (estado → Jugada) en
   `MGT_2026_Master.xlsx`, y regenera `ESTADO_2026.md`.
3. Subir `ESTADO_2026.md` regenerado al Project Knowledge (reemplazar).
4. Agregar la entrada de la fecha en `COCKPITS/MGT/core/registro-sesiones.md`.

> El Master tiene dos formas: el **curado** (`MGT_2026_Master.xlsx`, hosteado en el repo,
> con fórmulas reales, auditado, se regenera off-line tras cada fecha) y el **en vivo**
> (botón "Generar Master en vivo (JS)" → `scripts/master_excel_generator.js` + ExcelJS,
> útil apenas cargás una fecha). Los dos se mantienen.

## 4. Pendientes abiertos

Viven en `COCKPITS/MGT/core/decisions-pending.md`. Al 18-Ago-2026, los que importan:

- **#10 — La F6 (08-Ago) está validada pero SIN publicar.** El repo y la web llegan a F5.
- **#11** — `keep-supabase-alive.yml` sigue en este repo pero pinguea el Supabase de otro proyecto.
- **#12** — Token GitHub y API key de Anthropic viven en el localStorage del navegador.
- **#14** — `ESTADO_2026.md` queda desactualizado hasta publicar la F6.
- **#8 / #9** — Historia: falta confirmar ruta y formato del manuscrito, y el perfil de voz del cronista.
