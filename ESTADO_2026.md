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


> **Para el Project Knowledge del proyecto de chat.** Da contexto acumulado a Claude cuando procesa
> una fecha desde el teléfono (sin acceso al repo).
> Fuente: `data/fechas.json` del repo (F1–F8), con la misma lógica de cálculo que la web
> (`calcMedalPts` / `buildAccum`, verificado en render headless el 10-Oct-2026).
> Regenerar después de cada fecha.

---

## Próxima fecha

**FECHA 9 — GIRA Punta Cana (04-09 Nov 2026, día exacto a confirmar) — Fourball 2v2 inverso — Medal ×1.5**
Después, **FECHA 10 — GIRA — FINAL — Medal ×2 — Final individual #1 La Cele vs #1 Rojo.**
⚠️ Cancha distinta: el par y el stroke index se leen de la tarjeta. No asumir Fátima.

## Fixture y estado

| F# | Fecha | Cancha | Modalidad | Estado |
|---|---|---|---|---|
| 1 | 14-Mar | CUBA Fátima | Fourball 2v2 | Jugada |
| 2 | 11-Abr | CUBA Fátima | Fourball 2v2 | Jugada |
| 3 | 09-May | SHA Hebraica | Individual 1v1 | Jugada |
| 4 | 06-Jun | CUBA Fátima | Fourball 2v2 | Jugada — **suspendida por niebla**, solo valió Match Play. |
| 5 | 04-Jul | La Orquídea | Fourball 2v2 | Jugada |
| 6 | 08-Ago | CUBA Fátima | Individual 1v1 | Jugada — 16 presentes |
| 7 | 12-Sep | CUBA Fátima | Fourball 2v2 | Jugada — ausente Gonzalez (sup. Gatto, Hector) |
| 8 | **10-Oct** | CUBA Fátima | Individual 1v1 | Jugada — **reprogramada** del 03-Oct por clima. 5 ausentes, **sin multas** (fecha reprogramada). 6 matchs. |
| 9 | Nov (GIRA) | Punta Cana | Fourball inverso (×1.5) | Pendiente |
| 10 | Nov (GIRA) | Punta Cana | Individual FINAL (×2) | Pendiente |

## Medal — acumulado individual (F1–F8; F4 no dio pts)

Puntos como los calcula la web (redondeo por grupo de empate).

| # | Jugador | Equipo | Total pts | F8 |
|---|---|---|---|---|
| 1 | Benegas, Francisco | La Cele | 1481 | +135 |
| 2 | Elizalde, Juan Pedro | Rojo | 1388 | +70 |
| 3 | Guevara, Francisco | La Cele | 1259 | +135 |
| 4 | Vogelius, Nicolás | Rojo | 1031 | ausente |
| 5 | Fernandez, Lucas | Rojo | 885 | +90 |
| 6 | Pannullo, Martín | La Cele | 868 | +500 |
| 7 | Gatto, Mariano | Rojo | 862 | +20 |
| 8 | Méndez, Gastón | Rojo | 712 | +20 |
| 9 | Tarasido, Gonzalo | La Cele | 653 | ausente |
| 10 | Dipaola, Martín | La Cele | 496 | +78 |
| 11 | Basaldua, Ignacio | La Cele | 470 | ausente |
| 12 | Canónico, Agustín | Rojo | 439 | ausente |
| 13 | Gonzalez, Agustín | La Cele | 422 | +200 |
| 14 | Molinario, Andrés | Rojo | 410 | +78 |
| 15 | Zunino, Javier | La Cele | 195 | +100 |
| 16 | Scapparone, Nicolás | Rojo | 93 | ausente |
| — | Gatto, Alejandro (sup) | — | 320 | +300 (cuadro aparte) |

Quedan en juego: F9 (1° = 750) y F10 (1° = 1000).

Fechas ganadas: F1 Guevara y Vogelius · F2 Gatto Mariano · F3 Fernandez · F4 sin ganador ·
F5 Elizalde · F6 Benegas · F7 Benegas (73) · **F8 Pannullo (68)**.

## Match Play — Copa por equipos (F1–F8)

| Fecha | La Cele | Rojo | Dif hoyos (La Cele) |
|---|---|---|---|
| F1 | 1 | 3 | −2 |
| F2 | 2 | 2 | −2 |
| F3 | 4 | 4 | −7 |
| F4 | 3 | 1 | 0 |
| F5 | 2 | 2 | −1 |
| F6 | 5.5 | 2.5 | +15 |
| F7 | 2.5 | 1.5 | +9 |
| F8 | 4.5 | 1.5 | +11 |
| **TOTAL** | **24.5** | **17.5** | **+23** |

Ventaja La Cele: 7 pts. **La Copa se juega hasta el final**: hay matchs en las dos fechas de la gira.
F9 = 4 fourball (4 pts); F10 = individuales [SUPUESTO: 8 cruces, 8 pts] → 12 pts en juego.
La Cele asegura la Copa con 3 pts; Rojo necesita 10 para darla vuelta (9.5 empata y desempata la dif de hoyos).

## Match individual — finalistas provisorios de la F10

La Cele: Guevara 5.0 (+22) · Pannullo 3.75 · Benegas 3.0 · Dipaola 2.75 · Gonzalez 2.5 · Tarasido 2.0 · Basaldua 1.75 · Zunino 1.5
Rojo: Molinario 3.5 (+11) · Méndez 3.25 (+13) · Elizalde 3.25 (+8) · Gatto Mariano 2.75 · Canónico 1.25 · Fernandez 1.0 · Vogelius 0.75 · Scapparone 0.25
Gatto, Alejandro (sup): 1.5 pts, −12.

## Gross — historial 2026 (premio = promedio mejores 7 tarjetas)

| Jugador | Tarjetas | Avg (mejores ≤7) | Mejor | ¿Llega a 7? |
|---|---|---|---|---|
| Gatto, Mariano | 6 | 86.7 | 75 | con 1 más |
| Elizalde, Juan Pedro | 7 | 88.6 | 83 | ✓ |
| Tarasido, Gonzalo | 6 | 90.3 | 86 | con 1 más |
| Vogelius, Nicolás | 6 | 91.8 | 84 | con 1 más |
| Pannullo, Martín | 5 | 92.6 | 84 | necesita F9 y F10 |
| Méndez, Gastón | 6 | 93.7 | 86 | con 1 más |
| Basaldua, Ignacio | 5 | 94.6 | 91 | necesita F9 y F10 |
| Molinario, Andrés | 5 | 94.8 | 86 | necesita F9 y F10 |
| Guevara, Francisco | 7 | 95.6 | 87 | ✓ |
| Canónico, Agustín | 6 | 95.8 | 91 | con 1 más |
| Benegas, Francisco | 7 | 99.4 | 92 | ✓ |
| Dipaola, Martín | 7 | 104.3 | 93 | ✓ |
| Gonzalez, Agustín | 4 | 84.2 | 80 | no llega |
| Fernandez, Lucas | 4 | 93.0 | 90 | no llega |
| Zunino, Javier | 2 | 89.0 | 87 | no llega |
| Scapparone, Nicolás | 2 | 102.0 | 95 | no llega |
| Gatto, Alejandro | 4 | 110.2 | 97 | no compite |

## Últimos hdcp vistos (SOLO referencia — usar SIEMPRE el de la tarjeta del día)

F8 (10-Oct, CUBA Fátima, "HCP Medal" de la tarjeta: depende de las bochas de salida de cada jugador): Gonzalez 7 · Zunino 15 · Pannullo 16 ·
Benegas 25 · Guevara 20 · Dipaola 26 · Gatto Mariano 8 · Elizalde 14 · Méndez 16 · Molinario 17 ·
Fernandez 15 · Gatto Alejandro 25.

## Notas operativas (learnings vigentes)

- **Publicar ≠ guardar (desde el teléfono).** Si el navegador no tiene el token de GitHub cargado
  (Admin → 🔑 Publicación), el backoffice guarda solo en localStorage y la web se ve igual. Así se
  perdió una semana con la F6. Desde el 18-Ago la web muestra un aviso persistente "⚠ Sin publicar"
  con botón para publicar. **PASO 0 antes de cada fecha: abrir el backoffice y confirmar que el token
  está cargado, con el mismo navegador de siempre.**
- **Commitear ≠ publicar (desde Cowork).** El 07-Sep se descubrió que la F6 llevaba 3 semanas fuera de
  la web por un motivo distinto: los commits estaban hechos en el repo local de la Mac pero nunca se
  hizo `git push`. **Después de cualquier sesión de Cowork que toque el repo: `git push origin main` y
  verificar que `git log origin/main..HEAD` sale vacío.** El bash del agente tiene red pero no tiene
  credenciales de git, así que el push lo hace Pancho o se hace por Terminal.
- **Verificación real de que algo está online:** abrir la web en incógnito, o mirar
  `data/fechas.json` en GitHub. Nunca confiar en el navegador de siempre — su localStorage miente.
- **Fechas reprogramadas oficialmente no generan multa** (F8, decisión del 10-Oct-2026).
- Suplentes usados en 2026: `sup_shaw` (F2) · `sup_alfonso` = Alfonso, Juan Ignacio (F3, F5) ·
  `sup_nissen` = Nissen, Germán (F4) · `hector_gatto` (F4) · `sup_diazdelfino` = Díaz Delfino, Pablo (F5) ·
  `sup_gascon` = Gascon, Alejo (F5). Convención de ID externo: `sup_apellido`. **F6 no tuvo suplentes.** F7: `hector_gatto`. F8: `gatto_ale` (Rojo).
- `sin_suplente`: placeholder para matchs 2v1 — no romper el formato fourball.
- Jugador que juega el match pero no entrega tarjeta → scorecard con `hoyos/gross/neto/hdcp: null`.
  NO es un ausente y NO paga multa.
- **Master Excel regenerado el 10-Oct-2026** desde `data/fechas.json` con `scripts/build_master.py`
  (`python3 scripts/build_master.py MGT_2026_Master.xlsx data/fechas.json data/fixture.json MGT_2026_Master.xlsx`).
  Todo con fórmulas: hojas FN (hoyos + hdcp como input → gross, neto, puesto, pts con reparto de empates),
  `Match_Log` (un match por fila → Match individual y Copa), Medal, Gross (mejores 7 reales), Supuestos.
  Cuadra exacto con la web. Se conservó la hoja `Historico`. Las trampas viejas (Gatto, Alejandro en dos filas,
  sobrenombres en los lookups, Avg de todas las tarjetas) dejaron de existir: ahora todo se busca por ID.
