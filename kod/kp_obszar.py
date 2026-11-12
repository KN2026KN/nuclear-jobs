# Obszar (funkcja) oferty - 16 obszarów zatwierdzonych przez właściciela 12.11.2026 (wariant 4a).
# Rozpoznawanie po tytule (PL, EN, FR, DE, CS, SK, RO, BG, FI, SV, RU), potem po kategorii / dziale ze źródła.
# Kolejność reguł ma znaczenie: pierwsze trafienie wygrywa (konkretne przed ogólnymi).
import re

OBSZARY = [
    'Inżynieria i projektowanie', 'Budowa i montaż', 'Eksploatacja i utrzymanie ruchu', 'Bezpieczeństwo jądrowe i ochrona radiologiczna',
    'Jakość (QA/QC)', 'BHP i środowisko', 'Zarządzanie projektem', 'Zakupy i łańcuch dostaw', 'IT i cyberbezpieczeństwo',
    'Finanse i administracja', 'HR i szkolenia', 'Prawo i regulacje', 'Ochrona fizyczna', 'Badania i rozwój', 'Staże i praktyki', 'Inne']

OBSZARY_EN = {
    'Inżynieria i projektowanie': 'Engineering and design', 'Budowa i montaż': 'Construction and installation',
    'Eksploatacja i utrzymanie ruchu': 'Operations and maintenance', 'Bezpieczeństwo jądrowe i ochrona radiologiczna': 'Nuclear safety and radiation protection',
    'Jakość (QA/QC)': 'Quality (QA/QC)', 'BHP i środowisko': 'Health, safety and environment', 'Zarządzanie projektem': 'Project management',
    'Zakupy i łańcuch dostaw': 'Procurement and supply chain', 'IT i cyberbezpieczeństwo': 'IT and cybersecurity',
    'Finanse i administracja': 'Finance and administration', 'HR i szkolenia': 'HR and training', 'Prawo i regulacje': 'Legal and regulatory',
    'Ochrona fizyczna': 'Physical security', 'Badania i rozwój': 'Research and development', 'Staże i praktyki': 'Internships and graduates', 'Inne': 'Other'}

def _R(*p): return re.compile('|'.join(p), re.I)

REGULY = [
    ('Staże i praktyki', _R(r'new grad', r'placement', r'master thesis', r'thesis', r'praca dyplomow', r'\bintern(ship)?s?\b', r'\bgraduate\b', r'trainee', r'apprentic', r'\bstaż', r'praktyk', r'\bstage\b', r'stagiaire', r'alternan', r'\bpraktikant',
                            r'werkstudent', r'\bv\.?i\.?e\b', r'стаж[её]р', r'практикант', r'harjoittel', r'kesätyö', r'praktikant', r'absolvent', r'student')),
    ('Ochrona fizyczna', _R(r'protec[tț]ie fizic', r'informa[tț]ii clasificate', r'security coordinator', r'security manager', r'security (supervisor|lead)', r'security officer', r'security guard', r'physical security', r'\bguard\b', r'ochron\w* (fizyczn|obiekt|mienia)', r'pracownik ochrony', r'strażnik',
                            r'agent de (sûreté|sécurité)', r'protection physique', r'wachschutz', r'objektschutz', r'ostraha', r'охран', r'vartija', r'väktare', r'firefighter', r'strażak', r'pompier')),
    ('IT i cyberbezpieczeństwo', _R(r'servere', r'informatic', r'ITSM', r'data analy', r'records sys', r'cyber', r'software', r'developer', r'programist', r'programmer', r'devops', r'sysadmin', r'system(s)? administrator',
                                    r'administrator system', r'network (engineer|admin)', r'sieci komputer', r'\bdata (engineer|scientist|analyst)', r'database', 
                                    r'informati', r'\bOT security', r'helpdesk', r'help desk', r'service desk', r'cloud', r'architekt\w* (IT|rozwiązań)', r'solution architect',
                                    r'informatique', r'développeur', r'systèmes d.information', r'informatik', r'системн\w+ администратор', r'программист',
                                    r'информационн', r'tietohallin', r'ohjelmisto', r'digital')),
    ('Bezpieczeństwo jądrowe i ochrona radiologiczna', _R(r'radioprotec', r'radiolog', r'radiac', r'radiați', r'säteily', r'emergency preparedness', r'emergency planning', r'nuclear safety', r'bezpieczeństw\w* jądrow', r'radiation protection', r'radiological', r'radioprotection', r'health physic',
                                    r'ochron\w* radiologiczn', r'dozymetr', r'dosimetr', r'дозиметр', r'радиационн', r'ядерн\w+ безопасност', r'sûreté nucléaire', r'\bsûreté\b',
                                    r'strahlenschutz', r'kernsicherheit', r'radiační ochran', r'jaderná bezpečnost', r'säteilyturv', r'strålskydd', r'reactor safety', r'safety case',
                                    r'safety analys', r'\bPSA\b', r'criticality', r'krytyczno', r'licens', r'licencj', r'permitting', r'pozwoleni', r'regulatory affairs')),
    ('Jakość (QA/QC)', _R(r'qualifications? mat', r'assessor', r'assurance', r'quality', r'\bQA\b', r'\bQC\b', r'\bQA/QC\b', r'jakoś', r'inspector', r'inspektor', r'\bNDT\b', r'\bNDE\b', r'auditor', r'audytor', r'qualité',
                          r'qualitäts', r'kvalit', r'calitat', r'качеств', r'контрол', r'laatu', r'supplier (performance|surveillance|oversight)', r'compliance (engineer|specialist)')),
    ('BHP i środowisko', _R(r'HSEQ', r'\bCDM\b', r'fire watch', r'permit to work', r'securitatea muncii', r'industrial hygien', r'\bH&S\b', r'SHEQ', r'occupational health', r'\bHSE\b', r'\bEHS\b', r'health and safety', r'health & safety', r'safety (officer|advisor|adviser|specialist|engineer|manager|coordinator)',
                            r'\bBHP\b', r'środowisk', r'environment', r'ecolog', r'sustainab', r'sécurité au travail', r'\bQHSE\b', r'arbeitssicherheit', r'umwelt', r'\bBOZP\b',
                            r'охран\w* труда', r'эколог', r'työturvall', r'ympäristö', r'arbetsmiljö', r'miljö')),
    ('Zarządzanie projektem', _R(r'management de proiect', r'implementare proiecte', r'tehnician cn \(documente', r'interface coordinator', r'work pack', r'référentiel', r'planning', r'scheduling', r'surveyor', r'commercial manager', r'\bQS\b', r'owner.s scope', r'project manag', r'program(me)? manag', r'project control', r'project director', r'kierownik projekt', r'menedżer projekt', r'\bPMO\b', r'planner',
                                 r'planist', r'scheduler', r'harmonogram', r'cost (engineer|control|estimat)', r'estimator', r'kosztorys', r'chef de projet', r'planificat',
                                 r'projektleiter', r'projektmanager', r'projektový manažer', r'руководитель проект', r'менеджер проект', r'planerare', r'projektipäällik', r'project engineer',
                                 r'delivery (lead|manager)', r'interface manag', r'document control', r'dokumentacj\w* projekt', r'project (coordinator|assistant)')),
    ('Zakupy i łańcuch dostaw', _R(r'achizi[tț]', r'manutention', r'bus driver', r'\bPCV\b', r'transport', r'procurement', r'purchas', r'buyer', r'sourcing', r'supply chain', r'logisti', r'warehouse', r'magazyn', r'zakup', r'zaopatrz', r'contracts? (manager|specialist|officer|administrator)',
                                   r'kontrakt', r'subcontract', r'expedit', r'achats?\b', r'acheteur', r'approvisionn', r'einkauf', r'beschaffung', r'nákup', r'закупк', r'снабжен', r'склад', r'кладовщ',
                                   r'hankin', r'inköp', r'materials? (manag|coordinat)', r'inventory')),
    ('Prawo i regulacje', _R(r'ethics', r'compliance manager', r'legal', r'lawyer', r'counsel', r'attorney', r'prawn', r'radc\w+ prawn', r'adwokat', r'juris', r'juriste', r'avocat', r'jurist', r'právník', r'юрист',
                             r'правов', r'lakimies', r'paralegal', r'export control', r'trade compliance')),
    ('HR i szkolenia', _R(r'labou?r relations', r'employee relations', r'\bER (advisor|partner|manager)', r'people (governance|partner)', r'organisation set-up', r'\bHR\b', r'human resources', r'recruit', r'rekrut', r'talent', r'payroll', r'płac', r'kadr', r'personel\b', r'training', r'szkoleni', r'instructor',
                          r'instruktor', r'trainer', r'learning', r'formation', r'formateur', r'ressources humaines', r'personal(abteilung|referent)', r'schulung', r'personalist',
                          r'кадр', r'персонал', r'обучени', r'инструктор', r'henkilöstö', r'koulut', r'rekryter', r'utbild')),
    ('Finanse i administracja', _R(r'economist', r'contabil', r'administrare platform', r'referendar', r'naczelni(k|czka) wydział', r'exec admin', r'public affairs', r'trader', r'facilities', r'visitor centre', r'station guide', r'commercial\b', r'financ', r'account', r'księgow', r'controlling', r'controller', r'audit\w* (finans|wewnętrzn)', r'tax\b', r'podat', r'treasury', r'budget',
                                   r'admin(istrat|istracj)', r'assistant', r'asystent', r'sekretar', r'secretar', r'office', r'biur', r'receptio', r'recepcj', r'communicat', r'komunikacj',
                                   r'marketing', r'public relations', r'stakeholder', r'sales', r'sprzeda', r'business develop', r'comptab', r'gestionnaire', r'buchhalt',
                                   r'verwaltung', r'účetní', r'бухгалтер', r'финанс', r'секретар', r'администрат\w+ (офис|отдел)', r'kirjanpi', r'talous', r'ekonom', r'customer service')),
    ('Badania i rozwój', _R(r'research', r'scientist', r'naukow', r'badawcz', r'\bR&D\b', r'\bB\+R\b', r'phd', r'doktor', r'postdoc', r'post-doc', r'laborat', r'chemist', r'chemik',
                            r'physicist', r'fizyk', r'recherche', r'chercheur', r'forsch', r'wissenschaft', r'výzkum', r'исследоват', r'научн', r'tutkija', r'forskare')),
    ('Budowa i montaż', _R(r'steelfixer', r'machine driver', r'offshore (sub )?agent', r'travaux', r'technical manager - concrete', r'plater', r'plating', r'carpenter', r'shuttering', r'mixer driver', r'temporary works', r'plant supervisor', r'site delivery', r'construction', r'budow', r'montaż', r'monter', r'installat', r'erection', r'commissioning', r'rozruch', r'site (manager|supervisor|engineer)', r'kierownik robót',
                           r'inspektor nadzoru', r'foreman', r'brygadzist', r'majster', r'superintendent', r'weld', r'spaw', r'pipefitter', r'fitter', r'rigger', r'scaffold', r'rusztow',
                           r'civil (works|engineer)', r'cieśl', r'zbrojarz', r'betoniarz', r'chantier', r'génie civil', r'soudeur', r'tuyauteur', r'monteur', r'bauleiter', r'baustelle',
                           r'montáž', r'stavb', r'svář', r'монтаж', r'строител', r'сварщик', r'пусконалад', r'asennu', r'rakennus', r'hitsaaja', r'montör', r'svetsare', r'bygg')),
    ('Eksploatacja i utrzymanie ruchu', _R(r'operare', r'tehnician', r'déchets', r'reparator', r'intretinere', r'întreținere', r'\bLOTO\b', r'lock.?out', r'operator', r'operations', r'eksploatac', r'maintenance', r'utrzymani\w* ruchu', r'\bmechanic\b', r'\bmechanik\b', r'electrician', r'elektryk',
                           r'technician', r'technik', r'shift', r'zmian\w*\b', r'control room', r'reactor operator', r'outage', r'remont', r'serwis', r'service engineer', r'repair', r'naprawa',
                           r'fuel handl', r'chemistry technician', r'conduite', r'exploitation', r'maintenance', r'électricien', r'mécanicien', r'instandhaltung', r'betrieb',
                           r'schicht', r'údržb', r'obsluh', r'эксплуатац', r'ремонт', r'оператор', r'электромонт', r'слесар', r'дежурн', r'kunnossapi', r'käyttö', r'underhåll', r'drift')),
    ('Inżynieria i projektowanie', _R(r'inginer', r'fizician', r'méthode', r'control systems', r'\bICS\b', r'nuclear engr', r'\bengr\b', r'engineer', r'inżynier', r'design', r'projekt(ant|owani)', r'konstrukt', r'architect', r'architekt', r'drafts', r'kreślar', r'\bCAD\b', r'\bBIM\b',
                           r'\bI&C\b', r'automati', r'analyst', r'analityk', r'specialist', r'specjalist', r'ingénieur', r'ingenieur', r'concepteur', r'dessinat', r'konstruktér', r'inženýr',
                           r'projektant', r'инженер', r'конструктор', r'проектировщ', r'insinööri', r'suunnitteli', r'ingenjör', r'konstruktör', r'expert', r'ekspert')),
]

KATEGORIE = [   # kategoria / dział ze źródła (np. Bechtel, SuccessFactors) - gdy tytuł nic nie powiedział
    (r'project controls|project management', 'Zarządzanie projektem'), (r'supply chain|procurement|contracts', 'Zakupy i łańcuch dostaw'),
    (r'human resources|\bHR\b|training', 'HR i szkolenia'), (r'legal', 'Prawo i regulacje'), (r'environmental|safety & health|\bHSE\b|\bEHS\b', 'BHP i środowisko'),
    (r'construction', 'Budowa i montaż'), (r'engineering', 'Inżynieria i projektowanie'), (r'quality', 'Jakość (QA/QC)'),
    (r'information technology|\bIT\b|digital', 'IT i cyberbezpieczeństwo'), (r'finance|administration|communications|sales', 'Finanse i administracja'),
    (r'operations|maintenance', 'Eksploatacja i utrzymanie ruchu'), (r'research', 'Badania i rozwój'), (r'intern|graduate|student', 'Staże i praktyki')]

# skróty wielkimi literami - z rozróżnianiem wielkości liter (inaczej „it”, „she”, „si” łapałyby zwykłe słowa)
SKROTY = {'IT i cyberbezpieczeństwo': re.compile(r'\b(IT|ICT|SAP|ERP|OT|SI|DSI)\b|\bIT[- ]'), 'BHP i środowisko': re.compile(r'\bSHE\b'),
          'Finanse i administracja': re.compile(r'\bPR\b')}

OGOLNE = re.compile(r'^\s*((młodszy|starszy|główny)\s+)?specjalist\w*\s*$|^\s*ogłoszenie\s*$|^\s*обяви за работа\s*$|^\s*(job|offre|oferta)\s*$', re.I)

def obszar(tytul, kategoria='', tekst=''):
    """Tytuł, potem kategoria źródła; przy tytułach ogólnych („specjalista”, „OGŁOSZENIE”) - początek treści."""
    w = _obszar(tytul, kategoria)
    if (w == 'Inne' or OGOLNE.search(tytul or '')) and tekst:
        w2 = _obszar(re.sub(r'\s+', ' ', tekst)[:400], '')
        if w2 != 'Inne': return w2
    return w

def _obszar(tytul, kategoria=''):
    t = ' ' + re.sub(r'\s+', ' ', tytul or '') + ' '
    for nazwa, rx in REGULY:
        if rx.search(t) or (nazwa in SKROTY and SKROTY[nazwa].search(t)): return nazwa
    for rx, nazwa in KATEGORIE:
        if re.search(rx, kategoria or '', re.I): return nazwa
    return 'Inne'
