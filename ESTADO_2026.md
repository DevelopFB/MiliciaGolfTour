# MGT 2026 — Estado del Torneo (snapshot al 10-Oct-2026, post F8 / pre GIRA)

> ### ⚠️ El equipo Gris se llama **La Cele** desde el 07-Sep-2026
>
> Cambió **solo el nombre visible y los colores** (celeste bandera `#75AADB`, y `#1B5E9E`
> para texto sobre blanco). **El formato de datos NO cambió.** El JSON sigue usando
> exactamente las mismas claves de siempre:
>
> ```json
> { "equipo": "g", "ganador": "g", "gris": ["benegas","zunino"], "pts_g": 0.5 }
> ```
>
> **Al generar el JSON de una fecha, seguí escribiendo `"gris"` y `"g"`.** Si escribís
> `"la_cele"` el backoffice no lo va a reconocer y la carga falla. "La Cele" es lo que se
> muestra en pantalla; `g` es lo que se guarda.
>
> El cambio aplica a 2026. Los campeones de 2016-2025 quedan como estaban (el equipo se
> llamaba **Blanco** en esos años, y Rojo ganó 2025) — no se reescribe la historia.


> **Para el Project Knowledge del proyecto de chat.** Snapshot FINAL de la temporada 2026.
> Fuente: `data/fechas.json` del repo (F1–F10), misma lógica que la web (`calcMedalPts` / `buildAccum`,
> verificado en render headless el 11-Nov-2026) y cuadrado contra el Master Excel.

---

# MGT 2026 — TEMPORADA CERRADA (11-Nov-2026)

## Campeones 2026

| Competencia | Campeón | Detalle |
|---|---|---|
| Medal #1 | **Benegas, Francisco** | 2231 pts |
| Medal #2 | Elizalde, Juan Pedro | 1418 pts |
| Medal #3 | Vogelius, Nicolás | 1406 pts |
| Medal #4 | Guevara, Francisco | 1259 pts |
| Match individual #1 | **Guevara, Francisco** | Ganó la final F10 a Molinario en el hoyo 17 |
| Match individual #2 | Molinario, Andrés | Finalista Rojo |
| Gross #1 | **Gatto, Mariano** | 86.7 promedio de las mejores 7 |
| Copa Match Play | **La Cele** | 28 a 19 · +28 hoyos |

## Decisiones de cierre (Nov-2026)

- **F10 suspendida por tormenta eléctrica** (Iberostar Bávaro). Por decisión del grupo **no cuenta para Medal
  ni para Gross**: las posiciones finales son las de después de la F9. Solo terminaron Gatto, Mariano (86),
  Elizalde, Juan Pedro (93) y Benegas, Francisco (100), asumiendo el riesgo; sus tarjetas quedan en
  `registroHistorico` de la F10 (la web las muestra, no suman). Dipaola, Martín dejó en el hoyo 15.
- **La final individual de match sí se jugó**: Guevara, Francisco vs Molinario, Andrés, definida en el hoyo 17
  (cargada como 2 hoyos [SUPUESTO: 2&1]). En `data/fechas.json` es el único match de la F10, con `final: true`.
- **El punto de la final suma a la Copa** (La Cele 27 → 28). No cambia al campeón: sin ese punto queda 27 a 19.
  Los demás cruces individuales de la F10 no se jugaron.
- **La gira (F9 y F10) no genera multas por ausencia.**
- Suplente F9: `sup_diazandrade` = Díaz Andrade, Juampi (mat. 116949), Rojo por Canónico. Gatto, Alejandro, Rojo por Méndez.

## Fixture final

| F# | Fecha | Cancha | Modalidad | Estado |
|---|---|---|---|---|
| 1 | 14-Mar | CUBA Fátima | Fourball 2v2 | Jugada |
| 2 | 11-Abr | CUBA Fátima | Fourball 2v2 | Jugada |
| 3 | 09-May | SHA Hebraica | Individual 1v1 | Jugada |
| 4 | 06-Jun | CUBA Fátima | Fourball 2v2 | Suspendida por niebla: solo match |
| 5 | 04-Jul | La Orquídea | Fourball 2v2 | Jugada |
| 6 | 08-Ago | CUBA Fátima | Individual 1v1 | Jugada |
| 7 | 12-Sep | CUBA Fátima | Fourball 2v2 | Jugada |
| 8 | 10-Oct | CUBA Fátima | Individual 1v1 | Jugada (reprogramada, sin multas) |
| 9 | 05-Nov | The Lakes (Barceló, Punta Cana) | Fourball 2v2 ×1.5 | Jugada (sin multas) |
| 10 | Nov (GIRA) | Iberostar Bávaro | Final individual ×2 | Suspendida por tormenta: solo la final de match |

## Medal — final

| # | Jugador | Equipo | Pts |
|---|---|---|---|
| 1 | Benegas, Francisco | La Cele | 2231 |
| 2 | Elizalde, Juan Pedro | Rojo | 1418 |
| 3 | Vogelius, Nicolás | Rojo | 1406 |
| 4 | Guevara, Francisco | La Cele | 1259 |
| 5 | Pannullo, Martín | La Cele | 1071 |
| 6 | Gatto, Mariano | Rojo | 1012 |
| 7 | Fernandez, Lucas | Rojo | 915 |
| 8 | Tarasido, Gonzalo | La Cele | 766 |
| 9 | Méndez, Gastón | Rojo | 712 |
| 10 | Basaldua, Ignacio | La Cele | 605 |
| 11 | Zunino, Javier | La Cele | 570 |
| 12 | Dipaola, Martín | La Cele | 526 |
| 13 | Molinario, Andrés | Rojo | 515 |
| 14 | Gonzalez, Agustín | La Cele | 452 |
| 15 | Canónico, Agustín | Rojo | 439 |
| 16 | Scapparone, Nicolás | Rojo | 93 |
| — | Gatto, Alejandro (sup) | — | 523 (cuadro aparte) |

Fechas ganadas: Benegas 3 (F6, F7, F9) · Guevara y Vogelius (F1) · Gatto Mariano (F2) · Fernandez (F3) ·
Elizalde (F5) · Pannullo (F8). F4 y F10 sin medal.

## Copa Match Play — final

| Fecha | La Cele | Rojo | Dif (La Cele) |
|---|---|---|---|
| F1 | 1 | 3 | −2 |
| F2 | 2 | 2 | −2 |
| F3 | 4 | 4 | −7 |
| F4 | 3 | 1 | 0 |
| F5 | 2 | 2 | −1 |
| F6 | 5.5 | 2.5 | +15 |
| F7 | 2.5 | 1.5 | +9 |
| F8 | 4.5 | 1.5 | +11 |
| F9 | 2.5 | 1.5 | +3 |
| F10 | 1 | 0 | +2 (final) |
| **TOTAL** | **28** | **19** | **+28** |

## Match individual — final

La Cele: Guevara 6.0 (+19) · Pannullo 4.25 (0) · Benegas 3.5 (+8) · Dipaola 3.0 (+8) · Gonzalez 2.5 (+3) ·
Tarasido 2.25 (+1) · Basaldua 2.25 (+3) · Zunino 2.0 (+3)
Rojo: Molinario 4.0 (+14) · Méndez 3.25 (+13) · Elizalde 3.25 (+2) · Gatto Mariano 3.0 (−2) · Canónico 1.25 (−4) ·
Vogelius 1.25 (−9) · Fernandez 1.0 (−19) · Scapparone 0.25 (−17)
Gatto, Alejandro (sup): 1.75, −12.

## Gross — final (promedio mejores 7, mínimo 7 tarjetas)

| # | Jugador | Tarjetas | Prom. mejores 7 |
|---|---|---|---|
| 1 | Gatto, Mariano | 7 | 86.7 |
| 2 | Elizalde, Juan Pedro | 8 | 88.6 |
| 3 | Tarasido, Gonzalo | 7 | 91.0 |
| 4 | Vogelius, Nicolás | 7 | 91.6 |
| 5 | Guevara, Francisco | 7 | 95.6 |
| 6 | Benegas, Francisco | 8 | 97.4 |
| 7 | Dipaola, Martín | 8 | 104.3 |

No llegaron a 7: Gonzalez 5 · Zunino 3 · Basaldua 6 · Pannullo 6 · Canónico 6 · Méndez 6 · Molinario 6 ·
Scapparone 2 · Fernandez 5.

## Pozo y premios (USD, Master → Recaudación)

Pozo 832: Medal 174.72 / 108.16 / 74.88 / 49.92 · Match ind. 108.16 / 66.56 · Gross 24.96 · Copa 224.64.

## Notas operativas (learnings vigentes)

- **Publicar ≠ guardar (teléfono):** sin el token en Admin → 🔑 Publicación, el backoffice guarda solo en localStorage.
- **Commitear ≠ publicar (Cowork):** después de tocar el repo, `git push origin main` y `git log origin/main..HEAD` vacío.
- Verificación real: incógnito o `data/fechas.json` en GitHub.
- Jugador que juega el match sin entregar tarjeta → scorecard con `null`. No es ausente.
- Fecha sin medal (F4, F10) → `medal: []`, `scorecard: []`. Tarjetas que no suman → `registroHistorico`.
- Final de match → `matchs[].final = true` en la F10. La web lo usa para mostrar los campeones (`isTemporadaCerrada()`).
- Master: `python3 scripts/build_master.py MGT_2026_Master.xlsx data/fechas.json data/fixture.json MGT_2026_Master.xlsx`.
