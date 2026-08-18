# Templates de los documentos del tour

Diseño congelado según `COCKPITS/MGT/core/identidad-visual.md`. **No se rediseña cada fecha.**

| Archivo | Qué es | Cuándo |
|---|---|---|
| `informe-fecha.html` | 1 página A4 — podio, ranking, stats, match play, crónica | El sábado, para el grupo |
| `resumen-ejecutivo.html` | 3 páginas A4 — acumulados de medal, match y gross + fixture | El sábado, estado del torneo |

## Cómo se usan

Cada template renderiza desde un único `const DATA = {...}` al principio del script.
Para una fecha nueva: reemplazar ese objeto y nada más. Abrir en el navegador → Cmd/Ctrl+P → PDF.

Los datos que trae hoy son los reales de la F6, como referencia viva de qué forma tiene cada campo.

## Campos que hay que completar a mano cada fecha

- `horarios` de salida de cada match — no vienen en el JSON del backoffice.
- La crónica (`comentario`) — sale del JSON de la fecha.

## Reglas

- Nombre completo siempre (`"Apellido, Nombre"`).
- Formato es-AR: miles con punto, decimales con coma. Decimales solo cuando aportan.
- Medal y Match Play nunca se mezclan.
- El marcador de equipos se muestra como **diferencia** (`GRIS +3`), con la dif de hoyos al lado
  porque es el desempate.
