# Zawody (13.11.2026) - słownik do porównań wynagrodzeń między krajami i firmami.
# Tytuł oferty w dowolnym z języków źródeł (PL, EN, FR, DE, CS, SK, SV, FI, RO, BG, IT, ES, RU) -> jeden zawód.
# Kolejność ma znaczenie: pierwszy pasujący wzorzec wygrywa (konkretne przed ogólnymi).
import re

def _R(*p): return re.compile('|'.join(p), re.I)

# (klucz, nazwa PL, nazwa EN, wzorzec)
ZAWODY = [
    ('inspektor_spawalniczy', 'Inspektor spawalniczy / IWI', 'Welding inspector', _R(r'weld\w* inspect', r'inspector.{0,6}weld', r'inspektor\w* spaw', r'\bCWI\b', r'\bIWI\b', r'inspecteur soudage', r'контролер сварк')),
    ('inzynier_spawalnik', 'Inżynier spawalnik / IWE', 'Welding engineer', _R(r'weld\w* (engineer|manager|coordinator|supervisor|specialist)', r'inżynier\w* spaw', r'\bIWE\b', r'ingénieur soudage', r'schweißfachingenieur', r'svařovací inženýr', r'инженер-сварщик', r'svetsingenjör', r'responsable soudage')),
    ('spawacz', 'Spawacz', 'Welder', _R(r'\bwelder', r'welding operator', r'spawacz', r'soudeur', r'schwei(ß|ss)er', r'svářeč', r'zvárač', r'svetsare', r'hitsaaja', r'sudor\b', r'saldator', r'soldador', r'сварщик', r'заварчик')),
    ('ndt', 'Badania nieniszczące (NDT)', 'NDT technician', _R(r'\bNDT\b', r'\bNDE\b', r'non.?destructive', r'nieniszcz', r'ultrason', r'radiograph', r'\bCND\b', r'contrôle non destructif', r'zerstörungsfrei', r'неразрушающ')),
    ('kierownik_budowy', 'Kierownik budowy / robót, nadzór', 'Site / construction manager', _R(r'site manager', r'construction manager', r'superintendent', r'kierownik\w* (budowy|robót)', r'inspektor nadzoru', r'conducteur de travaux', r'bauleiter', r'stavbyvedoucí', r'прораб', r'начальник участка')),
    ('inspektor_qc', 'Inspektor QC / kontroli jakości', 'QC inspector', _R(r'\bQC\b', r'quality control', r'kontrol\w* jako', r'inspector', r'inspektor', r'contrôleur qualité', r'qualitätsprüfer', r'kontrolor', r'контролер')),
    ('qa', 'Specjalista / inżynier QA, zapewnienie jakości', 'QA engineer / specialist', _R(r'\bQA\b', r'quality assurance', r'quality (engineer|specialist|manager|lead|advisor|coordinator)', r'zapewnieni\w* jako', r'jakoś', r'qualité', r'qualitäts', r'kvalit', r'calitat', r'качеств', r'laatu')),
    ('audytor', 'Audytor', 'Auditor', _R(r'auditor', r'audytor', r'auditeur', r'аудитор')),
    ('ochrona_radiologiczna', 'Ochrona radiologiczna / dozymetria', 'Radiation protection', _R(r'radiation protection', r'radiolog', r'health physic', r'dozymetr', r'dosimetr', r'radioprotec', r'strahlenschutz', r'radiační', r'säteily', r'strålskydd', r'дозиметр', r'радиацион')),
    ('bezp_jadrowe', 'Bezpieczeństwo jądrowe / analizy bezpieczeństwa', 'Nuclear safety / safety case', _R(r'nuclear safety', r'safety case', r'safety analys', r'\bPSA\b', r'reactor safety', r'bezpieczeństw\w* jądrow', r'sûreté', r'kernsicherheit', r'jadern\w* bezpečnost', r'ядерн\w+ безопасност')),
    ('licencjonowanie', 'Licencjonowanie i dozór', 'Licensing and regulatory', _R(r'licens', r'licencj', r'permitting', r'regulatory', r'dozor', r'dozór', r'autorisation')),
    ('operator_reaktora', 'Operator reaktora / bloku', 'Reactor / plant operator', _R(r'reactor operator', r'control room', r'\bRO\b', r'\bSRO\b', r'operator\w* (bloku|reaktora|elektrowni)', r'opérateur', r'conduite', r'оператор', r'reaktoroperatör', r'operátor')),
    ('chemia', 'Chemik / technik chemii', 'Chemist / chemistry technician', _R(r'chemist', r'chemik', r'chemi(stry|e)', r'chimi', r'химик', r'kemist')),
    ('paliwo', 'Paliwo jądrowe i obsługa paliwa', 'Nuclear fuel', _R(r'\bfuel\b', r'paliw', r'combustible', r'brennstoff', r'топлив')),
    ('odpady', 'Odpady promieniotwórcze i likwidacja', 'Radwaste and decommissioning', _R(r'waste', r'odpad', r'decommission', r'likwidac', r'déchets', r'démantèlement', r'rückbau', r'отход', r'вывод из эксплуат')),
    ('aparatura', 'AKPiA / I&C, automatyka', 'I&C / automation', _R(r'\bI&C\b', r'\bC&I\b', r'instrumentation', r'automati', r'\bAKPiA\b', r'control systems', r'contrôle.commande', r'leittechnik', r'\bMaR\b', r'КИП', r'автоматик')),
    ('elektryk', 'Elektryk / inżynier elektryk', 'Electrical engineer / electrician', _R(r'electric', r'elektry', r'électri', r'elektrik', r'электр', r'sähkö', r'elkraft')),
    ('mechanik', 'Mechanik / inżynier mechanik', 'Mechanical engineer / mechanic', _R(r'mechanic', r'mechani', r'mécani', r'maschinenbau', r'strojní', r'механ', r'kone', r'maskin')),
    ('rurociagi', 'Rurociągi / monter rurociągów', 'Piping / pipefitter', _R(r'piping', r'pipefitter', r'pipe fitter', r'rurociąg', r'monter\w* rur', r'tuyaut', r'rohrleitung', r'potrubí', r'трубопровод', r'rör')),
    ('budowlany', 'Inżynier budowlany / konstrukcje', 'Civil / structural engineer', _R(r'civil', r'structural', r'budowl', r'konstrukc\w* (bud|stal)', r'génie civil', r'bauingenieur', r'stavební', r'строител', r'rakennus')),
    ('brygadzista', 'Brygadzista / mistrz', 'Foreman / supervisor', _R(r'foreman', r'brygadzist', r'majster', r'mistrz', r'chef d.équipe', r'vorarbeiter', r'polier', r'мастер', r'бригадир')),
    ('monter', 'Monter / ślusarz', 'Fitter / mechanical technician', _R(r'machinist', r'\bfitter', r'monter', r'ślusarz', r'monteur', r'montér', r'слесар', r'монтажник', r'asentaja', r'montör')),
    ('rzemioslo_bud', 'Rzemiosło budowlane (cieśla, zbrojarz, rigger, rusztowania)', 'Construction trades (carpenter, steel fixer, rigger, scaffolder)', _R(r'carpenter', r'cieśl', r'steel ?fixer', r'zbrojarz', r'rigger', r'scaffold', r'rusztow', r'plater', r'plating', r'shuttering', r'concrete', r'betoniarz', r'charpentier', r'coffreur', r'zimmermann', r'плотник', r'арматурщик', r'такелаж')),
    ('operator_maszyn', 'Operator maszyn / kierowca', 'Plant operator / driver', _R(r'(tractor|crane|plant|machine|excavator|dumper|forklift) operator', r'driver', r'kierowca', r'operator\w* (dźwigu|żurawia|koparki|wózka)', r'conducteur d.engins', r'grutier', r'kranführer', r'крановщик', r'водител', r'машинист')),
    ('rozruch', 'Rozruch (commissioning)', 'Commissioning', _R(r'commission', r'rozruch', r'mise en service', r'inbetriebnahme', r'uvádění do provozu', r'пусконалад')),
    ('utrzymanie_ruchu', 'Utrzymanie ruchu / technik', 'Maintenance technician', _R(r'\bLOTO\b', r'outage', r'maintenance', r'utrzymani', r'technician', r'technik\b', r'technicien', r'instandhaltung', r'údržb', r'ремонт', r'техник', r'kunnossapi', r'underhåll', r'tehnician')),
    ('projektant', 'Projektant / konstruktor / CAD', 'Designer / CAD', _R(r'architect', r'design', r'projektant', r'konstruktor', r'\bCAD\b', r'\bBIM\b', r'drafts', r'kreślar', r'dessinat', r'concepteur', r'konstrukt', r'проектировщ', r'конструктор', r'suunnitteli')),
    ('inzynier_jadrowy', 'Inżynier jądrowy / reaktorowy', 'Nuclear / reactor engineer', _R(r'nuclear engr', r'nuclear engineer', r'reactor engineer', r'inżynier\w* jądrow', r'ingénieur nucléaire', r'kerntechni', r'jaderný inženýr', r'инженер-ядерщик', r'physic', r'fizyk', r'physicien', r'физик')),
    ('kierownik_projektu', 'Kierownik projektu / programu', 'Project / programme manager', _R(r'project manag', r'program(me)? manag', r'project director', r'kierownik\w* projekt', r'chef de projet', r'projektleiter', r'projektov\w* manažer', r'руководитель проект', r'projektipäällik')),
    ('planista', 'Planista / kontrola projektu / koszty', 'Planner / project controls', _R(r'surveyor', r'planner', r'planning', r'scheduler', r'project control', r'cost (engineer|control)', r'estimator', r'quantity surveyor', r'planist', r'kosztorys', r'planificat', r'планиров')),
    ('dokumentacja', 'Dokumentacja / kontrola dokumentów', 'Document control', _R(r'document control', r'document controller', r'dokumentac', r'records', r'gestion documentaire')),
    ('zakupy', 'Zakupy / kontrakty', 'Procurement / contracts', _R(r'procurement', r'purchas', r'buyer', r'sourcing', r'contracts?', r'kontrakt', r'zakup', r'acheteur', r'achat', r'einkauf', r'nákup', r'закуп', r'inköp', r'hankin')),
    ('lancuch_dostaw', 'Łańcuch dostaw / jakość dostawców / logistyka', 'Supply chain / supplier quality', _R(r'supply chain', r'supplier', r'logisti', r'warehouse', r'magazyn', r'expedit', r'fournisseur', r'lieferant', r'логист', r'склад')),
    ('bhp', 'BHP / HSE / ochrona środowiska', 'HSE / environment', _R(r'industrial hygien', r'sustainab', r'\bHSE\b', r'\bEHS\b', r'\bSHE\b', r'\bSHEQ\b', r'health and safety', r'health & safety', r'safety (officer|advisor|adviser|coordinator|specialist)', r'\bBHP\b', r'środowisk', r'environment', r'sécurité au travail', r'\bQHSE\b', r'arbeitssicherheit', r'охран\w* труда', r'эколог')),
    ('it', 'IT / programista / administrator', 'IT / software / sysadmin', _R(r'\bITSM\b', r'(?-i:\bSAP\b)', r'(?-i:\bIT\b)', r'software', r'developer', r'programist', r'programmer', r'devops', r'sysadmin', r'system(s)? administrator', r'cyber', r'informati', r'\bdata (engineer|scientist|analyst)', r'network', r'cloud', r'développeur', r'программист')),
    ('finanse', 'Finanse / księgowość / controlling', 'Finance / accounting', _R(r'trader', r'financ', r'account', r'księgow', r'controll', r'treasury', r'comptab', r'buchhalt', r'účetní', r'бухгалт', r'ekonom', r'economist', r'contabil')),
    ('hr', 'HR / rekrutacja / szkolenia', 'HR / recruitment / training', _R(r'employee relations', r'labou?r relations', r'\bHR\b', r'human resources', r'recruit', r'rekrut', r'talent', r'payroll', r'kadr', r'trainer', r'training', r'szkoleni', r'instructor', r'instruktor', r'ressources humaines', r'formateur', r'кадр', r'персонал')),
    ('prawnik', 'Prawnik', 'Lawyer / legal', _R(r'legal', r'lawyer', r'counsel', r'attorney', r'prawn', r'radca', r'juriste', r'avocat', r'jurist', r'právník', r'юрист')),
    ('administracja', 'Administracja / asystent / biuro', 'Administration / office', _R(r'admin', r'assistant', r'asystent', r'secretar', r'sekretar', r'office', r'biur', r'receptio', r'recepcj', r'referendar', r'gestionnaire', r'секретар')),
    ('komunikacja', 'Komunikacja / PR / sprzedaż', 'Communications / sales', _R(r'communicat', r'komunikacj', r'marketing', r'public relations', r'public affairs', r'stakeholder', r'sales', r'sprzeda', r'business develop')),
    ('ochrona_fizyczna', 'Ochrona fizyczna / straż', 'Security officer / fire', _R(r'security (officer|guard|manager|coordinator)', r'guard', r'ochron\w* (fizyczn|obiekt)', r'strażnik', r'firefighter', r'strażak', r'pompier', r'agent de sûreté', r'wachschutz', r'охран')),
    ('naukowiec', 'Naukowiec / badacz', 'Researcher / scientist', _R(r'research', r'scientist', r'naukow', r'badawcz', r'postdoc', r'phd', r'doktor', r'chercheur', r'forscher', r'výzkum', r'исследоват', r'научн', r'tutkija', r'forskare')),
    ('staz', 'Staż / praktyki / absolwent', 'Intern / graduate', _R(r'new grad', r'placement', r'thesis', r'intern(ship)?\b', r'\bgraduate\b', r'trainee', r'apprentic', r'\bstaż', r'praktyk', r'stagiaire', r'alternan', r'werkstudent', r'стажер', r'kesätyö', r'student')),
    ('kierownik', 'Kierownik / dyrektor (inne)', 'Manager / director (other)', _R(r'manager', r'director', r'head of', r'kierownik', r'dyrektor', r'naczelnik', r'responsable', r'directeur', r'leiter', r'vedoucí', r'руководител', r'начальник', r'директор', r'päällikkö', r'chef\b')),
    ('inzynier', 'Inżynier (inne)', 'Engineer (other)', _R(r'engineer', r'inżynier', r'ingénieur', r'ingenieur', r'inženýr', r'inginer', r'ingegnere', r'ingeniero', r'insinööri', r'ingenjör', r'инженер')),
    ('specjalista', 'Specjalista / analityk (inne)', 'Specialist / analyst (other)', _R(r'specialist', r'specjalist', r'analyst', r'analityk', r'expert', r'ekspert', r'spécialiste', r'consultant', r'konsultant', r'специалист', r'аналитик', r'advisor', r'adviser', r'doradca')),
]

import unicodedata
def _norm(x):
    x = unicodedata.normalize('NFD', (x or '').lower().replace('ё', 'е'))
    x = ''.join(c for c in x if unicodedata.category(c) != 'Mn')
    return ' ' + re.sub(r'[^0-9a-zа-яіїєґ&]+', ' ', x).strip() + ' '

_SLOW = None
def _ze_slownika(tytul):
    """13.11.2026: gdy wzorce nie pasują - słownik wielojęzyczny (kp_zawody_slownik), najdłuższe trafienie od początku słowa."""
    global _SLOW
    if _SLOW is None:
        from kp_zawody_slownik import slownik
        _SLOW = sorted({(_norm(w).strip(), k) for k, d in slownik().items() for ws in d.values() for w in ws if len(_norm(w).strip()) >= 5},
                       key=lambda x: -len(x[0]))
    t = _norm(tytul)
    for w, k in _SLOW:
        if ' ' + w in t: return k
    return None

def zawod(tytul):
    t = ' ' + re.sub(r'\s+', ' ', tytul or '') + ' '
    for k, pl, en, rx in ZAWODY:
        if rx.search(t): return k
    return _ze_slownika(tytul) or 'inne'

NAZWY = {k: (pl, en) for k, pl, en, _ in ZAWODY}
NAZWY['inne'] = ('Inne', 'Other')

# Poziom stanowiska (13.11.2026) - wielojęzycznie, te same nazwy co kp_db.lvl, żeby porównywać odpowiedniki: zawód + poziom.
POZIOMY = ['Praktyka lub staż', 'Junior / wykonawczy', 'Specjalista', 'Senior lub ekspert', 'Kierownik']
_PZ = [
    ('Praktyka lub staż', r'intern|trainee|apprenti|graduate|stage\b|stagiaire|alternan|praktik|praktyk|stażyst|\bstaż|ausbildung|azubi|werkstudent|tirocin|becari|стаж|практикант|випускник|выпускник'),
    ('Kierownik', r'director|manager|\bhead\b|superintendent|team lead|supervisor|deputy|chief|kierownik|dyrektor|naczelnik|leiter\b|leiterin|direct(eur|rice)|responsable|chef d|jefe|director|responsabile|capo|vedouc|ředitel|riaditeľ|chef\b|päällikkö|johtaja|șef|vezető|ръководител|начальник|руководител|директор|керівник|müdür'),
    ('Senior lub ekspert', r'senior|\blead\b|principal|expert|ekspert|starsz|główn|chartered|confirm|exp[eé]riment|erfahren|esperto|zkušen|seniorn?\b|vanhempi|старш|ведущ|главн|провідн|kıdemli|\bsr\b|\bIII\b|\bIV\b'),
    ('Junior / wykonawczy', r'junior|młodsz|assistant|asystent|technician|technik\b|operator|helper|pomocnik|worker|laborer|labourer|débutant|einsteiger|mladší|младш|помощник|\bjr\b|\bI\b'),
]
def poziom(tytul):
    t = ' ' + (tytul or '') + ' '
    for nazwa, rx in _PZ:
        if re.search(rx, t, re.I): return nazwa
    return 'Specjalista'
