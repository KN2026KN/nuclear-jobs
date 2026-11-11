# Słownik projektów, krajów i języków ofert (11.2026, decyzje właściciela z 10.11.2026).
# - projekt(): etykieta projektu / obiektu z tytułu, lokalizacji i treści oferty + typ obiektu
# - kraj(): kod ISO kraju z lokalizacji (miasto / nazwa kraju)
# - tylko_analiza(): Rosatom i spółki, Rosja, Białoruś, Węgry (w całości, także Paks II) -> w bazie TAK, na stronie NIE
# - jezyk(): język ogłoszenia (langdetect, gdy jest; inaczej prosta heurystyka)
import re

TYP = {'bud': 'w budowie', 'eks': 'w eksploatacji', 'smr': 'SMR', 'bad': 'reaktor badawczy', 'fuz': 'fuzja',
       'odp': 'odpady i wycofywanie', 'ins': 'instytucja'}
TYP_EN = {'bud': 'under construction', 'eks': 'in operation', 'smr': 'SMR', 'bad': 'research reactor', 'fuz': 'fusion',
          'odp': 'waste and decommissioning', 'ins': 'institution'}

# (etykieta, kraj, typ, wzorzec). Kolejność ma znaczenie: pierwsze trafienie wygrywa (konkretne przed ogólnymi).
PROJEKTY = [
    ('AP1000 Lubiatowo-Kopalino', 'PL', 'bud', r'Lubiatow|Kopalin|Choczew|Pomeranian? (NPP|nuclear)|Polish (AP1000|nuclear power plant|NPP)|pierwsz\w* elektrown\w* jądrow|Polskie Elektrownie Jądrowe|\bPEJ\b'),
    ('BWRX-300 Włocławek', 'PL', 'smr', r'Włocławek|Wloclawek|Orlen Synthos|\bOSGE\b|BWRX[- ]?300.{0,40}(Polsk|Poland)'),
    ('MARIA Świerk', 'PL', 'bad', r'Świerk|Swierk|reaktor\w* MARIA|MARIA reactor|Narodowe Centrum Badań Jądrowych|\bNCBJ\b'),
    ('KSOP Różan', 'PL', 'odp', r'Różan|Rozan|\bKSOP\b|Unieszkodliwiania Odpadów Promieniotwórczych|\bZUOP\b'),
    ('Dukovany II', 'CZ', 'bud', r'Dukovany\s*(II|2)|EDU\s*II|Elektrárna Dukovany II|KHNP'),
    ('Dukovany', 'CZ', 'eks', r'Dukovan'),
    ('Temelín', 'CZ', 'eks', r'Temel[ií]n'),
    ('Mochovce', 'SK', 'bud', r'Mochovc'),
    ('Bohunice', 'SK', 'eks', r'Bohunic|Jaslovsk|JAVYS'),
    ('Kozloduy 7-8', 'BG', 'bud', r'Kozlod\w* (7|unit 7|NPP[- ]Newbuild)|Newbuild|Козлодуй.{0,20}(7|нови)|AP1000.{0,40}(Bulgaria|Kozlod)'),
    ('Kozloduy', 'BG', 'eks', r'Kozlod|Козлодуй'),
    ('Cernavodă 3-4', 'RO', 'bud', r'Cernavod\w*\s*(3|U3|unit\w* 3)|EnergoNuclear'),
    ('Cernavodă', 'RO', 'eks', r'Cernavod'),
    ('Doicești SMR', 'RO', 'smr', r'Doice[sș]ti|RoPower'),
    ('JEK2 / Krško', 'SI', 'eks', r'Kr[sš]k|JEK\s*2|GEN energija'),
    ('Hinkley Point C', 'GB', 'bud', r'Hinkley|\bHPC\b|Bridgwater|NNB Generation'),
    ('Sizewell C', 'GB', 'bud', r'Sizewell|Leiston'),
    ('Sellafield', 'GB', 'odp', r'Sellafield|Seascale|Whitehaven'),
    ('Wylfa / Rolls-Royce SMR', 'GB', 'smr', r'Wylfa|Rolls[- ]Royce SMR|Great British (Nuclear|Energy - Nuclear)'),
    ('Flamanville 3', 'FR', 'bud', r'Flamanville'),
    ('EPR2 Penly / Gravelines', 'FR', 'bud', r'\bEPR\s*2\b|Penly|Gravelines'),
    ('La Hague', 'FR', 'odp', r'La Hague|Beaumont-Hague'),
    ('Fermi Energia BWRX-300', 'EE', 'smr', r'Fermi Energia'),
    ('Ignalina (likwidacja)', 'LT', 'odp', r'Ignalin|Visaginas|\bINPP\b'),
    ('Khmelnytskyi 3-4', 'UA', 'bud', r'Khmelnyts\w*|Хмельницьк'),
    ('Leibstadt', 'CH', 'eks', r'Leibstadt|\bKKL\b'),
    ('Gösgen', 'CH', 'eks', r'G[öo]sgen|\bKKG\b'),
    ('Beznau', 'CH', 'eks', r'Beznau'),
    ('Doel / Tihange', 'BE', 'eks', r'\bDoel\b|Tihange'),
    ('MYRRHA', 'BE', 'bad', r'MYRRHA'),
    ('PALLAS Petten', 'NL', 'bad', r'\bPALLAS\b|Petten'),
    ('Almaraz', 'ES', 'eks', r'Almaraz'),
    ('Ascó / Vandellós', 'ES', 'eks', r'\bAsc[oó]\b|Vandell[oó]s|\bANAV\b'),
    ('Cofrentes', 'ES', 'eks', r'Cofrentes'),
    ('Trillo', 'ES', 'eks', r'\bTrillo\b'),
    ('Konrad / Asse / Morsleben', 'DE', 'odp', r'Schacht Konrad|Asse II|Morsleben'),
    ('Dounreay', 'GB', 'odp', r'Dounreay'),
    ('Heysham / Torness / Hartlepool', 'GB', 'eks', r'Heysham|Torness|Hartlepool'),
    ('STEP West Burton', 'GB', 'fuz', r'\bSTEP\b.{0,30}[Ff]usion|West Burton|UK Industrial Fusion Solutions|\bUKIFS\b'),
    ('Culham (UKAEA)', 'GB', 'fuz', r'Culham'),
    ('Jules Horowitz', 'FR', 'bad', r'Jules Horowitz|\bRJH\b'),
    ('ITER', 'FR', 'fuz', r'\bITER\b|Cadarache|Saint-Paul-l[eè]s-Durance'),
    ('Fusion for Energy (F4E)', 'ES', 'fuz', r'Fusion for Energy|\bF4E\b'),
    ('Olkiluoto', 'FI', 'eks', r'Olkiluoto|Eurajoki|\bTVO\b|Onkalo|Posiva'),
    ('Loviisa', 'FI', 'eks', r'Loviis|Lovisa'),
    ('Forsmark', 'SE', 'eks', r'Forsmark|Östhammar'),
    ('Ringhals', 'SE', 'eks', r'Ringhals|Varberg'),
    ('Oskarshamn', 'SE', 'eks', r'Oskarshamn|\bOKG\b'),
    ('Borssele', 'NL', 'eks', r'Borssele|\bEPZ\b'),
    ('Barakah', 'AE', 'eks', r'Barakah|Al Dhafra|\bENEC\b|Emirates Nuclear|Nawah'),
    ('Vogtle', 'US', 'eks', r'Vogtle|Waynesboro'),
    ('Darlington SMR', 'CA', 'smr', r'Darlington.{0,40}(SMR|BWRX|New Nuclear)|BWRX[- ]?300.{0,40}(Canada|Ontario|Darlington)'),
    ('Natrium Kemmerer', 'US', 'smr', r'Natrium|Kemmerer'),
    ('Palisades (restart)', 'US', 'eks', r'Palisades'),
    ('Crane / TMI (restart)', 'US', 'eks', r'Crane Clean Energy|Three Mile Island|\bTMI\b'),
    ('Hermes (Kairos Power)', 'US', 'smr', r'Kairos Power|\bHermes\b.{0,30}(reactor|Oak Ridge)'),
    ('Aurora (Oklo)', 'US', 'smr', r'\bOklo\b|Aurora[- ]INL'),
    ('Xe-100 Long Mott', 'US', 'smr', r'Xe-100|Long Mott|Seadrift|X-energy'),
    ('Clinch River BWRX-300', 'US', 'smr', r'Clinch River'),
    ('Bruce Power', 'CA', 'eks', r'Bruce Power|Bruce C\b'),
    ('Pickering', 'CA', 'eks', r'Pickering'),
    ('Wesleyville', 'CA', 'bud', r'Wesleyville'),
    ('Chalk River (CNL)', 'CA', 'bad', r'Chalk River|Canadian Nuclear Laboratories'),
    ('Saeul 3-4 / Shin Hanul 3-4', 'KR', 'bud', r'Saeul|Shin Hanul'),
    ('Chiny: Hualong One / CAP1000', 'CN', 'bud', r'Hualong|CAP1000|San.?ao|Xudabao|Lufeng|Haiyang'),
    ('Chashma 5', 'PK', 'bud', r'Chashma'),
    ('Rajasthan 7-8 / PFBR', 'IN', 'bud', r'Rawatbhata|Rajasthan Atomic|\bPFBR\b|Kalpakkam'),
    ('Ohma / Shimane 3', 'JP', 'bud', r'\bOhma\b|Shimane'),
    ('Angra 3', 'BR', 'bud', r'Angra'),
    ('Atucha / CAREM', 'AR', 'eks', r'Atucha|CAREM'),
    ('IAEA', 'AT', 'ins', r'\bIAEA\b|International Atomic Energy Agency'),
    # Rosatom: w bazie (analiza wynagrodzeń), nigdy na stronie
    ('Akkuyu', 'TR', 'bud', r'Akkuyu|Аккую'),
    ('El Dabaa', 'EG', 'bud', r'Dabaa|Эль[- ]Дабаа'),
    ('Rooppur', 'BD', 'bud', r'Rooppur|Руппур'),
    ('Bushehr', 'IR', 'eks', r'Bushehr|Бушер'),
    ('Kudankulam 3-6', 'IN', 'bud', r'Kudankulam|Куданкулам'),
    ('Paks II', 'HU', 'bud', r'Paks'),
    ('Uzbekistan SMR', 'UZ', 'smr', r'Jizzakh|Джизак'),
    ('Kazachstan Bałchasz', 'KZ', 'bud', r'Balkhash|Балхаш|Ulken|Улькен'),
    ('Leningrad II / Kursk II', 'RU', 'bud', r'Kursk II|Leningrad II|Курская АЭС|Ленинградская АЭС'),
]
_PRJ = [(e, k, t, re.compile(w, re.I)) for e, k, t, w in PROJEKTY]
PROJEKT_KRAJ = {e: k for e, k, t, w in PROJEKTY}
PROJEKT_TYP = {e: t for e, k, t, w in PROJEKTY}

ROSATOM = re.compile(r'Rosatom|Росатом|Akkuyu|Аккую|Atomstroyexport|Атомстройэкспорт|ASE JSC|Rusatom|Русатом|Greenatom|Гринатом|NIAEP|НИАЭП|Atomtechenergo|Атомтехэнерго|'
                     r'TVEL|ТВЭЛ|Rosenergoatom|Росэнергоатом|El Dabaa|Dabaa|Rooppur|Руппур|Bushehr|Бушер|Kudankulam|Куданкулам|Paks', re.I)
WYKLUCZONE_KRAJE = {'RU', 'BY', 'HU'}
ANALIZA_PROJEKTY = {'Akkuyu', 'El Dabaa', 'Rooppur', 'Bushehr', 'Kudankulam 3-6', 'Paks II', 'Uzbekistan SMR', 'Kazachstan Bałchasz', 'Leningrad II / Kursk II'}

# Kraje: nazwy (EN / lokalne / PL) i większe miasta jądrowe -> ISO
KRAJE = {
    'PL': r'Poland|Polska|Polen|Pologne|Warszaw|Warsaw|Krak[oó]w|Cracow|Gda[nń]sk|Gdynia|Wejherow|Lubiatow|Choczew|Otwock|Świerk|Różan|Włocławek|Wroc[lł]aw|Pozna[nń]|[ŁL][oó]d[zź]|Katowic|Szczecin|Lublin|Bydgoszcz|Toru[nń]',
    'CZ': r'Czech|Česk|Cesk|Praha|Prague|Brno|Plze[nň]|Dukovan|Temel[ií]n|T[řr]eb[ií][čc]|Řež',
    'SK': r'Slovak|Slovensk|Bratislav|Trnava|Mochovc|Levice|Bohunic',
    'BG': r'Bulgari|България|Sofia|София|Kozlod|Козлодуй',
    'RO': r'Romania|România|Bucure[sș]ti|Bucharest|Cernavod|Pite[sș]ti|Constan[tț]a',
    'SI': r'Sloveni|Ljubljana|Kr[sš]ko', 'HR': r'Croatia|Hrvatska|Zagreb',
    'FR': r'France|Paris|Lyon|Marseille|Cherbourg|Flamanville|Cadarache|Saint-Paul-l[eè]s-Durance|Orsay|Courbevoie|Saclay|Grenoble|Penly|Gravelines|Le Creusot|Chalon|Pierrelatte|Tricastin|Marcoule|Bagnols|La Hague|Lyon|Villeurbanne|Montrouge|Ch[aâ]tillon|Saint-Denis|Valence|Bordeaux|Tours|Chinon|Dunkerque|Rouen|Nantes|Lille|Dijon|Toulouse|Marseille|Aix',
    'GB': r'United Kingdom|\bUK\b|England|Scotland|Wales|London|Manchester|Warrington|Bristol|Gloucester|Derby|Sellafield|Whitehaven|Bridgwater|Hinkley|Sizewell|Leiston|Ipswich|Barnwood|Cumbria|Risley|Glasgow|Edinburgh|Hartlepool|Heysham|Torness|Anglesey|Wylfa|Harwell|Culham|Abingdon|Birmingham|Leeds|Sheffield|Cardiff|Plymouth|Barrow',
    'FI': r'Finland|Suomi|Helsin|Espoo|Eurajoki|Olkiluoto|Loviis|Rauma|Tampere|Turku',
    'SE': r'Sweden|Sverige|Stockholm|Solna|Forsmark|Ringhals|Varberg|Oskarshamn|Västerås|Göteborg|Gothenburg|Malmö|Östhammar|Uppsala|Luleå',
    'NL': r'Netherlands|Nederland|Amsterdam|Rotterdam|Petten|Borssele|Arnhem|Den Haag|The Hague|Almelo|Utrecht',
    'BE': r'Belgi|Bruxelles|Brussels|Brussel|Mol\b|Doel|Tihange|Antwerp|Liège',
    'ES': r'Spain|España|Madrid|Barcelona|Almaraz|Asc[oó]|Vandell[oó]s|Trillo|Cofrentes|Valencia|Sevilla|Salamanca',
    'CH': r'Switzerland|Schweiz|Suisse|Z[uü]rich|Baden|Gösgen|Leibstadt|Beznau|Gen[eè]v|Bern|Lausanne|Villigen',
    'DE': r'Germany|Deutschland|Berlin|M[uü]nchen|Munich|Erlangen|Karlsruhe|Essen|Hannover|Hamburg|Frankfurt|Gronau|Jülich|Garching|Stuttgart|Offenbach|Mannheim|Lingen',
    'IT': r'Italy|Italia|Roma|Rome|Milano|Milan|Genova|Ispra|Torino|Turin',
    'LT': r'Lithuania|Lietuv|Vilni|Visaginas|Ignalina', 'EE': r'Estonia|Eesti|Tallinn', 'LV': r'Latvia|Latvij|Riga',
    'AT': r'Austria|Österreich|Wien|Vienna|Seibersdorf', 'UA': r'Ukrain|Україн|Kyiv|Kiev|Київ|Khmelnytsk|Хмельницьк', 'DK': r'Denmark|Danmark|Copenhagen|København', 'NO': r'Norway|Norge|Oslo|Halden',
    'AE': r'United Arab Emirates|\bUAE\b|Abu Dhabi|Dubai|Barakah|Al Dhafra|Ruwais',
    'US': r'United States|\bUSA\b|\bU\.S\.|Pennsylvania|\bPA\b|Cranberry|Pittsburgh|Georgia|Waynesboro|Texas|Houston|Reston|Virginia|Tennessee|Knoxville|Oak Ridge|Richland|Washington|South Carolina|Columbia, SC|Aiken|Idaho|New Mexico|Los Alamos|Carlsbad|Ohio|Florida|California|Colorado|Denver|Wyoming|Kemmerer|Maryland|Frederick|Arizona|Phoenix|Michigan|Illinois|Chicago|North Carolina|Charlotte|Connecticut|Windsor|New York|Massachusetts|Missouri|Fulton|Kansas|Lynchburg|Newington|Madison|Alabama|Huntsville',
    'CA': r'Canada|Ontario|Toronto|Mississauga|Pickering|Darlington|Bowmanville|Kincardine|Peterborough|Chalk River|New Brunswick|Saskatchewan|Montr[eé]al|Qu[eé]bec|Calgary|Vancouver|Oakville|Ajax',
    'IN': r'\bIndia\b|Mumbai|Bangalore|Bengaluru|Chennai|Pune|Hyderabad|Delhi|Kudankulam', 'KR': r'Korea|Seoul|Daejeon|Gyeongju', 'JP': r'Japan|Tokyo',
    'CN': r'China|Shanghai|Beijing', 'ZA': r'South Africa|Johannesburg|Pretoria|Koeberg|Cape Town', 'BR': r'Brazil|Brasil|Rio de Janeiro|Angra', 'AR': r'Argentin|Buenos Aires|Atucha',
    'TR': r'Turkey|Türkiye|Turkiye|Mersin|Akkuyu|Аккую|Ankara|Istanbul', 'EG': r'Egypt|Cairo|Dabaa', 'BD': r'Bangladesh|Dhaka|Rooppur|Pabna', 'IR': r'\bIran\b|Bushehr',
    'HU': r'Hungary|Magyarorsz|Budapest|Paks', 'RU': r'Russia|Россия|Москва|Moscow|Санкт|Нижний|Росатом', 'BY': r'Belarus|Беларусь|Минск|Островец',
    'SA': r'Saudi', 'QA': r'Qatar|Doha', 'AU': r'Australia|Sydney|Adelaide', 'MX': r'Mexico|México', 'SG': r'Singapore', 'VN': r'Vietnam|Viet Nam|Hanoi|Ho Chi Minh', 'PH': r'Philippines|Manila', 'PK': r'Pakistan|Islamabad|Karachi|Chashma', 'UZ': r'Uzbekistan|Tashkent|Ташкент', 'KZ': r'Kazakhstan|Astana|Almaty|Казахстан', 'NZ': r'New Zealand|Auckland',
}
_KR = [(k, re.compile(w, re.I)) for k, w in KRAJE.items()]
ISO_KOD = {'Poland': 'PL', 'Czech Republic': 'CZ', 'Czechia': 'CZ', 'Slovakia': 'SK', 'Bulgaria': 'BG', 'Romania': 'RO', 'Slovenia': 'SI', 'France': 'FR',
           'United Kingdom': 'GB', 'Finland': 'FI', 'Sweden': 'SE', 'Netherlands': 'NL', 'Belgium': 'BE', 'Spain': 'ES', 'Switzerland': 'CH', 'Germany': 'DE',
           'Italy': 'IT', 'Lithuania': 'LT', 'Estonia': 'EE', 'Austria': 'AT', 'Ukraine': 'UA', 'United Arab Emirates': 'AE', 'United States': 'US', 'Canada': 'CA',
           'India': 'IN', 'South Korea': 'KR', 'Japan': 'JP', 'China': 'CN', 'South Africa': 'ZA', 'Brazil': 'BR', 'Argentina': 'AR', 'Turkey': 'TR', 'Egypt': 'EG',
           'Hungary': 'HU', 'Russia': 'RU', 'Belarus': 'BY', 'Croatia': 'HR', 'Denmark': 'DK', 'Norway': 'NO', 'Latvia': 'LV', 'Mexico': 'MX', 'Saudi Arabia': 'SA', 'Pakistan': 'PK', 'Uzbekistan': 'UZ', 'Kazakhstan': 'KZ', 'Australia': 'AU', 'New Zealand': 'NZ'}
NAZWA_PL = {'PL': 'Polska', 'CZ': 'Czechy', 'SK': 'Słowacja', 'BG': 'Bułgaria', 'RO': 'Rumunia', 'SI': 'Słowenia', 'HR': 'Chorwacja', 'FR': 'Francja', 'GB': 'Wielka Brytania',
            'FI': 'Finlandia', 'SE': 'Szwecja', 'NL': 'Holandia', 'BE': 'Belgia', 'ES': 'Hiszpania', 'CH': 'Szwajcaria', 'DE': 'Niemcy', 'IT': 'Włochy', 'LT': 'Litwa', 'EE': 'Estonia',
            'LV': 'Łotwa', 'AT': 'Austria', 'UA': 'Ukraina', 'DK': 'Dania', 'NO': 'Norwegia', 'AE': 'Zjednoczone Emiraty Arabskie', 'US': 'Stany Zjednoczone', 'CA': 'Kanada',
            'IN': 'Indie', 'KR': 'Korea Południowa', 'JP': 'Japonia', 'CN': 'Chiny', 'ZA': 'RPA', 'BR': 'Brazylia', 'AR': 'Argentyna', 'TR': 'Turcja', 'EG': 'Egipt', 'BD': 'Bangladesz',
            'IR': 'Iran', 'HU': 'Węgry', 'RU': 'Rosja', 'BY': 'Białoruś', 'SA': 'Arabia Saudyjska', 'QA': 'Katar', 'AU': 'Australia', 'MX': 'Meksyk', 'SG': 'Singapur', 'VN': 'Wietnam', 'PH': 'Filipiny', 'PK': 'Pakistan', 'UZ': 'Uzbekistan', 'KZ': 'Kazachstan', 'NZ': 'Nowa Zelandia'}
NAZWA_EN = {'PL': 'Poland', 'CZ': 'Czechia', 'SK': 'Slovakia', 'BG': 'Bulgaria', 'RO': 'Romania', 'SI': 'Slovenia', 'HR': 'Croatia', 'FR': 'France', 'GB': 'United Kingdom',
            'FI': 'Finland', 'SE': 'Sweden', 'NL': 'Netherlands', 'BE': 'Belgium', 'ES': 'Spain', 'CH': 'Switzerland', 'DE': 'Germany', 'IT': 'Italy', 'LT': 'Lithuania', 'EE': 'Estonia',
            'LV': 'Latvia', 'AT': 'Austria', 'UA': 'Ukraine', 'DK': 'Denmark', 'NO': 'Norway', 'AE': 'United Arab Emirates', 'US': 'United States', 'CA': 'Canada', 'IN': 'India',
            'KR': 'South Korea', 'JP': 'Japan', 'CN': 'China', 'ZA': 'South Africa', 'BR': 'Brazil', 'AR': 'Argentina', 'TR': 'Türkiye', 'EG': 'Egypt', 'BD': 'Bangladesh', 'IR': 'Iran',
            'HU': 'Hungary', 'RU': 'Russia', 'BY': 'Belarus', 'SA': 'Saudi Arabia', 'QA': 'Qatar', 'AU': 'Australia', 'MX': 'Mexico', 'SG': 'Singapore', 'VN': 'Vietnam', 'PH': 'Philippines', 'PK': 'Pakistan', 'UZ': 'Uzbekistan', 'KZ': 'Kazakhstan', 'NZ': 'New Zealand'}

def kraj(*teksty, domyslny=None):
    """Pierwszy kraj rozpoznany w lokalizacji (kolejność: przekazane teksty od najbardziej konkretnego)."""
    for t in teksty:
        if not t: continue
        t = t if isinstance(t, str) else ' '.join(str(x) for x in t if x)
        for nazwa, kod in ISO_KOD.items():
            if re.search(r'\b' + re.escape(nazwa) + r'\b', t, re.I): return kod
        m = re.search(r',\s*([A-Z]{2})\b(?!.*,\s*[A-Z]{2}\b)', t)   # "Krakow, PL" / "Madrid, ES"
        if m and m.group(1) in NAZWA_PL: return m.group(1)
        for kod, rx in _KR:
            if rx.search(t): return kod
    return domyslny

def projekt(tytul='', lokalizacja='', tekst='', pracodawca=''):
    """(etykieta, typ) albo (None, None). Najpierw tytuł i lokalizacja, potem treść (pierwsze 4000 znaków)."""
    for n, zrodlo in enumerate((f'{tytul} {lokalizacja}', pracodawca or '', (tekst or '')[:4000])):
        for e, k, t, rx in _PRJ:
            if n == 2 and t == 'ins': continue          # wzmianka o IAEA w treści nie czyni oferty ofertą IAEA
            if rx.search(zrodlo): return e, t
    return None, None

def tylko_analiza(pracodawca='', kraj_kod=None, projekt_et=None, tekst=''):
    if kraj_kod in WYKLUCZONE_KRAJE: return True
    if projekt_et in ANALIZA_PROJEKTY: return True
    return bool(ROSATOM.search(pracodawca or '')) or bool(re.search(r'Rosatom|Росатом|Atomstroyexport|Akkuyu Nükleer|Аккую Нуклеар', (tekst or '')[:3000], re.I))

# --- język ogłoszenia ---------------------------------------------------------------
try:
    from langdetect import DetectorFactory, detect_langs
    DetectorFactory.seed = 0
except Exception:   # brak biblioteki - heurystyka
    detect_langs = None
JEZYKI = {'pl': 'PL', 'en': 'EN', 'fr': 'FR', 'de': 'DE', 'cs': 'CS', 'sk': 'SK', 'bg': 'BG', 'ro': 'RO', 'sl': 'SL', 'hr': 'HR', 'fi': 'FI', 'sv': 'SV',
          'nl': 'NL', 'es': 'ES', 'it': 'IT', 'lt': 'LT', 'et': 'ET', 'lv': 'LV', 'uk': 'UK', 'ru': 'RU', 'ar': 'AR', 'hu': 'HU', 'tr': 'TR', 'da': 'DA', 'no': 'NO', 'pt': 'PT'}
_HEUR = [('PL', r'\b(oraz|wymagania|obowiązk|doświadczen|się|który|będzie|praca)\b'), ('FR', r'\b(et|vous|pour|avec|des|poste|expérience)\b'),
         ('DE', r'\b(und|Sie|mit|für|die|der|Erfahrung)\b'), ('CS', r'\b(a|pro|zkušenost|práce|nabízíme|požadujeme)\b'), ('EN', r'\b(the|and|you|with|experience|will)\b')]

def jezyk(tekst):
    t = re.sub(r'https?://\S+|\S+@\S+', ' ', tekst or '')[:5000]
    if len(t.strip()) < 40: return None
    if detect_langs:
        try:
            l = detect_langs(t)[0]
            return JEZYKI.get(l.lang.split('-')[0], l.lang.upper()[:2])
        except Exception:
            pass
    pkt = {k: len(re.findall(rx, t, re.I)) for k, rx in _HEUR}
    return max(pkt, key=pkt.get) if max(pkt.values()) else None
