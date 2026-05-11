/* =====================================================================
 * MGT Master Excel Generator
 * ---------------------------------------------------------------------
 * Genera un workbook XLSX "estilo Portfolio Analyst" del Milicia Golf
 * Tour, leyendo el estado global del index.html (PLAYERS, fechas,
 * MEDAL_PTS, etc.) y devolviendo un archivo descargable.
 *
 * Requisitos previos en runtime:
 *   - window.ExcelJS cargado.
 *   - Variables globales: PLAYERS, SUPLENTES_CONOCIDOS, fechas,
 *     MEDAL_PTS, F9_MULT, F10_MULT, PAR, fixtureData.
 *
 * Uso: await generateMasterExcel();
 * ===================================================================== */

(function (global) {
  'use strict';

  // ------------------------------------------------------------------
  // Paleta visual (estilo Portfolio Analyst)
  // ------------------------------------------------------------------
  const COLOR = {
    navy:       'FF0A1430',
    navySoft:   'FF142244',
    gold:       'FFC9A84C',
    goldSoft:   'FFE7D38A',
    grayLight:  'FFEDEEF1',
    grayMid:    'FF6A6E78',
    grayTeam:   'FF8A8E96',
    redTeam:    'FFB33A3A',
    white:      'FFFFFFFF',
    black:      'FF101010',
    eagle:      'FF2BB673', // verde
    birdie:     'FF7FC8E8', // celeste
    par:        'FFFFFFFF', // blanco
    bogey:      'FFFFE08A', // amarillo
    doubleBog:  'FFE57373', // rojo suave
    pendiente:  'FFFFF2CC',
  };

  const PAR_DEFAULT = [5,3,4,5,4,4,3,4,4, 4,5,4,4,3,4,4,3,5];
  const HDCP_CAP = 26;
  const TEAM_LABEL = { g: 'GRIS', r: 'ROJO' };

  // ------------------------------------------------------------------
  // Helpers de acceso al scope global
  // ------------------------------------------------------------------
  function _g(name, fallback) {
    if (typeof global[name] !== 'undefined') return global[name];
    return fallback;
  }
  function _getPlayers()      { return _g('PLAYERS', []); }
  function _getFechas()       { return _g('fechas', []); }
  function _getMedalPts()     {
    return _g('MEDAL_PTS', [500,300,200,150,120,100,90,80,75,70,20,20,20,20,0,0]);
  }
  function _getF9Mult()       { return _g('F9_MULT', 1.5); }
  function _getF10Mult()      { return _g('F10_MULT', 2);   }
  function _getDefaultPar()   { return _g('PAR', PAR_DEFAULT); }
  function _getFixture()      { return _g('fixtureData', null); }
  function _getSuplentesConocidos() { return _g('SUPLENTES_CONOCIDOS', []); }

  /** Lista de IDs oficiales (16). */
  function _officialIds() {
    return _getPlayers().map(p => p.id);
  }

  /** Devuelve player por id, o null. */
  function _playerById(id) {
    return _getPlayers().find(p => p.id === id) || null;
  }

  /** "Apellido, Nombre" - asume PLAYERS.name ya viene en ese formato. */
  function _displayName(id) {
    const p = _playerById(id);
    if (p) return p.name;
    const sup = _getSuplentesConocidos().find(s => s.id === id);
    if (sup) return sup.name;
    return id;
  }

  function _isOfficial(id) {
    return !!_playerById(id);
  }

  // ------------------------------------------------------------------
  // Helpers de estilo
  // ------------------------------------------------------------------

  /** Aplica el estilo de encabezado principal a una celda. */
  function _applyHeaderStyle(cell) {
    cell.font = { bold: true, color: { argb: COLOR.gold }, size: 11 };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.navy } };
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
    cell.border = {
      bottom: { style: 'medium', color: { argb: COLOR.gold } },
    };
  }

  /** Estilo de "section title" (más grande, fondo navy). */
  function _applySectionTitle(cell) {
    cell.font = { bold: true, color: { argb: COLOR.gold }, size: 14 };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.navy } };
    cell.alignment = { horizontal: 'left', vertical: 'middle', indent: 1 };
  }

  /** Pinta una celda con el color del equipo (g/r). */
  function _applyTeamFill(cell, team) {
    const fg = team === 'g' ? COLOR.grayTeam
             : team === 'r' ? COLOR.redTeam
             : COLOR.grayLight;
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: fg } };
    cell.font = Object.assign({}, cell.font, {
      color: { argb: COLOR.white },
      bold: true,
    });
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
  }

  /** Borde fino inferior (separador). */
  function _applyBottomBorder(cell, color) {
    cell.border = Object.assign({}, cell.border, {
      bottom: { style: 'thin', color: { argb: color || COLOR.grayMid } },
    });
  }

  /**
   * Devuelve color de fondo según score vs par del hoyo.
   * (Se usa para set estático; ExcelJS soporta conditional formatting
   *  pero acá lo aplicamos por celda directo, más simple y portable.)
   */
  function _holeColorForScore(score, par) {
    if (score === null || score === undefined || score === '') return null;
    const diff = score - par;
    if (diff <= -2) return COLOR.eagle;
    if (diff === -1) return COLOR.birdie;
    if (diff === 0)  return COLOR.par;
    if (diff === 1)  return COLOR.bogey;
    return COLOR.doubleBog;
  }

  /** Aplica color de hoyo a una celda (score vs par). */
  function _applyHoleColor(cell, score, par) {
    const c = _holeColorForScore(score, par);
    if (!c) return;
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: c } };
    cell.alignment = { horizontal: 'center', vertical: 'middle' };
    cell.font = { bold: c === COLOR.eagle || c === COLOR.doubleBog,
                  color: { argb: COLOR.black } };
  }

  /**
   * (Opcional) Aplica conditional formatting de score vs par a un rango.
   * NOTA: ExcelJS soporta conditionalFormattings pero para mantener simple
   * preferimos pintar por celda. Esta función queda como TODO.
   */
  function _applyHoleColorCondFormat(ws, range, parArr) {
    // TODO: convertir a conditionalFormattings nativos si hace falta
    // mantener dinámica la coloración al editar.
  }

  /** Formatea número entero o "-" si null. */
  function _intOrDash(v) {
    return (v === null || v === undefined || v === '') ? '' : v;
  }

  // ------------------------------------------------------------------
  // Cálculos auxiliares
  // ------------------------------------------------------------------

  /** Hdcp aplicado con cap 26. */
  function _hdcpAplicado(h) {
    if (h === null || h === undefined || isNaN(h)) return 0;
    return Math.min(Number(h), HDCP_CAP);
  }

  /**
   * Calcula posiciones netas de oficiales en una fecha. Devuelve mapa
   * { playerId: { pos, pts, neto, gross } } resolviendo empates con
   * promedio de pts y "fecha vacante" si pos 1 es no-oficial.
   */
  function _calcMedalFecha(fechaObj) {
    const result = {};
    if (!fechaObj || !fechaObj.scorecard) return result;
    const oficiales = fechaObj.scorecard.filter(s => _isOfficial(s.id) && s.id !== 'gatto_ale');
    if (!oficiales.length) return result;

    // Verificar vacante: si pos 1 (neto mínimo) global incluye suplente.
    const allNet = [...fechaObj.scorecard].sort((a,b) => (a.neto||999) - (b.neto||999));
    const vacante = allNet.length && !_isOfficial(allNet[0].id);

    const sorted = [...oficiales].sort((a,b) => (a.neto||999) - (b.neto||999));
    const tabla = _getMedalPts();
    const mult = fechaObj.num === 9 ? _getF9Mult()
               : fechaObj.num === 10 ? _getF10Mult()
               : 1;

    // Agrupar por neto (empates)
    let i = 0;
    while (i < sorted.length) {
      let j = i;
      while (j < sorted.length && sorted[j].neto === sorted[i].neto) j++;
      // Empate de [i..j-1]
      const ptsSum = sorted.slice(i, j).reduce((acc, _, k) => {
        const idx = i + k;
        return acc + (tabla[idx] || 0);
      }, 0);
      const ptsAvg = (ptsSum / (j - i)) * mult;
      for (let k = i; k < j; k++) {
        result[sorted[k].id] = {
          pos: i + 1,
          pts: ptsAvg,
          gross: sorted[k].gross,
          neto: sorted[k].neto,
          empate: (j - i) > 1,
          vacante: vacante,
        };
      }
      i = j;
    }
    return result;
  }

  /** Devuelve el par a usar para una fecha (override o default). */
  function _parFor(fechaObj) {
    if (fechaObj && Array.isArray(fechaObj.par) && fechaObj.par.length === 18) {
      return fechaObj.par;
    }
    return _getDefaultPar();
  }

  // ==================================================================
  // BUILDERS POR HOJA
  // ==================================================================

  /**
   * Hoja Dashboard — resumen visual con KPIs y top rankings.
   */
  function _buildDashboard(wb) {
    const ws = wb.addWorksheet('Dashboard', { views: [{ showGridLines: false }] });
    ws.properties.defaultRowHeight = 18;

    // Anchos
    ws.columns = Array.from({ length: 12 }, (_, i) => ({ width: i === 1 ? 28 : 14 }));

    // Título
    ws.mergeCells('A1:L2');
    const t = ws.getCell('A1');
    t.value = `MILICIA GOLF TOUR — Temporada ${new Date().getFullYear()}`;
    t.font = { bold: true, color: { argb: COLOR.gold }, size: 22, name: 'Calibri' };
    t.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.navy } };
    t.alignment = { horizontal: 'center', vertical: 'middle' };
    ws.getRow(1).height = 30;
    ws.getRow(2).height = 30;

    // Subtítulo
    ws.mergeCells('A3:L3');
    const sub = ws.getCell('A3');
    const now = new Date();
    sub.value = `Última actualización: ${now.toISOString().slice(0,10)} ${now.toTimeString().slice(0,5)}`;
    sub.font = { italic: true, color: { argb: COLOR.grayMid }, size: 10 };
    sub.alignment = { horizontal: 'center' };

    // KPIs
    const fechas = _getFechas();
    const jugadas = fechas.filter(f => !f.pendiente).length;
    const proxima = fechas.find(f => f.pendiente);

    const kpiRow = 5;
    const kpis = [
      { label: 'FECHAS JUGADAS', value: `${jugadas} / ${fechas.length || 10}` },
      { label: 'LÍDER MEDAL',    value: { formula: `INDEX('Acumulado Medal'!B:B,2)&" ("&TEXT(INDEX('Acumulado Medal'!N:N,2),"#,##0")&" pts)"` } },
      { label: 'EQUIPO LÍDER',   value: { formula: `IF('Match History'!Z1>0,"GRIS","ROJO")` } }, // simbólico, lo recalculamos abajo
      { label: 'PRÓXIMA FECHA',  value: proxima ? `F${proxima.num} — ${proxima.fecha}` : '—' },
    ];
    kpis.forEach((k, idx) => {
      const col = 1 + idx * 3;
      const labelCell = ws.getCell(kpiRow, col);
      const valCell = ws.getCell(kpiRow + 1, col);
      ws.mergeCells(kpiRow, col, kpiRow, col + 2);
      ws.mergeCells(kpiRow + 1, col, kpiRow + 1, col + 2);
      labelCell.value = k.label;
      labelCell.font = { bold: true, size: 9, color: { argb: COLOR.gold } };
      labelCell.alignment = { horizontal: 'center' };
      labelCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.navy } };
      valCell.value = k.value;
      valCell.font = { bold: true, size: 14, color: { argb: COLOR.navy } };
      valCell.alignment = { horizontal: 'center', vertical: 'middle' };
      valCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.grayLight } };
      ws.getRow(kpiRow + 1).height = 28;
    });

    // Top 5 Medal
    const topMedalStart = 9;
    ws.mergeCells(topMedalStart, 1, topMedalStart, 4);
    const tm = ws.getCell(topMedalStart, 1);
    tm.value = 'TOP 5 RANKING MEDAL';
    _applySectionTitle(tm);
    ws.getRow(topMedalStart).height = 22;

    const medalHdrs = ['#', 'Jugador', 'Equipo', 'Pts Total'];
    medalHdrs.forEach((h, i) => {
      const c = ws.getCell(topMedalStart + 1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    for (let i = 0; i < 5; i++) {
      const r = topMedalStart + 2 + i;
      ws.getCell(r, 1).value = i + 1;
      // Lee de la fila i+2 de Acumulado Medal (header en row 1).
      ws.getCell(r, 2).value = { formula: `IFERROR('Acumulado Medal'!B${i + 2},"")` };
      ws.getCell(r, 3).value = { formula: `IFERROR('Acumulado Medal'!C${i + 2},"")` };
      const pts = ws.getCell(r, 4);
      pts.value = { formula: `IFERROR('Acumulado Medal'!N${i + 2},0)` };
      pts.numFmt = '#,##0.0';
      pts.font = { bold: true };
    }

    // Top 5 Gross
    const topGrossStart = 9;
    const gC = 6;
    ws.mergeCells(topGrossStart, gC, topGrossStart, gC + 3);
    const tg = ws.getCell(topGrossStart, gC);
    tg.value = 'TOP 5 GROSS PROMEDIO';
    _applySectionTitle(tg);
    ['#', 'Jugador', 'Equipo', 'Avg Gross'].forEach((h, i) => {
      const c = ws.getCell(topGrossStart + 1, gC + i);
      c.value = h;
      _applyHeaderStyle(c);
    });
    for (let i = 0; i < 5; i++) {
      const r = topGrossStart + 2 + i;
      ws.getCell(r, gC).value = i + 1;
      // Estadísticas hoja: cols A=Nombre, B=Equipo, E=AvgGross (ver _buildEstadisticas)
      // Para top 5 ordenado, hacemos un LARGE/INDEX-MATCH manual:
      ws.getCell(r, gC + 1).value = { formula:
        `IFERROR(INDEX(Estadísticas!A:A,MATCH(SMALL(Estadísticas!E$2:E$20,${i + 1}),Estadísticas!E:E,0)),"")` };
      ws.getCell(r, gC + 2).value = { formula:
        `IFERROR(INDEX(Estadísticas!B:B,MATCH(SMALL(Estadísticas!E$2:E$20,${i + 1}),Estadísticas!E:E,0)),"")` };
      const av = ws.getCell(r, gC + 3);
      av.value = { formula: `IFERROR(SMALL(Estadísticas!E$2:E$20,${i + 1}),"")` };
      av.numFmt = '0.0';
    }

    // Match Play box
    const mStart = 17;
    ws.mergeCells(mStart, 1, mStart, 8);
    const mt = ws.getCell(mStart, 1);
    mt.value = 'MATCH PLAY — EQUIPOS';
    _applySectionTitle(mt);
    ws.getRow(mStart).height = 22;

    ['Equipo', 'Pts', 'Dif'].forEach((h, i) => {
      const c = ws.getCell(mStart + 1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    // Gris
    const gRow = mStart + 2;
    ws.getCell(gRow, 1).value = 'GRIS';
    _applyTeamFill(ws.getCell(gRow, 1), 'g');
    ws.getCell(gRow, 2).value = { formula: `IFERROR(SUM('Match History'!J:J),0)` };
    ws.getCell(gRow, 2).numFmt = '0.0';
    ws.getCell(gRow, 3).value = { formula: `B${gRow}-B${gRow + 1}` };
    ws.getCell(gRow, 3).numFmt = '+0.0;-0.0;0.0';
    // Rojo
    const rRow = mStart + 3;
    ws.getCell(rRow, 1).value = 'ROJO';
    _applyTeamFill(ws.getCell(rRow, 1), 'r');
    ws.getCell(rRow, 2).value = { formula: `IFERROR(SUM('Match History'!K:K),0)` };
    ws.getCell(rRow, 2).numFmt = '0.0';
    ws.getCell(rRow, 3).value = { formula: `B${rRow}-B${gRow}` };
    ws.getCell(rRow, 3).numFmt = '+0.0;-0.0;0.0';

    // Footer
    const footRow = 24;
    ws.mergeCells(footRow, 1, footRow, 12);
    const f = ws.getCell(footRow, 1);
    f.value = 'Generado por MGT Master Excel Generator — datos fuente: index.html / Supabase';
    f.font = { italic: true, size: 8, color: { argb: COLOR.grayMid } };
    f.alignment = { horizontal: 'center' };

    ws.views = [{ state: 'frozen', xSplit: 0, ySplit: 4, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja Setup — jugadores, hdcps, constantes, tabla de pts medal.
   */
  function _buildSetup(wb) {
    const ws = wb.addWorksheet('Setup', { views: [{ showGridLines: false }] });

    ws.columns = [
      { header: 'ID',           key: 'id',    width: 14 },
      { header: 'Nombre',       key: 'name',  width: 26 },
      { header: 'Equipo',       key: 'team',  width: 10 },
      { header: 'Hdcp Index',   key: 'hdc',   width: 12 },
      { header: 'Hdcp Aplicado',key: 'hcap',  width: 14 },
    ];
    ws.getRow(1).eachCell(c => _applyHeaderStyle(c));
    ws.getRow(1).height = 24;

    const players = _getPlayers();
    players.forEach((p, idx) => {
      const r = ws.addRow({
        id: p.id, name: p.name, team: TEAM_LABEL[p.team] || p.team,
        hdc: p.hdc,
      });
      // Hdcp aplicado por fórmula
      const row = r.number;
      ws.getCell(row, 5).value = { formula: `MIN(D${row},$B$${players.length + 5})` };
      ws.getCell(row, 5).numFmt = '0.0';
      ws.getCell(row, 4).numFmt = '0.0';

      // Team fill
      const teamCell = ws.getCell(row, 3);
      _applyTeamFill(teamCell, p.team);
    });

    // Suplente oficial gatto_ale
    const sup = _getSuplentesConocidos().find(s => s.id === 'gatto_ale');
    if (sup) {
      const r = ws.addRow({
        id: sup.id, name: sup.name, team: 'SUPL', hdc: sup.hdc || 0,
      });
      ws.getCell(r.number, 5).value = { formula: `MIN(D${r.number},$B$${players.length + 5})` };
      ws.getCell(r.number, 5).numFmt = '0.0';
      ws.getCell(r.number, 4).numFmt = '0.0';
      ws.getCell(r.number, 3).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.goldSoft } };
      ws.getCell(r.number, 3).alignment = { horizontal: 'center' };
    }

    // Constantes
    const cRow = players.length + 4;
    ws.getCell(cRow, 1).value = 'CONSTANTES';
    _applySectionTitle(ws.getCell(cRow, 1));
    ws.mergeCells(cRow, 1, cRow, 5);

    const consts = [
      ['Cap Hdcp', HDCP_CAP],
      ['F9 Mult',  _getF9Mult()],
      ['F10 Mult', _getF10Mult()],
    ];
    consts.forEach((kv, i) => {
      const r = cRow + 1 + i;
      ws.getCell(r, 1).value = kv[0];
      ws.getCell(r, 1).font = { bold: true };
      ws.getCell(r, 2).value = kv[1];
      ws.getCell(r, 2).numFmt = '0.0';
      _applyBottomBorder(ws.getCell(r, 1));
      _applyBottomBorder(ws.getCell(r, 2));
    });

    // Tabla pts medal
    const pRow = cRow + 5;
    ws.getCell(pRow, 1).value = 'PUNTOS MEDAL POR PUESTO';
    _applySectionTitle(ws.getCell(pRow, 1));
    ws.mergeCells(pRow, 1, pRow, 5);

    const medalHdr = ['Pos', 'Pts'];
    medalHdr.forEach((h, i) => {
      const c = ws.getCell(pRow + 1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    const pts = _getMedalPts();
    pts.forEach((p, i) => {
      const r = pRow + 2 + i;
      ws.getCell(r, 1).value = i + 1;
      ws.getCell(r, 2).value = p;
      _applyBottomBorder(ws.getCell(r, 1));
      _applyBottomBorder(ws.getCell(r, 2));
    });

    ws.views = [{ state: 'frozen', ySplit: 1, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja Fixture — calendario del año.
   */
  function _buildFixture(wb) {
    const ws = wb.addWorksheet('Fixture', { views: [{ showGridLines: false }] });
    ws.columns = [
      { header: 'F#',           key: 'num',   width: 6  },
      { header: 'Fecha',        key: 'fecha', width: 18 },
      { header: 'Cancha',       key: 'cancha',width: 22 },
      { header: 'Modalidad',    key: 'mod',   width: 22 },
      { header: 'Criterio',     key: 'crit',  width: 22 },
      { header: 'Organizadores',key: 'org',   width: 28 },
      { header: 'Estado',       key: 'est',   width: 14 },
    ];
    ws.getRow(1).eachCell(c => _applyHeaderStyle(c));
    ws.getRow(1).height = 24;

    const fechas = _getFechas();
    const fixture = _getFixture() || {};
    fechas.forEach(f => {
      const fxItem = fixture[f.num] || {};
      const row = ws.addRow({
        num: `F${f.num}`,
        fecha: f.fecha || '',
        cancha: f.cancha || fxItem.cancha || '',
        mod: f.modalidad || fxItem.modalidad || '',
        crit: fxItem.criterio || '',
        org: f.organizadores || fxItem.organizadores || '',
        est: f.pendiente ? 'PENDIENTE' : 'JUGADA',
      });
      const estCell = ws.getCell(row.number, 7);
      if (f.pendiente) {
        estCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.pendiente } };
      } else {
        estCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.eagle } };
        estCell.font = { color: { argb: COLOR.white }, bold: true };
      }
      estCell.alignment = { horizontal: 'center' };
    });

    ws.views = [{ state: 'frozen', ySplit: 1, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja por fecha (F1..F10).
   * Si pendiente, sólo muestra cartel "PENDIENTE".
   */
  function _buildFecha(wb, fechaObj) {
    const sheetName = `F${fechaObj.num}`;
    const ws = wb.addWorksheet(sheetName, { views: [{ showGridLines: false }] });

    // Headers de fecha
    ws.getCell('A1').value = `FECHA ${fechaObj.num}`;
    _applySectionTitle(ws.getCell('A1'));
    ws.mergeCells('A1:F1');
    ws.getRow(1).height = 26;

    ws.getCell('A2').value = 'Fecha:';
    ws.getCell('B2').value = fechaObj.fecha || '';
    ws.getCell('A3').value = 'Cancha:';
    ws.getCell('B3').value = fechaObj.cancha || '';
    ws.getCell('A4').value = 'Modalidad:';
    ws.getCell('B4').value = fechaObj.modalidad || '';
    ws.getCell('D2').value = 'Organizadores:';
    ws.getCell('E2').value = fechaObj.organizadores || '';
    ws.mergeCells('E2:K2');
    ws.getCell('D3').value = 'Par total:';
    const par = _parFor(fechaObj);
    ws.getCell('E3').value = par.reduce((a,b) => a + b, 0);
    ws.getCell('D4').value = 'Estado:';
    ws.getCell('E4').value = fechaObj.pendiente ? 'PENDIENTE' : 'JUGADA';

    [2,3,4].forEach(r => {
      ws.getCell(r, 1).font = { bold: true, color: { argb: COLOR.gold } };
      ws.getCell(r, 4).font = { bold: true, color: { argb: COLOR.gold } };
    });

    if (fechaObj.pendiente) {
      ws.mergeCells('A6:U10');
      const p = ws.getCell('A6');
      p.value = 'FECHA PENDIENTE — sin scorecard cargado';
      p.font = { bold: true, size: 18, color: { argb: COLOR.grayMid }, italic: true };
      p.alignment = { horizontal: 'center', vertical: 'middle' };
      p.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.pendiente } };
      return ws;
    }

    // Row 5: PAR por hoyo
    // Cols: A Equipo, B Nombre, C Hdcp, D HcapApl, E..V H1..H18, W F9, X B9, Y Gross, Z Neto, AA Pos, AB Pts
    const HOLE_START_COL = 5;
    const headerRow = 5;
    ws.getCell(headerRow, 1).value = 'Eq';
    ws.getCell(headerRow, 2).value = 'Jugador';
    ws.getCell(headerRow, 3).value = 'Hdcp';
    ws.getCell(headerRow, 4).value = 'HcapAp';
    for (let h = 0; h < 18; h++) {
      ws.getCell(headerRow, HOLE_START_COL + h).value = `H${h + 1}`;
    }
    const F9_COL = HOLE_START_COL + 18;       // 23
    const B9_COL = F9_COL + 1;                // 24
    const GROSS_COL = B9_COL + 1;             // 25
    const NETO_COL = GROSS_COL + 1;           // 26
    const POS_COL = NETO_COL + 1;             // 27
    const PTS_COL = POS_COL + 1;              // 28
    ws.getCell(headerRow, F9_COL).value = 'F9';
    ws.getCell(headerRow, B9_COL).value = 'B9';
    ws.getCell(headerRow, GROSS_COL).value = 'Gross';
    ws.getCell(headerRow, NETO_COL).value = 'Neto';
    ws.getCell(headerRow, POS_COL).value = 'Pos';
    ws.getCell(headerRow, PTS_COL).value = 'Pts';
    for (let c = 1; c <= PTS_COL; c++) {
      _applyHeaderStyle(ws.getCell(headerRow, c));
    }
    ws.getRow(headerRow).height = 24;

    // Row 6: PAR
    const parRow = 6;
    ws.getCell(parRow, 2).value = 'PAR';
    ws.getCell(parRow, 2).font = { bold: true, italic: true };
    par.forEach((p, i) => {
      const c = ws.getCell(parRow, HOLE_START_COL + i);
      c.value = p;
      c.font = { bold: true, italic: true };
      c.alignment = { horizontal: 'center' };
      c.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.grayLight } };
    });
    // Totales PAR (fórmula)
    const parRowNum = parRow;
    ws.getCell(parRow, F9_COL).value = { formula: `SUM(E${parRowNum}:M${parRowNum})` };
    ws.getCell(parRow, B9_COL).value = { formula: `SUM(N${parRowNum}:V${parRowNum})` };
    ws.getCell(parRow, GROSS_COL).value = { formula: `W${parRowNum}+X${parRowNum}` };
    [F9_COL, B9_COL, GROSS_COL].forEach(c => {
      ws.getCell(parRow, c).font = { bold: true, italic: true };
      ws.getCell(parRow, c).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.grayLight } };
    });

    // Scorecards
    const scorecards = (fechaObj.scorecard || []).filter(s =>
      _isOfficial(s.id) || s.id === 'gatto_ale'
    );
    const medalCalc = _calcMedalFecha(fechaObj);

    const firstDataRow = parRow + 1;
    scorecards.forEach((sc, idx) => {
      const p = _playerById(sc.id) || _getSuplentesConocidos().find(s => s.id === sc.id);
      const team = p ? p.team : (sc.team || '');
      const r = firstDataRow + idx;

      // Equipo
      const eqC = ws.getCell(r, 1);
      eqC.value = TEAM_LABEL[team] ? TEAM_LABEL[team].charAt(0) : '?';
      _applyTeamFill(eqC, team);

      // Nombre
      const nameC = ws.getCell(r, 2);
      nameC.value = _displayName(sc.id);
      nameC.font = { bold: sc.id !== 'gatto_ale' };
      if (sc.id === 'gatto_ale') {
        nameC.font = { italic: true, color: { argb: COLOR.grayMid } };
      }

      // Hdcp / HcapAp
      ws.getCell(r, 3).value = sc.hdcp != null ? sc.hdcp : '';
      ws.getCell(r, 3).numFmt = '0.0';
      ws.getCell(r, 4).value = { formula: `MIN(C${r},${HDCP_CAP})` };
      ws.getCell(r, 4).numFmt = '0.0';

      // Hoyos
      const hoyos = sc.hoyos || [];
      hoyos.forEach((h, i) => {
        const c = ws.getCell(r, HOLE_START_COL + i);
        c.value = h;
        c.alignment = { horizontal: 'center' };
        _applyHoleColor(c, h, par[i]);
      });

      // F9 / B9 / Gross / Neto por fórmula
      ws.getCell(r, F9_COL).value = { formula: `SUM(E${r}:M${r})` };
      ws.getCell(r, B9_COL).value = { formula: `SUM(N${r}:V${r})` };
      ws.getCell(r, GROSS_COL).value = { formula: `W${r}+X${r}` };
      ws.getCell(r, NETO_COL).value = { formula: `Y${r}-D${r}` };
      [F9_COL, B9_COL, GROSS_COL, NETO_COL].forEach(c => {
        ws.getCell(r, c).font = { bold: true };
        ws.getCell(r, c).alignment = { horizontal: 'center' };
      });

      // Pos / Pts: por simplicidad calculamos en JS (empates / vacante son
      // complejos de poner en fórmula limpia). // TODO: convertir a fórmula
      const calc = medalCalc[sc.id];
      if (calc) {
        ws.getCell(r, POS_COL).value = calc.pos;
        ws.getCell(r, PTS_COL).value = calc.pts;
        ws.getCell(r, PTS_COL).numFmt = '0.0';
      } else if (sc.id === 'gatto_ale') {
        ws.getCell(r, POS_COL).value = '—';
        ws.getCell(r, PTS_COL).value = 0;
      }
      [POS_COL, PTS_COL].forEach(c => {
        ws.getCell(r, c).alignment = { horizontal: 'center' };
      });

      // Separador
      _applyBottomBorder(ws.getCell(r, PTS_COL));
    });

    // Vacante flag
    const lastScRow = firstDataRow + scorecards.length;
    const oficSorted = [...(fechaObj.scorecard || [])].sort((a,b) => (a.neto||999) - (b.neto||999));
    const vac = oficSorted.length && !_isOfficial(oficSorted[0].id);
    ws.getCell(lastScRow + 1, 1).value = 'VACANTE:';
    ws.getCell(lastScRow + 1, 1).font = { bold: true, color: { argb: COLOR.gold } };
    const vCell = ws.getCell(lastScRow + 1, 2);
    vCell.value = vac ? 'SÍ — ganador no oficial, nadie suma FG' : 'NO';
    vCell.font = { bold: true };
    if (vac) vCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.bogey } };

    // Matchs
    const matchStart = lastScRow + 3;
    ws.getCell(matchStart, 1).value = 'MATCHS';
    _applySectionTitle(ws.getCell(matchStart, 1));
    ws.mergeCells(matchStart, 1, matchStart, 10);

    const matchHdr = ['Tipo', 'Gris', 'Rojo', 'Hoyos G', 'Hoyos R', 'Ganador', 'Dif'];
    matchHdr.forEach((h, i) => {
      const c = ws.getCell(matchStart + 1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    (fechaObj.matchs || []).forEach((m, i) => {
      const r = matchStart + 2 + i;
      ws.getCell(r, 1).value = (m.tipo || '').toUpperCase();
      ws.getCell(r, 2).value = (m.g || []).map(_displayName).join(' + ');
      ws.getCell(r, 3).value = (m.r || []).map(_displayName).join(' + ');
      ws.getCell(r, 4).value = m.hoyos_g != null ? m.hoyos_g : '';
      ws.getCell(r, 5).value = m.hoyos_r != null ? m.hoyos_r : '';
      const gan = ws.getCell(r, 6);
      gan.value = m.ganador === 'g' ? 'GRIS' : m.ganador === 'r' ? 'ROJO' : 'EMPATE';
      if (m.ganador === 'g') _applyTeamFill(gan, 'g');
      else if (m.ganador === 'r') _applyTeamFill(gan, 'r');
      else gan.alignment = { horizontal: 'center' };
      ws.getCell(r, 7).value = m.dif != null ? m.dif : '';
      ws.getCell(r, 7).alignment = { horizontal: 'center' };
    });

    // Comentario
    if (fechaObj.comentario) {
      const cRow = matchStart + 2 + (fechaObj.matchs || []).length + 1;
      ws.getCell(cRow, 1).value = 'COMENTARIO:';
      ws.getCell(cRow, 1).font = { bold: true, color: { argb: COLOR.gold } };
      ws.mergeCells(cRow, 2, cRow, 14);
      const cm = ws.getCell(cRow, 2);
      cm.value = fechaObj.comentario;
      cm.alignment = { wrapText: true, vertical: 'top' };
      cm.font = { italic: true, color: { argb: COLOR.grayMid } };
    }

    // Anchos
    ws.getColumn(1).width = 6;
    ws.getColumn(2).width = 26;
    ws.getColumn(3).width = 7;
    ws.getColumn(4).width = 7;
    for (let i = 0; i < 18; i++) ws.getColumn(HOLE_START_COL + i).width = 5;
    [F9_COL, B9_COL, GROSS_COL, NETO_COL, POS_COL].forEach(c => ws.getColumn(c).width = 7);
    ws.getColumn(PTS_COL).width = 8;

    ws.views = [{ state: 'frozen', xSplit: 2, ySplit: 6, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja Acumulado Medal — ranking total con fórmulas por fecha.
   * Cols: A=Pos | B=Jugador | C=Equipo | D..M=Pts F1..F10 | N=Total
   * (Las fórmulas usan los datos calculados en cada hoja F#.)
   */
  function _buildAcumulado(wb) {
    const ws = wb.addWorksheet('Acumulado Medal', { views: [{ showGridLines: false }] });

    const hdrs = ['Pos', 'Jugador', 'Equipo'];
    for (let i = 1; i <= 10; i++) hdrs.push(`F${i}`);
    hdrs.push('TOTAL');
    hdrs.forEach((h, i) => {
      const c = ws.getCell(1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    ws.getRow(1).height = 24;

    // Para mantener fórmulas vivas usamos VLOOKUP del nombre del jugador
    // sobre la columna B (Nombre) de cada hoja F#, devolviendo la col 28 (Pts).
    // F#: cols A..AB; nombre en B; pts en AB (col 28).
    const players = _getPlayers();
    const fechas = _getFechas();

    // Pre-cálculo de totales para sort estático
    const totals = players.map(p => {
      let t = 0;
      fechas.forEach(f => {
        if (f.pendiente) return;
        const calc = _calcMedalFecha(f);
        if (calc[p.id]) t += calc[p.id].pts;
      });
      return { id: p.id, name: p.name, team: p.team, total: t };
    }).sort((a, b) => b.total - a.total);

    totals.forEach((t, idx) => {
      const r = idx + 2;
      ws.getCell(r, 1).value = idx + 1;
      ws.getCell(r, 2).value = t.name;
      const teamCell = ws.getCell(r, 3);
      teamCell.value = TEAM_LABEL[t.team] || '';
      _applyTeamFill(teamCell, t.team);

      for (let f = 1; f <= 10; f++) {
        const col = 3 + f; // D..M
        // Fórmula: lookup por nombre en hoja F#, devolver col 28 (Pts).
        // Asumimos que en F# hay header en row 5 y datos desde row 7.
        const formula = `IFERROR(VLOOKUP("${t.name.replace(/"/g, '""')}",'F${f}'!B7:AB30,27,FALSE),0)`;
        const cell = ws.getCell(r, col);
        cell.value = { formula };
        cell.numFmt = '0.0';
        cell.alignment = { horizontal: 'center' };
      }
      // Total
      const totalCell = ws.getCell(r, 14);
      totalCell.value = { formula: `SUM(D${r}:M${r})` };
      totalCell.numFmt = '#,##0.0';
      totalCell.font = { bold: true };
      _applyBottomBorder(ws.getCell(r, 14));
    });

    // Anchos
    ws.getColumn(1).width = 5;
    ws.getColumn(2).width = 28;
    ws.getColumn(3).width = 10;
    for (let i = 4; i <= 13; i++) ws.getColumn(i).width = 9;
    ws.getColumn(14).width = 12;

    ws.views = [{ state: 'frozen', xSplit: 3, ySplit: 1, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja Match History — todos los enfrentamientos.
   * Cols: A Fecha | B F# | C Tipo | D Equipo G | E Equipo R | F Hoyos G | G Hoyos R | H Ganador | I Dif | J Pts G | K Pts R
   */
  function _buildMatchHistory(wb) {
    const ws = wb.addWorksheet('Match History', { views: [{ showGridLines: false }] });
    const hdrs = ['Fecha', 'F#', 'Tipo', 'Equipo G', 'Equipo R', 'Hoyos G', 'Hoyos R', 'Ganador', 'Dif', 'Pts G', 'Pts R'];
    hdrs.forEach((h, i) => {
      const c = ws.getCell(1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    ws.getRow(1).height = 24;

    const fechas = _getFechas();
    let row = 2;
    fechas.forEach(f => {
      if (f.pendiente) return;
      (f.matchs || []).forEach(m => {
        ws.getCell(row, 1).value = f.fecha || '';
        ws.getCell(row, 2).value = `F${f.num}`;
        ws.getCell(row, 3).value = (m.tipo || '').toUpperCase();
        ws.getCell(row, 4).value = (m.g || []).map(_displayName).join(' + ');
        ws.getCell(row, 5).value = (m.r || []).map(_displayName).join(' + ');
        ws.getCell(row, 6).value = m.hoyos_g != null ? m.hoyos_g : '';
        ws.getCell(row, 7).value = m.hoyos_r != null ? m.hoyos_r : '';
        const gan = ws.getCell(row, 8);
        gan.value = m.ganador === 'g' ? 'GRIS' : m.ganador === 'r' ? 'ROJO' : 'EMPATE';
        if (m.ganador === 'g') _applyTeamFill(gan, 'g');
        else if (m.ganador === 'r') _applyTeamFill(gan, 'r');
        else gan.alignment = { horizontal: 'center' };
        ws.getCell(row, 9).value = m.dif != null ? m.dif : '';
        ws.getCell(row, 9).alignment = { horizontal: 'center' };

        // Pts por equipo (regla 2026: 1 pt al ganador, 0.5 c/u empate)
        // Los suplentes ahora suman para el color que representan; misma regla
        // siempre, haya o no suplente en el match.
        let pg = 0, pr = 0;
        if (m.ganador === 'g') pg = 1;
        else if (m.ganador === 'r') pr = 1;
        else { pg = 0.5; pr = 0.5; }
        ws.getCell(row, 10).value = pg;
        ws.getCell(row, 11).value = pr;
        ws.getCell(row, 10).numFmt = '0.0';
        ws.getCell(row, 11).numFmt = '0.0';
        row++;
      });
    });

    // Totales
    const totRow = row + 1;
    ws.getCell(totRow, 1).value = 'TOTALES';
    _applySectionTitle(ws.getCell(totRow, 1));
    ws.mergeCells(totRow, 1, totRow, 9);
    ws.getCell(totRow, 10).value = { formula: `SUM(J2:J${row - 1})` };
    ws.getCell(totRow, 11).value = { formula: `SUM(K2:K${row - 1})` };
    [10, 11].forEach(c => {
      ws.getCell(totRow, c).numFmt = '0.0';
      ws.getCell(totRow, c).font = { bold: true, color: { argb: COLOR.gold } };
      ws.getCell(totRow, c).fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: COLOR.navy } };
      ws.getCell(totRow, c).alignment = { horizontal: 'center' };
    });

    ws.columns.forEach((col, i) => {
      const widths = [14, 6, 8, 24, 24, 8, 8, 10, 6, 8, 8];
      ws.getColumn(i + 1).width = widths[i] || 12;
    });

    ws.views = [{ state: 'frozen', ySplit: 1, showGridLines: false }];
    return ws;
  }

  /**
   * Hoja Estadísticas — por jugador, con fórmulas sobre las hojas F#.
   * Cols: A Nombre | B Equipo | C Fechas Jugadas | D Fechas Ganadas |
   *       E Avg Gross | F Avg Neto | G Eagles | H Birdies |
   *       I Mejor Gross | J Peor Gross | K Mejor Pos
   */
  function _buildEstadisticas(wb) {
    const ws = wb.addWorksheet('Estadísticas', { views: [{ showGridLines: false }] });
    const hdrs = ['Nombre', 'Equipo', 'Fechas Jugadas', 'Fechas Ganadas',
                  'Avg Gross', 'Avg Neto', 'Eagles', 'Birdies',
                  'Mejor Gross', 'Peor Gross', 'Mejor Pos'];
    hdrs.forEach((h, i) => {
      const c = ws.getCell(1, i + 1);
      c.value = h;
      _applyHeaderStyle(c);
    });
    ws.getRow(1).height = 24;

    const players = _getPlayers();
    const fechas = _getFechas().filter(f => !f.pendiente);

    players.forEach((p, idx) => {
      const r = idx + 2;
      ws.getCell(r, 1).value = p.name;
      const eq = ws.getCell(r, 2);
      eq.value = TEAM_LABEL[p.team] || '';
      _applyTeamFill(eq, p.team);

      // Calcular en JS (más simple y robusto que fórmulas dinámicas sobre N hojas).
      // TODO: convertir a fórmula con SUMPRODUCT sobre rangos de cada F#.
      let jugadas = 0, ganadas = 0;
      let sumG = 0, sumN = 0, nG = 0, nN = 0;
      let eagles = 0, birdies = 0;
      let mejorG = Infinity, peorG = -Infinity;
      let mejorPos = Infinity;

      fechas.forEach(f => {
        const sc = (f.scorecard || []).find(s => s.id === p.id);
        if (!sc) return;
        jugadas++;
        if (typeof sc.gross === 'number') {
          sumG += sc.gross; nG++;
          if (sc.gross < mejorG) mejorG = sc.gross;
          if (sc.gross > peorG) peorG = sc.gross;
        }
        if (typeof sc.neto === 'number') { sumN += sc.neto; nN++; }
        const par = _parFor(f);
        (sc.hoyos || []).forEach((h, i) => {
          if (typeof h !== 'number') return;
          const d = h - par[i];
          if (d <= -2) eagles++;
          else if (d === -1) birdies++;
        });
        const calc = _calcMedalFecha(f);
        if (calc[p.id]) {
          if (calc[p.id].pos < mejorPos) mejorPos = calc[p.id].pos;
          if (calc[p.id].pos === 1 && !calc[p.id].vacante) ganadas++;
        }
      });

      ws.getCell(r, 3).value = jugadas;
      ws.getCell(r, 4).value = ganadas;
      ws.getCell(r, 5).value = nG ? +(sumG / nG).toFixed(1) : '';
      ws.getCell(r, 6).value = nN ? +(sumN / nN).toFixed(1) : '';
      ws.getCell(r, 7).value = eagles;
      ws.getCell(r, 8).value = birdies;
      ws.getCell(r, 9).value = mejorG === Infinity ? '' : mejorG;
      ws.getCell(r, 10).value = peorG === -Infinity ? '' : peorG;
      ws.getCell(r, 11).value = mejorPos === Infinity ? '' : mejorPos;

      [3,4,7,8,9,10,11].forEach(c => {
        ws.getCell(r, c).alignment = { horizontal: 'center' };
      });
      [5,6].forEach(c => {
        ws.getCell(r, c).numFmt = '0.0';
        ws.getCell(r, c).alignment = { horizontal: 'center' };
      });
      _applyBottomBorder(ws.getCell(r, 11));
    });

    // Anchos
    const widths = [26, 10, 12, 14, 11, 11, 9, 10, 12, 12, 11];
    widths.forEach((w, i) => ws.getColumn(i + 1).width = w);

    ws.views = [{ state: 'frozen', xSplit: 1, ySplit: 1, showGridLines: false }];
    return ws;
  }

  // ==================================================================
  // MAIN
  // ==================================================================

  /**
   * Genera el workbook completo y dispara la descarga.
   * @returns {Promise<Blob>} blob del archivo XLSX
   */
  async function generateMasterExcel() {
    if (!global.ExcelJS) {
      throw new Error('ExcelJS no está cargado. Incluí la librería antes de llamar generateMasterExcel().');
    }
    const wb = new global.ExcelJS.Workbook();
    wb.creator = 'MGT Master Excel Generator';
    wb.created = new Date();
    wb.properties.date1904 = false;

    // Sheets en orden
    _buildDashboard(wb);
    _buildSetup(wb);
    _buildFixture(wb);

    const fechas = _getFechas();
    fechas.forEach(f => {
      try {
        _buildFecha(wb, f);
      } catch (err) {
        console.error(`[MGT XLSX] Error en F${f.num}:`, err);
        // Hoja mínima de error
        const ws = wb.addWorksheet(`F${f.num}`, { views: [{ showGridLines: false }] });
        ws.getCell('A1').value = `F${f.num} — ERROR: ${err.message}`;
      }
    });

    _buildAcumulado(wb);
    _buildMatchHistory(wb);
    _buildEstadisticas(wb);

    // Buffer + descarga
    const buf = await wb.xlsx.writeBuffer();
    const blob = new Blob([buf], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    });

    const today = new Date().toISOString().slice(0, 10);
    const filename = `MGT_Master_${today}.xlsx`;

    // Disparar descarga si estamos en browser
    if (typeof global.document !== 'undefined') {
      const url = URL.createObjectURL(blob);
      const a = global.document.createElement('a');
      a.href = url;
      a.download = filename;
      global.document.body.appendChild(a);
      a.click();
      setTimeout(() => {
        global.document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 0);
    }

    return blob;
  }

  // Exponer al global scope
  global.generateMasterExcel = generateMasterExcel;

})(typeof window !== 'undefined' ? window : globalThis);
