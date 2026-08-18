# Milicia Golf Tour

Webapp single-file (`index.html`) del torneo Milicia Golf Tour, desplegada en
**GitHub Pages**: https://developfb.github.io/MiliciaGolfTour/

## Arquitectura (plana, sin base de datos)

Desde jul-2026 **no hay Supabase**. La fuente de verdad son archivos JSON versionados
en este mismo repo:

| Archivo | Contenido |
|---|---|
| `data/fechas.json` | fechas jugadas: scorecard + matchs + medal + comentario |
| `data/fixture.json` | fecha, modalidad, criterio y organizadores de las 10 fechas |
| `data/recaudacion.json` | inscripción + multas por fecha por jugador |
| `jugadores_historico.json` | histórico 2016-2025 por jugador (`_version` fuerza re-sync) |
| `data/backup-supabase/` | snapshot de las tablas Supabase al migrar (sólo histórico) |

**Lectura**: el navegador pinta primero desde localStorage (cache) y después hace
`fetch` de los JSON del repo, que mandan.

**Escritura**: el backoffice (tab Admin) comitea vía **GitHub Contents API** con un token
fine-grained (scope: sólo este repo, permiso *Contents: Read and write*) guardado en el
localStorage del navegador del admin — tab Admin → 🔑 Publicación. El guardado es
read-modify-write (lee sha + contenido fresco, mergea, publica). Pages republica en ~1 min.
Sin token, los cambios quedan sólo en el navegador.

> El token nunca se commitea ni se comparte. Si se filtra, revocarlo en GitHub y generar
> uno nuevo; no hace falta tocar código.

## Otros archivos

- `CLAUDE.md` — reglas canónicas del torneo (jugadores, medal vs match, pts, hdcp cap 26).
  Fuente de verdad de las reglas: leer siempre antes de tocar datos.
- `PROMPT_CARGA_FECHA.md` — procedimiento de extracción de tarjetas y outputs esperados.
- `PROJECT_INSTRUCTIONS.md` — instrucciones del agente del torneo.
- `scripts/master_excel_generator.js` — genera el Master XLSX "en vivo" desde el navegador
  (ExcelJS). Complementa a `MGT_2026_Master.xlsx`, el Master curado que se regenera
  off-line después de cada fecha.

## Desarrollo local

```bash
python3 -m http.server 8377   # servir el repo y abrir http://localhost:8377
```
