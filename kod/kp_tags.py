# Słownik wymagań / obowiązków (wersja robocza 1, do akceptacji)
import re

def R(*p): return re.compile('|'.join(p), re.I)

NORMS = {
    'ISO 19443': R(r'iso\s*19443'),
    'ISO 9001': R(r'iso\s*9001'),
    'ISO 14001': R(r'iso\s*14001'),
    'ISO 45001': R(r'iso\s*45001'),
    'ISO 17025': R(r'iso\s*(/iec\s*)?17025'),
    'ISO 27001': R(r'iso\s*(/iec\s*)?27001'),
    'ISO 3834': R(r'iso\s*3834'),
    'ISO 9606 / 15614': R(r'iso\s*9606|iso\s*15614'),
    'ISO 19650 (BIM)': R(r'iso\s*19650'),
    'ASME NQA-1': R(r'nqa[\s-]*1'),
    'ASME BPVC Sec. III': R(r'asme\s*(bpvc\s*)?(section|sec\.?)\s*iii\b'),
    'ASME (inne)': R(r'\basme\b(?!\s*(bpvc\s*)?(section|sec\.?)\s*iii\b)(?![\s-]*nqa)'),
    '10 CFR 50 App. B': R(r'10\s*cfr\s*50.{0,20}appendix\s*b|appendix\s*b\s*(to|of)\s*10\s*cfr'),
    '10 CFR 21': R(r'10\s*cfr\s*(part\s*)?21\b'),
    '10 CFR 810 (kontrola eksportu)': R(r'10\s*cfr\s*(part\s*)?810'),
    'RCC-M / RCC-E': R(r'rcc-?[me]\b'),
    'Eurokody': R(r'eurocode|eurokod'),
    'EN 1090': R(r'en\s*1090'),
    'IAEA (standardy)': R(r'\biaea\b|maea\b|gsr part'),
    'IEC / IEEE': R(r'\biec\s*\d|\bieee\b'),
    'Prawo atomowe': R(r'prawo(m)? atomow|atomic law|polish nuclear law|nuclear law'),
    'Prawo budowlane': R(r'praw\w* budowlan|construction law|building law'),
    'Prawo zamówień publicznych': R(r'zamówień publicznych|\bpzp\b|public procurement'),
    'FIDIC / NEC': R(r'\bfidic\b|\bnec\s*\d|\bnec\b contract'),
    'ITIL': R(r'\bitil\b'),
}
CERTS = {
    'Uprawnienia budowlane': R(r'uprawnienia budowlane|building permit(s)? licen'),
    'Uprawnienia SEP / energetyczne': R(r'\bsep\b|uprawnienia energetyczne|świadectwo kwalifikacyjne'),
    'UDT': R(r'\budt\b'),
    'Spawalnictwo IWE / IWI / IWT': R(r'\biw[eit]\b|international welding (engineer|inspector|technologist)|ewe\b'),
    'Spawacz (certyfikat)': R(r'certyfikowany spawacz|uprawnienia spawalnicze|welder qualification|certified welder'),
    'NDT poziom 2/3': R(r'\bndt\b|\bnde\b|badania nieniszczące|level\s*(ii|iii|2|3)\b'),
    'CSWIP / AWS CWI': R(r'cswip|\bcwi\b'),
    'Audytor wiodący': R(r'lead auditor|audytor wiodący|auditor certif'),
    'PMP / PMI': R(r'\bpmp\b|\bpmi\b|pmi-sp'),
    'PRINCE2 / IPMA': R(r'prince\s*2|\bipma\b'),
    'Primavera P6 (certyfikat)': R(r'primavera p6 certification'),
    'Lean / Six Sigma': R(r'six sigma|\blean\b|green belt|black belt'),
    'NEBOSH / IOSH': R(r'nebosh|iosh'),
    'ACCA / CIMA / biegły rewident': R(r'\bacca\b|\bcima\b|biegły rewident'),
    'Licencja inżynierska (PE / CEng)': R(r'\bp\.?e\.? licen|professional engineer|chartered engineer|\bceng\b'),
    'Prawo jazdy kat. B': R(r'prawo jazdy|driver\'?s licen'),
    'Certyfikaty Microsoft / Azure': R(r'azure administrator|identity & access administrator|windows server hybrid administrator|microsoft certified'),
}
SOFT = {
    'SAP': R(r'\bsap\b'), 'Primavera P6': R(r'primavera|\bp6\b'), 'MS Project': R(r'ms project|microsoft project'),
    'AutoCAD': R(r'autocad'), 'Revit': R(r'\brevit\b'), 'Navisworks': R(r'navisworks'), 'Autodesk ACC': R(r'\bacc\b|autodesk construction cloud'),
    'AVEVA E3D / PDMS': R(r'\be3d\b|pdms|aveva'), 'SmartPlant / Intergraph': R(r'smartplant|intergraph|smart 3d'),
    'Tekla': R(r'tekla'), 'MicroStation': R(r'microstation'), 'ANSYS / FEA': R(r'ansys|\bfea\b|finite element'),
    'MATLAB': R(r'matlab'), 'Power BI': R(r'power\s*bi'), 'Excel (zaawansowany)': R(r'advanced.{0,10}excel|excel.{0,15}(advanced|zaawansowan)|advance ms excel'),
    'Python': R(r'python'), 'C# / .NET': R(r'c#|\.net\b|c_net'), 'Java': R(r'\bjava\b'), 'SQL': R(r'\bsql\b'),
    'Azure / chmura': R(r'\bazure\b|\baws\b|cloud'), 'VMware': R(r'vmware'), 'Linux': R(r'\blinux\b'),
    'Aconex / EDMS': R(r'aconex|edms|documentum|sharepoint'), 'Teamcenter / PLM': R(r'teamcenter|\bplm\b'), 'Ecosys': R(r'ecosys'),
    'CRM': R(r'\bcrm\b'), 'LMS': R(r'\blms\b|cornerstone|moodle'),
}
LANG = {'angielski': R(r'english|angielsk'), 'polski': R(r'polish|polsk(i|iego) (język|na poziomie)|język(a)? polsk|native polish'),
        'niemiecki': R(r'german|niemieck'), 'francuski': R(r'french|francusk'), 'hiszpański': R(r'spanish|hiszpańsk'),
        'czeski': R(r'czech|czesk'), 'słowacki': R(r'slovak|słowack'), 'rosyjski': R(r'russian|rosyjsk')}
FLAGS = {
    'Doświadczenie w sektorze jądrowym': R(r'(experience|doświadczeni\w*).{0,80}(nuclear|jądrow)|nuclear (industry|power|plant|project)s? experience'),
    'Znajomość AP1000': R(r'ap1000'),
    'Kultura bezpieczeństwa': R(r'safety culture|kultur\w* bezpieczeństwa|nuclear safety culture|questioning attitude'),
    'Poświadczenie bezpieczeństwa (niejawne)': R(r'poświadczeni\w* bezpieczeństwa|informacji niejawnych|security clearance'),
    'Background check / test narkotykowy': R(r'background check|drug screen'),
    'Praca na budowie / w terenie': R(r'on site|on-site|project site|na terenie budowy|lubiatowo|construction site|field'),
    'Podróże służbowe': R(r'travel|podróż|delegacj|wyjazd'),
    'Relokacja': R(r'relocat|relokacj|przeprowadz'),
    'Zarządzanie ludźmi': R(r'direct reports|supervis\w* (staff|team|employees)|zarządzani\w* zespoł|kierowani\w* zespoł|lead(ing)? a team|people management'),
    'Środowisko międzynarodowe': R(r'international (environment|team|project)|międzynarodow'),
    'Projekty EPC / duże inwestycje': R(r'\bepc\b|large[- ]scale|major (capital )?project|duż\w* (projekt|inwestycj)'),
    'Nadzór nad dostawcami': R(r'supplier (oversight|surveillance|performance|audit|assessment|quality)|nadzór nad dostaw|vendor (oversight|surveillance)'),
    'Kontrola jakości / odbiory': R(r'inspection|quality control|\bqc\b|odbior|kontrol\w* jakości|itp\b|inspection and test plan'),
    'Niezgodności / działania korygujące': R(r'non-?conformanc|\bncr\b|corrective action|niezgodno|działa\w* korygując|\bcap\b'),
    'Audyty': R(r'audit|audyt'),
    'Licencjonowanie / dozór': R(r'licens|licencj|regulator|dozor|paa\b|państwow\w* agencj'),
    'Ochrona radiologiczna': R(r'radiation protection|ochron\w* radiologiczn|dozymetr|alara'),
    'Harmonogramowanie': R(r'schedul|harmonogram'),
    'Zarządzanie kosztami': R(r'cost (control|management|estimat)|koszt|budżet|budget'),
    'Zakupy / kontrakty': R(r'procure|purchas|zakup|kontrakt\w*|\bcontract(s|ing)?\b(?! scope)'),
    'Współpraca z podwykonawcami': R(r'subcontract|podwykonaw|contractor'),
    'Dokumentacja techniczna': R(r'technical documentation|dokumentacj\w* techniczn|engineering deliverables|specyfikacj'),
    'Szkolenie / instruktaż': R(r'training|szkoleni|instruct'),
    'BHP / EHS': R(r'\bbhp\b|\behs\b|\besh\b|health and safety|occupational safety'),
}
EDU = [('doktorat', R(r'ph\.?d|doktor')), ('magister', R(r"master'?s|magist|mgr\b|msc")),
       ('wyższe (licencjat/inżynier)', R(r"bachelor|wyższe|degree|inżynier|university|studia")),
       ('średnie / zawodowe', R(r'high school|średnie|zawodowe|vocational|technikum'))]
FIELD = {'budownictwo': R(r'civil|structural|budownic|konstrukc'), 'mechanika': R(r'mechanic|mechani'), 'elektryka': R(r'electric|elektr'),
         'energetyka / jądrowe': R(r'nuclear engineering|nuclear physics|energetyk|power engineering|inżynieri\w* jądrow'), 'chemia': R(r'chemi'), 'informatyka': R(r'computer science|informatyk|information technology|software engineering|telekomunik'),
         'architektura': R(r'architekt|architect'), 'ekonomia / finanse': R(r'finance|accounting|ekonom|finans|rachunk'), 'prawo': R(r'law degree|degree in law|prawnicz|kierun\w* prawo|\bllm\b|juris'),
         'zarządzanie': R(r'business administration|zarządzani|management degree'), 'fizyka': R(r'physic|fizyk')}

def langs(text):
    res = {}
    for k, rx in LANG.items():
        for m in rx.finditer(text):
            ctx = text[max(0, m.start() - 80): m.end() + 80]
            lvl = re.search(r'\b(A1|A2|B1|B2|C1|C2)\b', ctx)
            fl = re.search(r'fluent|native|biegł|bardzo dobr|very good|proficient|advanced', ctx, re.I)
            v = lvl.group(1) if lvl else ('biegły' if fl else 'tak')
            if k not in res or res[k] == 'tak': res[k] = v
    return res

def years(text):
    ys = []
    for m in re.finditer(r'(\d{1,2})\s*(?:\+|–|-\s*\d{1,2})?\s*(?:\+)?\s*(?:years?|yrs|lat\w*|letni\w*|roku)', text, re.I):
        n = int(m.group(1))
        if 0 < n <= 30: ys.append(n)
    for m in re.finditer(r'(?:minimum|min\.|at least|co najmniej|przynajmniej|łącznie)\s*(\d{1,2})', text, re.I):
        n = int(m.group(1))
        if 0 < n <= 30: ys.append(n)
    return ys

def hits(d, text):
    return sorted(k for k, rx in d.items() if rx.search(text))

def extract(sec, full):
    must = '\n'.join(sec.get('must', []))
    nice = '\n'.join(sec.get('nice', []))
    duties = '\n'.join(sec.get('duties', []) + sec.get('summary', []))
    reqtext = must + '\n' + nice
    body = reqtext + '\n' + duties
    yr = years(must) or years(reqtext)
    edu = next((n for n, rx in EDU if rx.search(reqtext)), None)
    out = dict(
        normy=hits(NORMS, body), normy_wymagane=hits(NORMS, must), normy_mile=hits(NORMS, nice),
        certyfikaty=hits(CERTS, body), oprogramowanie=hits(SOFT, body),
        jezyki=langs(reqtext if reqtext.strip() else body),
        lata_min=min(yr) if yr else None, lata_max=max(yr) if yr else None,
        wyksztalcenie=edu, kierunki=hits(FIELD, reqtext),
        cechy=hits(FLAGS, reqtext), obowiazki_tagi=hits(FLAGS, duties),
        warunki=hits(FLAGS, full) ,
        kontrola_eksportu=export_control(full, sec),
        n_obowiazkow=len(sec.get('duties', [])), n_wymagan=len(sec.get('must', [])), n_mile=len(sec.get('nice', [])),
    )
    return out

# --- Kontrola eksportu (pole wewnętrzne, nie publikujemy) -------------------
EXPORT_RULES = [
    ('10 CFR 810 (DOE)', re.compile(r'10\s*CFR\s*(Part\s*)?810|Part\s*810', re.I)),
    ('10 CFR 110 (NRC)', re.compile(r'10\s*CFR\s*(Part\s*)?110\b', re.I)),
    ('ITAR', re.compile(r'\bITAR\b')),
    ('EAR', re.compile(r'\bEAR\b|Export Administration Regulations')),
    ('Wzmianka o kontroli eksportu', re.compile(r'export[- ]control|export regulation|kontrol\w* eksport|deemed export', re.I)),
]

def export_control(full, sec):
    """Zwraca (status, lista reżimów, gdzie). status: 'TAK - warunek stanowiska' / 'TEMAT w obowiązkach/wymaganiach' / 'NIE'."""
    hits = [n for n, rx in EXPORT_RULES if rx.search(full)]
    if not hits: return 'NIE', [], ''
    cond = re.search(r'(position|role|job)\s+is\s+subject\s+to.{0,120}(CFR|export)', full, re.I | re.S) or re.search(r'10\s*CFR\s*(Part\s*)?810', full, re.I)
    work = '\n'.join(sec.get('duties', []) + sec.get('must', []) + sec.get('nice', []))
    inwork = [n for n, rx in EXPORT_RULES if rx.search(work)]
    if cond: return 'TAK - warunek stanowiska', hits, 'klauzula w opisie stanowiska'
    return 'TEMAT w obowiązkach/wymaganiach', hits, ', '.join(inwork) or 'tekst ogłoszenia'
