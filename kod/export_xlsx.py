# Eksport bazy do Excela: python3 export_xlsx.py kp.sqlite wynik.xlsx
import sys, json, sqlite3, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import kp_tags

db = sqlite3.connect(sys.argv[1]); out = sys.argv[2]
FIRM = {'bechtel': 'Bechtel', 'westinghouse': 'Westinghouse', 'pej': 'PEJ'}
F = Font(name='Calibri', size=10); FB = Font(name='Calibri', size=10, bold=True)
HDR = PatternFill('solid', fgColor='D9D9D9'); g = Side(style='thin', color='BFBFBF'); k = Side(style='thin', color='000000')
C = Alignment(horizontal='center', vertical='center', wrap_text=True); L = Alignment(horizontal='left', vertical='center', wrap_text=True)

def sheet(ws, head, rows, widths, left=()):
    ws.append(head)
    for r in rows: ws.append(r)
    nr, nc = ws.max_row, ws.max_column
    for row in ws.iter_rows(min_row=1, max_row=nr, max_col=nc):
        for c in row:
            c.font = FB if c.row == 1 else F
            c.alignment = L if (c.column in left and c.row > 1) else C
            c.border = Border(left=k if c.column == 1 else g, right=k if c.column == nc else g, top=k if c.row == 1 else g, bottom=k if c.row == nr else g)
            if c.row == 1: c.fill = HDR
    for i, w in enumerate(widths, 1): ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = 'A2'; ws.auto_filter.ref = ws.dimensions

wb = Workbook()
# 1. Oferty
q = '''SELECT j.firm, j.ext_id, j.title, j.func, j.level, j.city, j.status, j.first_seen, j.last_seen, j.closed_on, j.url,
       v.mode, v.sal_min, v.sal_max, v.sal_period, v.sal_min_month, v.sal_max_month, v.posted, v.tags, v.employer
       FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1)
       ORDER BY j.firm, j.func, j.title'''
rows = []
for (firm, eid, title, fn, lv, city, st, fs, ls, cl, url, mode, smin, smax, per, mmin, mmax, posted, tags, emp) in db.execute(q):
    t = json.loads(tags); e = json.loads(emp)
    rows.append([FIRM[firm], eid, title, fn, lv, city, mode or '', mmin, mmax,
                 (f"{smin:,} - {smax:,} PLN / {'rok' if per == 'rok' else 'mies.'}".replace(',', ' ') if smin else 'nie podano'),
                 'otwarta' if st == 'open' else 'zamknięta', fs, ls, cl or '', posted or '',
                 t['lata_min'], t['wyksztalcenie'] or '', ', '.join(t['kierunki']), ', '.join(f'{a} {b}' for a, b in t['jezyki'].items()),
                 ', '.join(t['normy_wymagane']), ', '.join(sorted(set(t['normy']) - set(t['normy_wymagane']))), ', '.join(t['certyfikaty']), ', '.join(t['oprogramowanie']),
                 ', '.join(t['cechy']), ', '.join(t['obowiazki_tagi']), t['n_obowiazkow'], t['n_wymagan'], t['n_mile'],
                 e.get('texpPostingGrade') or e.get('texpGrade') or '', e.get('texpDisciplineSpecialty') or '', e.get('texpExperienceLevel') or e.get('jobBoardPostingType') or '',
                 e.get('texpPlannedEndDate') or '', e.get('texpProjectNo') or '', e.get('ref') or '', e.get('valid_until') or '', (t.get('kontrola_eksportu') or ['?'])[0], ', '.join((t.get('kontrola_eksportu') or ['', []])[1]), url])
ws = wb.active; ws.title = 'Oferty'
sheet(ws, ['Firma', 'ID', 'Stanowisko', 'Funkcja', 'Poziom', 'Miasto', 'Tryb pracy', 'Wynagr. min (PLN/mies.)', 'Wynagr. max (PLN/mies.)', 'Wynagrodzenie wg ogłoszenia',
           'Status', 'Pierwszy raz widziana', 'Ostatnio widziana', 'Zamknięta', 'Data publikacji', 'Min. lat doświadczenia', 'Wykształcenie', 'Kierunki', 'Języki',
           'Normy wymagane', 'Normy w obowiązkach / mile widziane', 'Certyfikaty i uprawnienia', 'Oprogramowanie', 'Wymagania (kategorie)', 'Obowiązki (kategorie)',
           'Liczba obowiązków', 'Liczba wymagań', 'Liczba „mile widziane”', 'Bechtel: grade', 'Bechtel: specjalność', 'Poziom doświadczenia (pracodawca)',
           'Bechtel: planowany koniec', 'Bechtel: projekt', 'PEJ: nr ref.', 'PEJ: ważne do', 'Kontrola eksportu (wewn.)', 'Reżim / wzmianka', 'Link'],
      rows, [13, 11, 42, 26, 18, 16, 13, 12, 12, 26, 11, 12, 12, 11, 13, 11, 18, 22, 22, 24, 24, 28, 28, 40, 40, 10, 10, 10, 9, 18, 20, 13, 22, 14, 12, 26, 26, 40], left=(3, 18, 19, 20, 21, 22, 23, 24, 25, 38))
for r in range(2, ws.max_row + 1):
    for col in (8, 9): ws.cell(r, col).number_format = '#,##0'
    c = ws.cell(r, 38); c.hyperlink = c.value; c.font = Font(name='Calibri', size=10, color='0563C1', underline='single')
n = ws.max_row
ws2 = wb.create_sheet('Treść ogłoszeń')
SECN = {'duties': 'Obowiązki', 'must': 'Wymagania', 'nice': 'Mile widziane', 'summary': 'Opis stanowiska'}
rr = []
for firm, eid, title, secs in db.execute('''SELECT j.firm, j.ext_id, j.title, v.sections FROM jobs j JOIN versions v ON v.id=(SELECT id FROM versions WHERE job_key=j.job_key ORDER BY seen DESC, id DESC LIMIT 1) ORDER BY j.firm, j.title'''):
    s = json.loads(secs)
    for key in ('summary', 'duties', 'must', 'nice'):
        for i, line in enumerate(s.get(key, []), 1): rr.append([FIRM[firm], eid, title, SECN[key], i, line])
sheet(ws2, ['Firma', 'ID', 'Stanowisko', 'Sekcja', 'Lp.', 'Treść'], rr, [13, 11, 40, 16, 6, 110], left=(3, 6))
ws3 = wb.create_sheet('Historia zmian')
ev = [[FIRM[f], e, t, d, ty, det] for f, e, t, d, ty, det in db.execute('SELECT j.firm, j.ext_id, j.title, ev.day, ev.type, ev.detail FROM events ev JOIN jobs j USING(job_key) ORDER BY ev.day, j.firm')]
sheet(ws3, ['Firma', 'ID', 'Stanowisko', 'Data', 'Zdarzenie', 'Szczegóły'], ev, [13, 11, 42, 12, 14, 60], left=(3, 6))
wsL = wb.create_sheet('Archiwum list PEJ')
try:
    ls = [list(r) for r in db.execute("SELECT day, title, city, ref, valid_until FROM list_snapshots ORDER BY day, valid_until")]
except Exception:
    ls = []
sheet(wsL, ['Data migawki (Wayback)', 'Stanowisko', 'Lokalizacja', 'Nr ref.', 'Ważne do'], ls, [16, 70, 22, 22, 14], left=(2,))
# 4. Statystyka (formuły)
ws4 = wb.create_sheet('Statystyka')
R = f'Oferty!$A$2:$A${n}'
def col(letter): return f'Oferty!${letter}$2:${letter}${n}'
blocks = []
blocks.append(('Oferty wg firmy', ['Firma', 'Otwarte', 'Z podanym wynagrodzeniem', 'Śr. min (PLN/mies.)', 'Śr. max (PLN/mies.)'],
               [[f, f'=COUNTIFS({R},"{f}",{col("K")},"otwarta")', f'=COUNTIFS({R},"{f}",{col("H")},">0")',
                 f'=IFERROR(ROUND(AVERAGEIFS({col("H")},{R},"{f}",{col("H")},">0"),0),"-")', f'=IFERROR(ROUND(AVERAGEIFS({col("I")},{R},"{f}",{col("I")},">0"),0),"-")'] for f in FIRM.values()]))
funcs = [r[0] for r in db.execute('SELECT DISTINCT func FROM jobs ORDER BY 1')]
blocks.append(('Oferty wg funkcji', ['Funkcja'] + list(FIRM.values()) + ['Razem', 'Śr. min (PLN/mies.)', 'Śr. max (PLN/mies.)'],
               [[fn] + [f'=COUNTIFS({col("D")},"{fn}",{R},"{f}")' for f in FIRM.values()] + [f'=COUNTIFS({col("D")},"{fn}")',
                f'=IFERROR(ROUND(AVERAGEIFS({col("H")},{col("D")},"{fn}",{col("H")},">0"),0),"-")', f'=IFERROR(ROUND(AVERAGEIFS({col("I")},{col("D")},"{fn}",{col("I")},">0"),0),"-")'] for fn in funcs]))
def tagblock(title, names, letters):
    rows = []
    for nm in names:
        rows.append([nm] + [('=' + '+'.join(f'COUNTIFS({col(l)},"*{nm}*",{R},"{f}")' for l in letters)) for f in FIRM.values()] + [f'=SUM(B{{r}}:D{{r}})'])
    return (title, ['Pozycja'] + list(FIRM.values()) + ['Razem'], rows)
blocks.append(tagblock('Normy i przepisy (wymagane + w obowiązkach)', list(kp_tags.NORMS), ['T', 'U']))
blocks.append(tagblock('Certyfikaty i uprawnienia', list(kp_tags.CERTS), ['V']))
blocks.append(tagblock('Wymagania (kategorie)', list(kp_tags.FLAGS), ['X']))
blocks.append(tagblock('Obowiązki (kategorie)', list(kp_tags.FLAGS), ['Y']))
blocks.append(tagblock('Oprogramowanie', list(kp_tags.SOFT), ['W']))
row = 1
ws4.cell(row, 1, 'Statystyka liczona formułami z arkusza „Oferty”: wszystkie oferty w bazie (otwarte i zamknięte, w tym z archiwum Wayback), poza kolumną „Otwarte”. Wynagrodzenia Bechtel podane rocznie, przeliczone na miesiąc (/12). Westinghouse i PEJ: brutto miesięcznie. Średnie liczone tylko z ofert, w których podano wynagrodzenie.').font = Font(name='Calibri', size=10, italic=True)
row = 3
for title, head, rows_ in blocks:
    ws4.cell(row, 1, title).font = Font(name='Calibri', size=11, bold=True); row += 1
    top = row
    for j, h in enumerate(head, 1):
        c = ws4.cell(row, j, h); c.font = FB; c.fill = HDR; c.alignment = C
    for rws in rows_:
        row += 1
        for j, v in enumerate(rws, 1):
            if isinstance(v, str): v = v.replace('{r}', str(row))
            c = ws4.cell(row, j, v); c.font = F; c.alignment = L if j == 1 else C
            if j > 1: c.number_format = '#,##0'
    nc = len(head)
    for r in range(top, row + 1):
        for j in range(1, nc + 1):
            ws4.cell(r, j).border = Border(left=k if j == 1 else g, right=k if j == nc else g, top=k if r == top else g, bottom=k if r == row else g)
    row += 3
for i, w in enumerate([44, 14, 14, 14, 14, 16, 16, 16], 1): ws4.column_dimensions[get_column_letter(i)].width = w
# 5. Słownik
ws5 = wb.create_sheet('Słownik (do akceptacji)')
sl = []
for grp, d in (('Normy i przepisy', kp_tags.NORMS), ('Certyfikaty i uprawnienia', kp_tags.CERTS), ('Oprogramowanie', kp_tags.SOFT), ('Języki', kp_tags.LANG),
               ('Kategorie wymagań i obowiązków', kp_tags.FLAGS), ('Kierunki studiów', kp_tags.FIELD)):
    for nm, rx in d.items(): sl.append([grp, nm, rx.pattern])
sheet(ws5, ['Grupa', 'Pozycja', 'Wzorzec wyszukiwania (EN i PL)'], sl, [28, 40, 90], left=(2, 3))
wb.save(out)
print(n - 1, len(rr), len(ev))
