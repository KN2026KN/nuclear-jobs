# Usuwa dane kontaktowe rekruterów z surowych plików ofert przed zapisem do publicznego repozytorium (11.11.2026).
# E-maile -> [e-mail], numery telefonów (z +kodem kraju, linki tel:, liczby obok słów tel/phone/telefon) -> [telefon],
# linie „Contact / Kontakt / Recruiter: Imię Nazwisko” -> usunięte. Kwoty wynagrodzeń i identyfikatory zostają.
# Użycie: python3 kod/bez_kontaktow.py raw/2026-11-11 [raw/2026-11-10 ...]   (pliki .json, .json.gz, .txt, .txt.gz)
import sys, os, re, json, gzip

EMAIL = re.compile(r'(mailto:)?[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}')
TEL_HREF = re.compile(r'tel:[+\d\s().\-]{6,}')
TEL_PLUS = re.compile(r'(?<![\w/=])\+\d{1,3}[\s.\-]?\(?\d{1,4}\)?(?:[\s.\-]?\d{2,4}){2,4}(?!\d)')
TEL_SLOWO = re.compile(r'((?:tel|phone|telefon|mobile|mobil|kom|gsm|тел)\.?\s*[:.]?\s*)(\(?\+?\d[\d\s().\-]{6,}\d)', re.I)
OSOBA = re.compile(r'(^|\n)[ \t]*(contact( person)?|kontakt|osoba kontaktowa|recruiter|rekruter|kontaktní osoba|контактное лицо|контакт)[ \t]*:[ \t]*[^\n<:]{2,60}(?=\n|$)', re.I)

def czysc(s):
    if not isinstance(s, str) or not s: return s
    s = EMAIL.sub('[e-mail]', s)
    s = TEL_HREF.sub('tel:[telefon]', s)
    s = TEL_SLOWO.sub(lambda m: m.group(1) + '[telefon]', s)
    s = TEL_PLUS.sub('[telefon]', s)
    return OSOBA.sub(r'\1', s)

def przejdz(o):
    if isinstance(o, dict): return {k: przejdz(v) for k, v in o.items()}
    if isinstance(o, list): return [przejdz(v) for v in o]
    return czysc(o)

def plik(p):
    gz = p.endswith('.gz'); otw = (lambda m: gzip.open(p, m + 't', encoding='utf-8')) if gz else (lambda m: open(p, m, encoding='utf-8'))
    with otw('r') as f: tekst = f.read()
    if '.json' in p:
        try: nowy = json.dumps(przejdz(json.loads(tekst)), ensure_ascii=False)
        except ValueError: nowy = czysc(tekst)
    else: nowy = czysc(tekst)
    if nowy != tekst:
        with otw('w') as f: f.write(nowy)
        return True
    return False

if __name__ == '__main__':
    n = z = 0
    for kat in sys.argv[1:]:
        for root, _, pliki in os.walk(kat):
            for f in pliki:
                if re.search(r'\.(json|txt)(\.gz)?$', f):
                    n += 1; z += plik(os.path.join(root, f))
    print(f'bez_kontaktow: plików {n}, zmienionych {z}')
