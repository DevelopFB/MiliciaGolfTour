# -*- coding: utf-8 -*-
"""Regenera MGT_2026_Master.xlsx desde data/fechas.json + data/fixture.json.
Todo lo calculable va como fórmula. Inputs (golpes, hdcp, resultados de match) en azul.
Conserva la hoja 'Historico' del Master anterior.
Uso: python3 build_master.py <master_viejo.xlsx> <fechas.json> <fixture.json> <salida.xlsx> [recaudacion.json]
(si no se pasa, toma recaudacion.json de la misma carpeta que fechas.json)
"""
import json, sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import FormulaRule
from openpyxl.utils import get_column_letter as L
from openpyxl.comments import Comment

OLD, FECHAS, FIXTURE, OUT = sys.argv[1:5]
import os
RECAUD = sys.argv[5] if len(sys.argv) > 5 else os.path.join(os.path.dirname(FECHAS), 'recaudacion.json')
fechas = [f for f in json.load(open(FECHAS)) if not f.get('pendiente')]
fixture = json.load(open(FIXTURE))
recaud = {r['id']: r for r in json.load(open(RECAUD))}

# ── Jugadores canónicos (CLAUDE.md §2) ───────────────────────────────
OFICIALES = [
    ('gonzalez', 'Gonzalez, Agustín', 'Agus', 'g'), ('tarasido', 'Tarasido, Gonzalo', 'Gonzalo', 'g'),
    ('zunino', 'Zunino, Javier', 'Javi', 'g'), ('basaldua', 'Basaldua, Ignacio', 'Ignacio', 'g'),
    ('pannullo', 'Pannullo, Martín', 'Tincho', 'g'), ('benegas', 'Benegas, Francisco', 'Pancho', 'g'),
    ('guevara', 'Guevara, Francisco', 'Franki', 'g'), ('dipaola', 'Dipaola, Martín', 'Dipa', 'g'),
    ('gatto', 'Gatto, Mariano', 'Gattait', 'r'), ('elizalde', 'Elizalde, Juan Pedro', 'Juancho', 'r'),
    ('canonico', 'Canónico, Agustín', 'Kno', 'r'), ('vogelius', 'Vogelius, Nicolás', 'Nico', 'r'),
    ('mendez', 'Méndez, Gastón', 'Pato', 'r'), ('molinario', 'Molinario, Andrés', 'Andy', 'r'),
    ('scapparone', 'Scapparone, Nicolás', 'Nico', 'r'), ('fernandez', 'Fernandez, Lucas', 'Lule', 'r'),
]
SUP_ESP = ('gatto_ale', 'Gatto, Alejandro', 'Ale', '')
SUP_NAMES = {'gatto_ale': 'Gatto, Alejandro', 'hector_gatto': 'Gatto, Hector',
             'sup_alfonso': 'Alfonso, Juan Ignacio', 'sup_nissen': 'Nissen, Germán',
             'sup_diazdelfino': 'Díaz Delfino, Pablo', 'sup_gascon': 'Gascon, Alejo',
             'sup_diazandrade': 'Díaz Andrade, Juampi'}
OF_IDS = [p[0] for p in OFICIALES]
NAME = {p[0]: p[1] for p in OFICIALES}; NAME.update(SUP_NAMES)
TEAM = {p[0]: p[3] for p in OFICIALES}
TEAM_TXT = {'g': 'LA CELE', 'r': 'ROJO'}
PAR_FATIMA = [5, 3, 4, 5, 4, 4, 3, 4, 4, 4, 5, 4, 4, 3, 4, 4, 3, 5]

# ── Estilos ──────────────────────────────────────────────────────────
NAVY = '1B2A4A'; GOLD = 'C9A84C'; CELE = '1B5E9E'; ROJO = 'C0392B'
F_BASE = Font(name='Arial', size=10)
F_IN = Font(name='Arial', size=10, color='0000FF')            # input
F_LINK = Font(name='Arial', size=10, color='008000')          # link a otra hoja
F_HDR = Font(name='Arial', size=10, bold=True, color='FFFFFF')
F_TITLE = Font(name='Arial', size=14, bold=True, color=NAVY)
F_SUB = Font(name='Arial', size=9, italic=True, color='666666')
F_BOLD = Font(name='Arial', size=10, bold=True)
FILL_HDR = PatternFill('solid', fgColor=NAVY)
FILL_IN = PatternFill('solid', fgColor='FFF9E6')
FILL_PAR = PatternFill('solid', fgColor='EEF2F7')
FILL_TOT = PatternFill('solid', fgColor='F3EAD2')
THIN = Side(style='thin', color='D0D5DD')
B_BOT = Border(bottom=THIN)
CENTER = Alignment(horizontal='center', vertical='center')
LEFT = Alignment(horizontal='left', vertical='center')
NUM0 = '#,##0;-#,##0;"-"'
NUM2 = '#,##0.00;-#,##0.00;"-"'
NUMS = '+#,##0;-#,##0;0'


def setup(ws, title, subtitle=None, widths=None):
    ws.sheet_view.showGridLines = False
    ws['A1'] = title; ws['A1'].font = F_TITLE
    if subtitle:
        ws['A2'] = subtitle; ws['A2'].font = F_SUB
    for col, w in (widths or {}).items():
        ws.column_dimensions[col].width = w


def header(ws, row, col, labels):
    for i, lab in enumerate(labels):
        c = ws.cell(row=row, column=col + i, value=lab)
        c.font = F_HDR; c.fill = FILL_HDR; c.alignment = CENTER


def put(ws, ref, value, font=F_BASE, fmt=None, align=None, fill=None):
    c = ws[ref]; c.value = value; c.font = font
    if fmt: c.number_format = fmt
    if align: c.alignment = align
    if fill: c.fill = fill
    return c


# ── Libro base: conservar solo Historico ────────────────────────────
wb = openpyxl.load_workbook(OLD)
for ws in list(wb.worksheets):
    if ws.title != 'Historico':
        wb.remove(ws)
hist = wb['Historico']

# ════════════════════════════════════════════════════════════════════
# SUPUESTOS
# ════════════════════════════════════════════════════════════════════
sup = wb.create_sheet('Supuestos', 0)
setup(sup, 'MGT 2026 — Supuestos y reglas', 'Celdas azules = inputs editables. Fuente: CLAUDE.md del repo (reglas 2026).',
      {'A': 30, 'B': 14, 'C': 14, 'D': 4, 'E': 30, 'F': 14})
header(sup, 4, 1, ['Puesto', 'Pts base'])
POS_MAX = 24
for i in range(POS_MAX):
    r = 5 + i; pos = i + 1
    pts = {1: 500, 2: 300, 3: 200, 4: 150, 5: 120, 6: 100, 7: 90, 8: 80, 9: 75, 10: 70}.get(pos, 20 if pos <= 14 else 0)
    put(sup, f'A{r}', pos, align=CENTER)
    put(sup, f'B{r}', pts, F_IN, NUM0, CENTER, FILL_IN)
POS_RNG = f'Supuestos!$A$5:$A${4 + POS_MAX}'
PTS_RNG = f'Supuestos!$B$5:$B${4 + POS_MAX}'
header(sup, 4, 5, ['Parámetro', 'Valor'])
params = [('Tope de hdcp del tour', 26, 'HCAP'), ('Multiplicador F1–F8', 1, 'M1'), ('Multiplicador F9', 1.5, 'M9'),
          ('Multiplicador F10', 2, 'M10'), ('Pts equipo por match ganado', 1, 'PW'), ('Pts equipo por match empatado', 0.5, 'PE'),
          ('Pts personales fourball (por jugador ganador)', 0.5, 'PFB'), ('Pts personales individual (ganador)', 1, 'PIND'),
          ('Multa por ausencia (USD)', 12, 'MULTA'), ('Tarjetas que cuentan para el Gross', 7, 'BESTN')]
P = {}
for i, (lab, val, key) in enumerate(params):
    r = 5 + i
    put(sup, f'E{r}', lab); put(sup, f'F{r}', val, F_IN, '0.0#', CENTER, FILL_IN)
    P[key] = f'Supuestos!$F${r}'
r = 5 + len(params) + 1
notes = ['Empates en el Medal: se suman los pts de los puestos ocupados y se reparten en partes iguales (redondeo a entero, igual que la web).',
         'Todos los que presentaron tarjeta ocupan puesto (oficiales y suplentes). Solo los oficiales acumulan al tour; Gatto, Alejandro acumula en cuadro aparte.',
         'Copa Match Play: solo suman los matchs. El Medal no aporta nada a los equipos.',
         'Dif de hoyos: se carga en magnitud positiva; el ganador define el signo (perspectiva La Cele).',
         'Fechas reprogramadas oficialmente no generan multa (F8, decisión 10-Oct-2026).',
         'Hdcp: el "HCP Medal" de la tarjeta del día (depende de las bochas de salida), con tope de 26.']
for i, n in enumerate(notes):
    put(sup, f'E{r + i}', '• ' + n, F_SUB)

# ════════════════════════════════════════════════════════════════════
# JUGADORES
# ════════════════════════════════════════════════════════════════════
jug = wb.create_sheet('Jugadores', 1)
setup(jug, 'Jugadores 2026', 'Lista canónica (CLAUDE.md). Oficial = 1 acumula Medal y Match individual.',
      {'A': 14, 'B': 26, 'C': 12, 'D': 10, 'E': 9})
header(jug, 4, 1, ['ID', 'Nombre', 'Sobrenombre', 'Equipo', 'Oficial'])
roster = OFICIALES + [SUP_ESP]
for i, (pid, nm, nick, t) in enumerate(roster):
    r = 5 + i
    put(jug, f'A{r}', pid, F_IN); put(jug, f'B{r}', nm, F_IN); put(jug, f'C{r}', nick, F_IN)
    put(jug, f'D{r}', TEAM_TXT.get(t, 'SUP'), F_IN, align=CENTER); put(jug, f'E{r}', 1 if t else 0, F_IN, align=CENTER)
JUG_LAST = 4 + len(roster)
JID = f'Jugadores!$A$5:$A${JUG_LAST}'; JOF = f'Jugadores!$E$5:$E${JUG_LAST}'

# ════════════════════════════════════════════════════════════════════
# HOJAS DE FECHA
# ════════════════════════════════════════════════════════════════════
FECHA_SHEETS = {}   # num -> (sheetname, first_row, last_row)
HOLE_COL0 = 4       # D = H1
for f in fechas:
    if not f.get('medal'):
        continue  # F4: suspendida, sin tarjetas
    n = f['num']; name = f'F{n}'
    ws = wb.create_sheet(name)
    par = f.get('par') or PAR_FATIMA
    mult_key = 'M9' if n == 9 else 'M10' if n == 10 else 'M1'
    sups = {s['id']: s for s in f.get('suplentes') or []}
    for s in sups.values():
        if s['id'] not in NAME:
            NAME[s['id']] = s.get('name') or s.get('nombre') or s['id']
    setup(ws, f"FECHA {n} — {f['fecha']} — {f.get('cancha', '')}",
          f"Organizadores: {f.get('organizadores', '')} · Par {sum(par)} · Azul = input (golpes, hdcp del día, gross de tarjeta si no hay hoyo por hoyo)",
          {'A': 13, 'B': 24, 'C': 9})
    for k in range(18):
        ws.column_dimensions[L(HOLE_COL0 + k)].width = 4.2
    # columnas derivadas
    cG, cGT, cHD, cHA, cN, cPos, cEmp, cPts, cOf, cAc = [HOLE_COL0 + 18 + k for k in range(10)]
    cE, cB, cPa, cBo, cD = [cAc + 1 + k for k in range(5)]
    for c, w in zip(range(cG, cD + 1), [7, 8, 7, 7, 7, 6, 6, 8, 7, 8, 6, 6, 6, 6, 6]):
        ws.column_dimensions[L(c)].width = w
    hdr = ['ID', 'Jugador', 'Equipo'] + [f'H{k + 1}' for k in range(18)] + \
          ['Gross', 'Gross tarjeta', 'Hdcp día', 'Hdcp aplic', 'Neto', 'Pos', 'Empat.', 'Pts', 'Oficial', 'Acumula',
           'Eagle-', 'Birdie', 'Par', 'Bogey', 'Doble+']
    header(ws, 5, 1, hdr)
    # fila PAR
    put(ws, 'B4', 'PAR', F_BOLD, fill=FILL_PAR)
    for k in range(18):
        put(ws, f'{L(HOLE_COL0 + k)}4', par[k], F_IN, align=CENTER, fill=FILL_PAR)
    put(ws, f'{L(cG)}4', f'=SUM({L(HOLE_COL0)}4:{L(HOLE_COL0 + 17)}4)', F_BOLD, align=CENTER, fill=FILL_PAR)
    # filas
    sc = {s['id']: s for s in f.get('scorecard') or []}
    medal = {m['id']: m for m in f.get('medal') or []}
    ids = list(dict.fromkeys(list(medal) + list(sc)))
    ids.sort(key=lambda i: (0 if TEAM.get(i) == 'g' and i not in sups else 1 if TEAM.get(i) == 'r' and i not in sups else 2,
                            OF_IDS.index(i) if i in OF_IDS else 99))
    r0 = 6; r1 = r0 + len(ids) - 1
    NRNG = f'${L(cN)}${r0}:${L(cN)}${r1}'
    for i, pid in enumerate(ids):
        r = r0 + i
        s = sc.get(pid) or {}
        m = medal.get(pid) or {}
        holes = s.get('holes') or s.get('hoyos')
        eq = sups[pid]['equipo'] if pid in sups else TEAM.get(pid, '')
        put(ws, f'A{r}', pid, F_IN)
        put(ws, f'B{r}', NAME.get(pid, pid) + (' (sup)' if pid in sups or pid not in OF_IDS else ''))
        put(ws, f'C{r}', TEAM_TXT.get(eq, ''), F_IN, align=CENTER)
        h1, h18 = f'{L(HOLE_COL0)}{r}', f'{L(HOLE_COL0 + 17)}{r}'
        if holes:
            for k in range(18):
                put(ws, f'{L(HOLE_COL0 + k)}{r}', holes[k], F_IN, align=CENTER)
        elif m.get('gross'):
            put(ws, f'{L(cGT)}{r}', m['gross'], F_IN, align=CENTER, fill=FILL_IN)
            ws[f'{L(cGT)}{r}'].comment = Comment('Gross cargado sin hoyo por hoyo (dato de data/fechas.json).', 'MGT')
        hd = m.get('hdcp') if m else s.get('hdcp')
        if hd is not None and (holes or m.get('gross')):
            put(ws, f'{L(cHD)}{r}', hd, F_IN, align=CENTER)
        G, GT, HD, HA, N = (f'{L(c)}{r}' for c in (cG, cGT, cHD, cHA, cN))
        put(ws, G, f'=IF(COUNT({h1}:{h18})=18,SUM({h1}:{h18}),IF({GT}="","",{GT}))', F_BOLD, align=CENTER)
        put(ws, HA, f'=IF({HD}="","",MIN({HD},{P["HCAP"]}))', align=CENTER)
        put(ws, N, f'=IF(OR({G}="",{HA}=""),"",{G}-{HA})', F_BOLD, align=CENTER)
        put(ws, f'{L(cPos)}{r}', f'=IF({N}="","",COUNTIF({NRNG},"<"&{N})+1)', align=CENTER)
        put(ws, f'{L(cEmp)}{r}', f'=IF({N}="","",COUNTIF({NRNG},{N}))', align=CENTER)
        pos, emp = f'{L(cPos)}{r}', f'{L(cEmp)}{r}'
        put(ws, f'{L(cPts)}{r}',
            f'=IF({N}="","",ROUND(SUMPRODUCT(({POS_RNG}>={pos})*({POS_RNG}<{pos}+{emp})*{PTS_RNG})/{emp}*{P[mult_key]},0))',
            F_BOLD, NUM0, CENTER)
        es_sup = 1 if pid in sups else 0
        put(ws, f'{L(cOf)}{r}', f'=IF({es_sup}=1,0,IFERROR(INDEX({JOF},MATCH(A{r},{JID},0)),0))', align=CENTER)
        put(ws, f'{L(cAc)}{r}', f'=IF(OR({L(cPts)}{r}="",{L(cOf)}{r}=0),0,{L(cPts)}{r})', NUM0 and F_BASE, NUM0, CENTER)
        parrow = lambda k: f'{L(HOLE_COL0)}$4:{L(HOLE_COL0 + 17)}$4'
        rng = f'{h1}:{h18}'; prng = f'${L(HOLE_COL0)}$4:${L(HOLE_COL0 + 17)}$4'
        for col, cond in zip((cE, cB, cPa, cBo, cD), ('<=-2', '=-1', '=0', '=1', '>=2')):
            op = cond[:2] if cond[1] == '=' else cond[0]
            val = cond[len(op):]
            put(ws, f'{L(col)}{r}', f'=IF(COUNT({rng})<18,"",SUMPRODUCT(--(({rng})-{prng}{op}{val})))', align=CENTER)
        for c in range(1, cD + 1):
            ws.cell(row=r, column=c).border = B_BOT
    # Colores por golpe vs par
    hr = f'{L(HOLE_COL0)}{r0}:{L(HOLE_COL0 + 17)}{r1}'
    a = f'{L(HOLE_COL0)}{r0}'; pa = f'{L(HOLE_COL0)}$4'
    rules = [(f'AND(ISNUMBER({a}),{a}-{pa}<=-2)', 'FFD700', '000000'), (f'AND(ISNUMBER({a}),{a}-{pa}=-1)', '2E7D32', 'FFFFFF'),
             (f'AND(ISNUMBER({a}),{a}-{pa}=1)', 'F6C7A8', '000000'), (f'AND(ISNUMBER({a}),{a}-{pa}>=2)', 'E8A0A0', '000000')]
    for formula, bg, fg in rules:
        ws.conditional_formatting.add(hr, FormulaRule(formula=[formula], fill=PatternFill('solid', fgColor=bg),
                                                      font=Font(name='Arial', color=fg, bold=True)))
    # Bloque de stats
    rs = r1 + 2
    put(ws, f'B{rs}', 'ESTADÍSTICAS DE LA FECHA', F_BOLD)
    labels = [('Tarjetas', f'=COUNT({L(cG)}{r0}:{L(cG)}{r1})', NUM0),
              ('Gross promedio', f'=IFERROR(AVERAGE({L(cG)}{r0}:{L(cG)}{r1}),"")', '0.0'),
              ('Neto promedio', f'=IFERROR(AVERAGE({L(cN)}{r0}:{L(cN)}{r1}),"")', '0.0'),
              ('Mejor neto', f'=IFERROR(MIN({L(cN)}{r0}:{L(cN)}{r1}),"")', NUM0),
              ('Mejor gross', f'=IFERROR(MIN({L(cG)}{r0}:{L(cG)}{r1}),"")', NUM0)] + \
             [(lab, f'=SUM({L(col)}{r0}:{L(col)}{r1})', NUM0) for lab, col in
              zip(('Eagles o mejor', 'Birdies', 'Pares', 'Bogeys', 'Dobles o peor'), (cE, cB, cPa, cBo, cD))]
    for i, (lab, fm, fmt) in enumerate(labels):
        put(ws, f'B{rs + 1 + i}', lab); put(ws, f'C{rs + 1 + i}', fm, F_BOLD, fmt, CENTER)
    ws.freeze_panes = 'D6'
    FECHA_SHEETS[n] = (name, r0, r1, cG, cN, cPts, cAc, cPos)

# ════════════════════════════════════════════════════════════════════
# MATCH_LOG (inputs de matchs)
# ════════════════════════════════════════════════════════════════════
ml = wb.create_sheet('Match_Log')
setup(ml, 'Match Play — registro de matchs', 'Un match por fila. Azul = input. Dif hoyos en magnitud positiva; el ganador define el signo.',
      {'A': 7, 'B': 6, 'C': 14, 'D': 14, 'E': 14, 'F': 14, 'G': 9, 'H': 8, 'I': 9, 'J': 9, 'K': 10, 'L': 10, 'M': 10})
header(ml, 4, 1, ['Fecha', 'Tipo', 'La Cele 1', 'La Cele 2', 'Rojo 1', 'Rojo 2', 'Ganador', 'Dif hoyos',
                  'Pts La Cele', 'Pts Rojo', 'Dif (La Cele)', 'Pts c/u Cele', 'Pts c/u Rojo'])
r = 5
for f in fechas:
    for m in f.get('matchs') or []:
        g = [x for x in (m.get('gris') or [])] + ['', '']
        rr = [x for x in (m.get('rojo') or [])] + ['', '']
        gan = {'g': 'g', 'r': 'r', 'empate': 'empate'}[m['ganador']]
        vals = [f['num'], m['tipo'], g[0], g[1], rr[0], rr[1], gan, abs(m.get('difHoyos') or 0)]
        for k, v in enumerate(vals):
            put(ml, f'{L(1 + k)}{r}', v if v != '' else None, F_IN, align=CENTER)
        put(ml, f'I{r}', f'=IF(G{r}="g",{P["PW"]},IF(G{r}="empate",{P["PE"]},0))', align=CENTER, fmt='0.0#')
        put(ml, f'J{r}', f'=IF(G{r}="r",{P["PW"]},IF(G{r}="empate",{P["PE"]},0))', align=CENTER, fmt='0.0#')
        put(ml, f'K{r}', f'=IF(G{r}="g",H{r},IF(G{r}="r",-H{r},0))', align=CENTER, fmt=NUMS)
        put(ml, f'L{r}', f'=I{r}*IF(B{r}="fb",{P["PFB"]},{P["PIND"]})', align=CENTER, fmt='0.0#')
        put(ml, f'M{r}', f'=J{r}*IF(B{r}="fb",{P["PFB"]},{P["PIND"]})', align=CENTER, fmt='0.0#')
        for c in range(1, 14):
            ml.cell(row=r, column=c).border = B_BOT
        r += 1
ML_LAST = 200  # rangos con espacio para F9/F10
put(ml, f'A{r + 1}', 'Para cargar F9/F10: agregar filas debajo con el mismo formato (las fórmulas I:M se copian).', F_SUB)
ml.freeze_panes = 'A5'
MLR = lambda c: f'Match_Log!${c}$5:${c}${ML_LAST}'
# fórmulas I:M pre-cargadas hasta ML_LAST para que F9/F10 sean solo input
for rr_ in range(r, ML_LAST + 1):
    pass

# ════════════════════════════════════════════════════════════════════
# MEDAL (acumulado individual)
# ════════════════════════════════════════════════════════════════════
FN = list(range(1, 11))
med = wb.create_sheet('Medal', 2)
setup(med, 'Medal — acumulado individual', 'Pts por fecha tomados de cada hoja FN (columna Acumula). Solo oficiales; Gatto, Alejandro en fila aparte.',
      {'A': 13, 'B': 24, 'C': 9})
header(med, 4, 1, ['ID', 'Jugador', 'Equipo'] + [f'F{n}' for n in FN] + ['TOTAL', 'Puesto', 'Fechas', 'Clave orden'])
cTot = 4 + len(FN); cRk = cTot + 1; cFj = cTot + 2
for c in range(4, cFj + 1):
    med.column_dimensions[L(c)].width = 8
med.column_dimensions[L(cTot)].width = 10


def fecha_pts_formula(pid_ref, n, col_key):
    if n not in FECHA_SHEETS:
        return 0
    name, r0, r1, cG, cN, cPts, cAc, cPos = FECHA_SHEETS[n]
    col = {'acum': cAc, 'pts': cPts}[col_key]
    return f"=SUMIFS('{name}'!${L(col)}${r0}:${L(col)}${r1},'{name}'!$A${r0}:$A${r1},{pid_ref})"


rows_med = OFICIALES + [SUP_ESP]
for i, (pid, nm, nick, t) in enumerate(rows_med):
    r = 5 + i + (1 if pid == 'gatto_ale' else 0)
    put(med, f'A{r}', pid, F_LINK); put(med, f'B{r}', nm + (' (sup)' if not t else ''), F_BOLD if t else F_SUB)
    put(med, f'C{r}', TEAM_TXT.get(t, 'SUP'), align=CENTER)
    for k, n in enumerate(FN):
        fm = fecha_pts_formula(f'$A{r}', n, 'pts' if pid == 'gatto_ale' else 'acum')
        put(med, f'{L(4 + k)}{r}', fm, F_LINK, NUM0, CENTER)
    put(med, f'{L(cTot)}{r}', f'=SUM(D{r}:{L(cTot - 1)}{r})', F_BOLD, NUM0, CENTER, FILL_TOT)
    if t:
        put(med, f'{L(cRk)}{r}', f'=RANK({L(cTot)}{r},${L(cTot)}$5:${L(cTot)}$20)', align=CENTER)
    fj = []
    for n in FN:
        if n in FECHA_SHEETS:
            name, r0, r1, cG, cN, *_ = FECHA_SHEETS[n]
            fj.append(f"COUNTIFS('{name}'!$A${r0}:$A${r1},$A{r},'{name}'!${L(cN)}${r0}:${L(cN)}${r1},\"<>\")")
    put(med, f'{L(cFj)}{r}', '=' + '+'.join(fj), align=CENTER)
    if t:
        put(med, f'{L(cFj + 1)}{r}', f'={L(cTot)}{r}+(100-ROW())/100000', F_SUB, '0.00000', CENTER)
    for c in range(1, cFj + 1):
        med.cell(row=r, column=c).border = B_BOT
# Ranking ordenado
rs = 24
put(med, f'B{rs}', 'RANKING MEDAL (ordenado)', F_BOLD)
header(med, rs + 1, 1, ['#', 'Jugador', 'Equipo', 'Total'])
for k in range(16):
    r = rs + 2 + k
    key = f'${L(cFj + 1)}$5:${L(cFj + 1)}$20'
    put(med, f'A{r}', k + 1, align=CENTER)
    m = f'MATCH(LARGE({key},{k + 1}),{key},0)'
    put(med, f'B{r}', f'=INDEX($B$5:$B$20,{m})', F_BOLD)
    put(med, f'C{r}', f'=INDEX($C$5:$C$20,{m})', align=CENTER)
    put(med, f'D{r}', f'=INDEX(${L(cTot)}$5:${L(cTot)}$20,{m})', F_BOLD, NUM0, CENTER)
med.freeze_panes = 'D5'

# ════════════════════════════════════════════════════════════════════
# MATCH (individual por jugador)
# ════════════════════════════════════════════════════════════════════
mt = wb.create_sheet('Match', 3)
setup(mt, 'Match Play — puntos individuales', 'Calculado desde Match_Log. Fourball 0,5 c/u al ganador (0,25 empate); individual 1 / 0,5.',
      {'A': 13, 'B': 24, 'C': 9})
header(mt, 4, 1, ['ID', 'Jugador', 'Equipo'] + [f'F{n}' for n in FN] + ['TOT Pts', 'TOT Dif', 'Puesto equipo'])
cTp = 4 + len(FN); cTd = cTp + 1; cRe = cTp + 2
for c in range(4, cRe + 1):
    mt.column_dimensions[L(c)].width = 8


def match_pts(pid_ref, fecha_ref):
    parts = []
    for slot, ptscol in (('C', 'L'), ('D', 'L'), ('E', 'M'), ('F', 'M')):
        parts.append(f'SUMIFS({MLR(ptscol)},{MLR("A")},{fecha_ref},{MLR(slot)},{pid_ref})')
    return '=' + '+'.join(parts)


def match_dif(pid_ref):
    g = [f'SUMIFS({MLR("K")},{MLR(s)},{pid_ref})' for s in ('C', 'D')]
    rj = [f'SUMIFS({MLR("K")},{MLR(s)},{pid_ref})' for s in ('E', 'F')]
    return '=' + '+'.join(g) + '-' + '-'.join(rj)


for i, (pid, nm, nick, t) in enumerate(rows_med):
    r = 5 + i + (1 if pid == 'gatto_ale' else 0)
    put(mt, f'A{r}', pid, F_LINK); put(mt, f'B{r}', nm + (' (sup)' if not t else ''), F_BOLD if t else F_SUB)
    put(mt, f'C{r}', TEAM_TXT.get(t, 'SUP'), align=CENTER)
    for k, n in enumerate(FN):
        put(mt, f'{L(4 + k)}{r}', match_pts(f'$A{r}', n), F_LINK, '0.0#;-0.0#;"-"', CENTER)
    put(mt, f'{L(cTp)}{r}', f'=SUM(D{r}:{L(cTp - 1)}{r})', F_BOLD, '0.0#', CENTER, FILL_TOT)
    put(mt, f'{L(cTd)}{r}', match_dif(f'$A{r}'), F_LINK, NUMS, CENTER)
    if t:
        # puesto dentro del equipo: pts, desempata dif
        put(mt, f'{L(cRe)}{r}',
            f'=COUNTIFS($C$5:$C$20,C{r},${L(cTp)}$5:${L(cTp)}$20,">"&{L(cTp)}{r})'
            f'+COUNTIFS($C$5:$C$20,C{r},${L(cTp)}$5:${L(cTp)}$20,{L(cTp)}{r},${L(cTd)}$5:${L(cTd)}$20,">"&{L(cTd)}{r})+1',
            align=CENTER)
    if t:
        put(mt, f'{L(cRe + 1)}{r}', f'={L(cTp)}{r}+{L(cTd)}{r}/1000+(100-ROW())/10000000', F_SUB, '0.0000000', CENTER)
    for c in range(1, cRe + 1):
        mt.cell(row=r, column=c).border = B_BOT
put(mt, f'{L(cRe + 1)}4', 'Clave orden general', F_HDR, fill=FILL_HDR, align=CENTER)
MT_KEY = f'Match!${L(cRe + 1)}$5:${L(cRe + 1)}$20'
rs = 24
put(mt, f'B{rs}', 'FINALISTAS F10 (#1 de cada equipo post F9: pts, desempata dif)', F_BOLD)
header(mt, rs + 1, 1, ['Equipo', 'Jugador', '', 'Pts', 'Dif'])
for k, eq in enumerate(('LA CELE', 'ROJO')):
    r = rs + 2 + k
    m = f'MATCH(1,INDEX(($C$5:$C$20="{eq}")*(${L(cRe)}$5:${L(cRe)}$20=1),0),0)'
    put(mt, f'A{r}', eq, F_BOLD)
    put(mt, f'B{r}', f'=INDEX($B$5:$B$20,{m})', F_BOLD)
    put(mt, f'D{r}', f'=INDEX(${L(cTp)}$5:${L(cTp)}$20,{m})', fmt='0.0#', align=CENTER)
    put(mt, f'E{r}', f'=INDEX(${L(cTd)}$5:${L(cTd)}$20,{m})', fmt=NUMS, align=CENTER)
# Resultado de la final F10 (la única fila de F10 en Match_Log es la final #1 vs #1)
rf = rs + 5
put(mt, f'B{rf}', 'FINAL F10 — RESULTADO', F_BOLD)
header(mt, rf + 1, 1, ['Puesto', 'Jugador', '', 'Pts', 'Dif'])
_gan = f'IFERROR(INDEX({MLR("G")},MATCH(10,{MLR("A")},0)),"")'
put(mt, f'A{rf + 2}', 'Campeón', F_BOLD)
put(mt, f'B{rf + 2}', f'=IF({_gan}="g",B{rs + 2},IF({_gan}="r",B{rs + 3},"Final pendiente"))', F_BOLD)
put(mt, f'A{rf + 3}', 'Subcampeón', F_BOLD)
put(mt, f'B{rf + 3}', f'=IF({_gan}="g",B{rs + 3},IF({_gan}="r",B{rs + 2},"Final pendiente"))', F_BOLD)
for k in (2, 3):
    put(mt, f'D{rf + k}', f'=INDEX(${L(cTp)}$5:${L(cTp)}$20,MATCH(B{rf + k},$B$5:$B$20,0))', fmt='0.0#', align=CENTER)
    put(mt, f'E{rf + k}', f'=INDEX(${L(cTd)}$5:${L(cTd)}$20,MATCH(B{rf + k},$B$5:$B$20,0))', fmt=NUMS, align=CENTER)
MT_CAMP, MT_SUB = f'Match!B{rf + 2}', f'Match!B{rf + 3}'
mt.freeze_panes = 'D5'

# ════════════════════════════════════════════════════════════════════
# COPA (equipos)
# ════════════════════════════════════════════════════════════════════
cp = wb.create_sheet('Copa', 4)
setup(cp, 'Copa Match Play — La Cele vs Rojo', 'Solo suman los matchs (Match_Log). La dif de hoyos desempata.', {'A': 22})
header(cp, 4, 1, ['Equipo'] + [f'F{n}' for n in FN] + ['TOTAL'])
cT = 2 + len(FN)
rows = [('La Cele — Pts', 'I', 1), ('Rojo — Pts', 'J', 1), ('La Cele — Dif hoyos', 'K', 1), ('Matchs jugados', 'A', 0)]
for i, (lab, col, _) in enumerate(rows):
    r = 5 + i
    put(cp, f'A{r}', lab, F_BOLD)
    for k, n in enumerate(FN):
        fm = (f'=COUNTIF({MLR("A")},{n})' if col == 'A' else f'=SUMIFS({MLR(col)},{MLR("A")},{n})')
        put(cp, f'{L(2 + k)}{r}', fm, F_LINK, NUMS if col == 'K' else '0.0#;-0.0#;"-"', CENTER)
    put(cp, f'{L(cT)}{r}', f'=SUM(B{r}:{L(cT - 1)}{r})', F_BOLD, NUMS if col == 'K' else '0.0#', CENTER, FILL_TOT)
for c in range(2, cT + 1):
    cp.column_dimensions[L(c)].width = 8
put(cp, 'A10', 'Diferencia La Cele (pts)', F_BOLD); put(cp, 'B10', f'={L(cT)}5-{L(cT)}6', F_BOLD, '+0.0#;-0.0#;0', CENTER)
put(cp, 'A11', 'Líder', F_BOLD)
put(cp, 'B11', f'=IF({L(cT)}5>{L(cT)}6,"LA CELE",IF({L(cT)}6>{L(cT)}5,"ROJO",IF({L(cT)}7>0,"LA CELE (dif hoyos)",IF({L(cT)}7<0,"ROJO (dif hoyos)","EMPATE"))))', F_BOLD)

# ════════════════════════════════════════════════════════════════════
# GROSS (premio: promedio mejores 7)
# ════════════════════════════════════════════════════════════════════
gr = wb.create_sheet('Gross', 5)
setup(gr, 'Gross — premio al mejor promedio de las mejores 7 tarjetas',
      'Gross de cada hoja FN. Las columnas 1°–7° toman las mejores tarjetas; el promedio vale como premio solo con 7 o más.', {'A': 13, 'B': 24, 'C': 9})
header(gr, 4, 1, ['ID', 'Jugador', 'Equipo'] + [f'F{n}' for n in FN] + ['Tarj.'] + [f'{k}°' for k in range(1, 8)] +
       ['Prom. mejores', 'Mejor', 'Elegible'])
cTj = 4 + len(FN); cB1 = cTj + 1; cAvg = cB1 + 7; cBest = cAvg + 1; cEl = cAvg + 2
for c in range(4, cEl + 1):
    gr.column_dimensions[L(c)].width = 7
gr.column_dimensions[L(cAvg)].width = 11; gr.column_dimensions[L(cEl)].width = 9
for i, (pid, nm, nick, t) in enumerate(rows_med):
    r = 5 + i + (1 if pid == 'gatto_ale' else 0)
    put(gr, f'A{r}', pid, F_LINK); put(gr, f'B{r}', nm + (' (sup)' if not t else ''), F_BOLD if t else F_SUB)
    put(gr, f'C{r}', TEAM_TXT.get(t, 'SUP'), align=CENTER)
    for k, n in enumerate(FN):
        if n in FECHA_SHEETS:
            name, r0, r1, cG, *_ = FECHA_SHEETS[n]
            fm = f"=IFERROR(INDEX('{name}'!${L(cG)}${r0}:${L(cG)}${r1},MATCH($A{r},'{name}'!$A${r0}:$A${r1},0)),\"\")"
            put(gr, f'{L(4 + k)}{r}', fm, F_LINK, NUM0, CENTER)
    rng = f'D{r}:{L(cTj - 1)}{r}'
    put(gr, f'{L(cTj)}{r}', f'=COUNT({rng})', align=CENTER)
    for k in range(7):
        put(gr, f'{L(cB1 + k)}{r}', f'=IF({L(cTj)}{r}>={k + 1},SMALL({rng},{k + 1}),"")', align=CENTER, fmt=NUM0)
    put(gr, f'{L(cAvg)}{r}', f'=IF({L(cTj)}{r}=0,"",AVERAGE({L(cB1)}{r}:{L(cB1 + 6)}{r}))', F_BOLD, '0.0', CENTER, FILL_TOT)
    put(gr, f'{L(cBest)}{r}', f'=IF({L(cTj)}{r}=0,"",MIN({rng}))', align=CENTER, fmt=NUM0)
    put(gr, f'{L(cEl)}{r}', ('="No compite"' if not t else
                            f'=IF({L(cTj)}{r}>={P["BESTN"]},"Sí",IF({L(cTj)}{r}+COUNTIF(Fixture!$H$5:$H$14,"Pendiente")>={P["BESTN"]},"Puede","No llega"))'),
        align=CENTER)
    if t:
        put(gr, f'{L(cEl + 1)}{r}', f'=IF({L(cEl)}{r}="Sí",{L(cAvg)}{r},"")', F_SUB, '0.0', CENTER)
    for c in range(1, cEl + 1):
        gr.cell(row=r, column=c).border = B_BOT
put(gr, f'{L(cEl + 1)}4', 'Prom. si elegible', F_HDR, fill=FILL_HDR, align=CENTER)
GR_EL = f'Gross!${L(cEl + 1)}$5:${L(cEl + 1)}$20'
gr.freeze_panes = 'D5'

# ════════════════════════════════════════════════════════════════════
# FIXTURE
# ════════════════════════════════════════════════════════════════════
fx = wb.create_sheet('Fixture', 6)
setup(fx, 'Fixture 2026', 'Fuente: data/fixture.json. Estado se actualiza a mano.', {'A': 5, 'B': 22, 'C': 16, 'D': 20, 'E': 28, 'F': 22, 'G': 8, 'H': 34})
header(fx, 4, 1, ['F#', 'Fecha', 'Cancha', 'Modalidad', 'Criterio', 'Organizadores', 'Mult.', 'Estado'])
canchas = {f['num']: f.get('cancha', '') for f in fechas}
estado = {4: 'Jugada (solo match — niebla)', 8: 'Jugada (reprogramada del 03-Oct, sin multas)',
          9: 'Jugada (GIRA, sin multas)', 10: 'Suspendida por tormenta: solo la final de match (no cuenta Medal ni Gross)'}
for i, fxr in enumerate(fixture):
    r = 5 + i; n = fxr['num']
    vals = [n, fxr['fecha'], canchas.get(n, 'Punta Cana (GIRA)' if n >= 9 else ''), fxr['modalidad'], fxr['criterio'], fxr['organizadores']]
    for k, v in enumerate(vals):
        put(fx, f'{L(1 + k)}{r}', v, F_IN)
    put(fx, f'G{r}', f'={P["M9"] if n == 9 else P["M10"] if n == 10 else P["M1"]}', F_LINK, '0.0"x"', CENTER)
    put(fx, f'H{r}', estado.get(n, 'Jugada' if n in canchas else 'Pendiente'), F_IN)

# Cruces ya definidos de fechas pendientes (campo opcional "cruces" en data/fixture.json)
NOMBRE_CORTO = {'gatto': 'Gatto, Mariano', 'gatto_ale': 'Gatto, Alejandro (sup)', 'sup_diazandrade': 'Díaz Andrade, Juampi (sup)'}
r = 5 + len(fixture) + 2
for fxr in fixture:
    if not fxr.get('cruces'):
        continue
    put(fx, f'A{r}', f"F{fxr['num']} — Cruces definidos ({fxr['modalidad']})", F_BOLD); r += 1
    header(fx, r, 1, ['Match', 'La Cele', '', 'vs', 'Rojo', '', 'Seeds', 'Nota']); r += 1
    for c in fxr['cruces']:
        nm = lambda i: NOMBRE_CORTO.get(i, i.capitalize())
        g = c['gris'] + [''] * (2 - len(c['gris'])); rj = c['rojo'] + [''] * (2 - len(c['rojo']))
        vals = [c['match'], nm(g[0]), nm(g[1]) if g[1] else '', 'vs', nm(rj[0]), nm(rj[1]) if rj[1] else '', c.get('seeds', ''), c.get('nota', '')]
        for k, v in enumerate(vals):
            put(fx, f'{L(1 + k)}{r}', v, F_IN)
        r += 1
    r += 1

# ════════════════════════════════════════════════════════════════════
# RECAUDACIÓN (pozo y premios) — fuente: data/recaudacion.json
# ════════════════════════════════════════════════════════════════════
rc = wb.create_sheet('Recaudación')
RCN = "'Recaudación'"
setup(rc, 'Recaudación 2026 — pozo y premios (USD)',
      'Fuente: data/recaudacion.json (lo que carga el backoffice). Azul = input. Multa por ausencia en Supuestos. '
      'Fechas reprogramadas oficialmente no generan multa (F8).',
      {'A': 13, 'B': 26, 'C': 10, 'D': 12})
header(rc, 4, 1, ['ID', 'Jugador', 'Equipo', 'Inscripción USD'] + [f'F{n} USD' for n in range(1, 11)] +
       ['Multas USD', 'Total USD', 'Ausencias'])
cMul = 15; cTotR = 16; cAus = 17
for c in range(5, cAus + 1):
    rc.column_dimensions[L(c)].width = 9
rc.column_dimensions[L(cMul)].width = 11; rc.column_dimensions[L(cTotR)].width = 11
for i, (pid, nm, nick, t) in enumerate(rows_med):
    r = 5 + i + (1 if pid == 'gatto_ale' else 0)
    d = recaud.get(pid, {})
    put(rc, f'A{r}', pid, F_LINK); put(rc, f'B{r}', nm + (' (sup)' if not t else ''), F_BOLD if t else F_SUB)
    put(rc, f'C{r}', TEAM_TXT.get(t, 'SUP'), align=CENTER)
    put(rc, f'D{r}', float(d.get('inscripcion') or 0), F_IN, NUM0, CENTER, FILL_IN)
    for n in range(1, 11):
        put(rc, f'{L(4 + n)}{r}', float(d.get(f'f{n}') or 0), F_IN, NUM0, CENTER, FILL_IN)
    put(rc, f'{L(cMul)}{r}', f'=SUM(E{r}:N{r})', F_BOLD, NUM0, CENTER)
    put(rc, f'{L(cTotR)}{r}', f'=D{r}+{L(cMul)}{r}', F_BOLD, NUM0, CENTER, FILL_TOT)
    put(rc, f'{L(cAus)}{r}', f'=COUNTIF(E{r}:N{r},">0")', align=CENTER, fmt=NUM0)
    for c in range(1, cAus + 1):
        rc.cell(row=r, column=c).border = B_BOT
RT = 24
put(rc, f'B{RT}', 'TOTAL', F_BOLD)
for c in range(4, cAus + 1):
    put(rc, f'{L(c)}{RT}', f'=SUM({L(c)}5:{L(c)}22)', F_BOLD, NUM0, CENTER, FILL_TOT)
rc.freeze_panes = 'D5'

# ── Pozo ──
R0 = 27
put(rc, f'B{R0}', 'POZO', F_BOLD)
header(rc, R0 + 1, 2, ['Concepto', '', 'USD', 'ARS'])
put(rc, f'B{R0 + 2}', 'Inscripciones'); put(rc, f'D{R0 + 2}', f'=D{RT}', F_LINK, NUM0, CENTER)
put(rc, f'B{R0 + 3}', 'Multas por ausencia'); put(rc, f'D{R0 + 3}', f'={L(cMul)}{RT}', F_LINK, NUM0, CENTER)
put(rc, f'B{R0 + 4}', 'Pozo total', F_BOLD); put(rc, f'D{R0 + 4}', f'=D{R0 + 2}+D{R0 + 3}', F_BOLD, NUM0, CENTER, FILL_TOT)
put(rc, f'B{R0 + 6}', 'Tipo de cambio MEP 01-Oct-2026 (ARS por USD)')
c = put(rc, f'D{R0 + 6}', None, F_IN, NUM2, CENTER, FILL_IN)
c.comment = Comment('Completar con el MEP del 01/10/2026 (reglamento: la inscripción se paga en pesos a ese tipo de cambio).', 'MGT')
MEP = f'$D${R0 + 6}'
for rr in (R0 + 2, R0 + 3, R0 + 4):
    put(rc, f'E{rr}', f'=IF({MEP}="","",D{rr}*{MEP})', F_BOLD if rr == R0 + 4 else F_BASE, NUM0, CENTER)
POZO = f'$D${R0 + 4}'

# ── Premios ──
P0 = R0 + 9
put(rc, f'B{P0}', 'PREMIOS (reglamento 2026 · % del pozo)', F_BOLD)
header(rc, P0 + 1, 2, ['Premio', '% pozo', 'USD', 'ARS', 'Ganador 2026'])
rc.column_dimensions['F'].width = 9
mkey = MT_KEY
premios = [
    ('Medal #1', 0.21, '=Medal!B26'), ('Medal #2', 0.13, '=Medal!B27'),
    ('Medal #3', 0.09, '=Medal!B28'), ('Medal #4', 0.06, '=Medal!B29'),
    ('Match individual #1', 0.13, f'={MT_CAMP}'),
    ('Match individual #2', 0.08, f'={MT_SUB}'),
    ('Gross #1', 0.03, f'=IFERROR(INDEX(Gross!$B$5:$B$20,MATCH(MIN({GR_EL}),{GR_EL},0)),"Nadie llega a 7")'),
    ('Equipo campeón Match Play', 0.27, '=Copa!B11'),
]
for i, (lab, pct, who) in enumerate(premios):
    r = P0 + 2 + i
    put(rc, f'B{r}', lab)
    put(rc, f'C{r}', pct, F_IN, '0%', CENTER, FILL_IN)
    put(rc, f'D{r}', f'={POZO}*C{r}', F_BASE, NUM0, CENTER)
    put(rc, f'E{r}', f'=IF({MEP}="","",D{r}*{MEP})', F_BASE, NUM0, CENTER)
    put(rc, f'F{r}', who, F_LINK)
    for cc in range(2, 7):
        rc.cell(row=r, column=cc).border = B_BOT
rT = P0 + 2 + len(premios)
put(rc, f'B{rT}', 'TOTAL', F_BOLD)
put(rc, f'C{rT}', f'=SUM(C{P0 + 2}:C{rT - 1})', F_BOLD, '0%', CENTER, FILL_TOT)
put(rc, f'D{rT}', f'=SUM(D{P0 + 2}:D{rT - 1})', F_BOLD, NUM0, CENTER, FILL_TOT)
put(rc, f'E{rT}', f'=IF({MEP}="","",D{rT}*{MEP})', F_BOLD, NUM0, CENTER, FILL_TOT)
put(rc, f'F{rT}', f'=IF(ROUND(C{rT},4)=1,"✓ reparte el 100%","⚠ los % no suman 100%")', F_SUB)
put(rc, f'B{rT + 2}', '• Temporada cerrada. La F10 se suspendió por tormenta: no cuenta para Medal ni Gross; Match individual = final F10 '
    '(Guevara le ganó a Molinario en el hoyo 17). Gross exige 7 tarjetas.', F_SUB)
put(rc, f'B{rT + 3}', '• Montos en ARS: se completan solos al cargar el MEP del 01-Oct-2026 arriba.', F_SUB)

# ════════════════════════════════════════════════════════════════════
# RESUMEN (portada)
# ════════════════════════════════════════════════════════════════════
rsm = wb.create_sheet('Resumen', 0)
setup(rsm, 'MILICIA GOLF TOUR 2026 — Estado del torneo', 'Temporada cerrada · F10 suspendida por tormenta (no cuenta Medal ni Gross; solo se jugó la final de match). Todo enlazado a las hojas de cálculo.',
      {'A': 4, 'B': 30, 'C': 12, 'D': 4, 'E': 30, 'F': 12, 'G': 12})
put(rsm, 'B4', 'COPA MATCH PLAY', F_BOLD)
put(rsm, 'B5', 'La Cele'); put(rsm, 'C5', f'=Copa!{L(cT)}5', F_LINK, '0.0#', CENTER)
put(rsm, 'B6', 'Rojo'); put(rsm, 'C6', f'=Copa!{L(cT)}6', F_LINK, '0.0#', CENTER)
put(rsm, 'B7', 'Dif hoyos La Cele'); put(rsm, 'C7', f'=Copa!{L(cT)}7', F_LINK, NUMS, CENTER)
put(rsm, 'B8', 'Campeón'); put(rsm, 'C8', '=Copa!B11', F_LINK)
put(rsm, 'E4', 'MATCH INDIVIDUAL — FINAL F10', F_BOLD)
put(rsm, 'E5', f'="Campeón: "&{MT_CAMP}', F_LINK); put(rsm, 'F5', f'={MT_CAMP.replace("!B", "!D")}', F_LINK, '0.0#', CENTER)
put(rsm, 'E6', f'="Subcampeón: "&{MT_SUB}', F_LINK); put(rsm, 'F6', f'={MT_SUB.replace("!B", "!D")}', F_LINK, '0.0#', CENTER)
put(rsm, 'E9', 'GROSS #1', F_BOLD)
put(rsm, 'F9', f'=IFERROR(INDEX(Gross!$B$5:$B$20,MATCH(MIN({GR_EL}),{GR_EL},0)),"")', F_LINK)
put(rsm, 'E8', 'POZO TOTAL (USD)', F_BOLD); put(rsm, 'F8', f"={RCN}!{POZO}", F_LINK, NUM0, CENTER)
put(rsm, 'B11', 'MEDAL — TOP 10', F_BOLD)
header(rsm, 12, 2, ['Jugador', 'Pts'])
for k in range(10):
    r = 13 + k
    put(rsm, f'A{r}', k + 1, align=CENTER)
    put(rsm, f'B{r}', f'=Medal!B{26 + k}', F_LINK); put(rsm, f'C{r}', f'=Medal!D{26 + k}', F_LINK, NUM0, CENTER)

# Orden de hojas
order = ['Resumen', 'Supuestos', 'Medal', 'Match', 'Copa', 'Gross', 'Recaudación'] + [FECHA_SHEETS[n][0] for n in sorted(FECHA_SHEETS)] + \
        ['Match_Log', 'Fixture', 'Jugadores', 'Historico']
wb._sheets = [wb[s] for s in order]
wb.active = 0
wb.save(OUT)
print('ok', OUT)
