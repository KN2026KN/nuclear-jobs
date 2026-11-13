# Szyfrowanie pełnych tekstów ofert w repozytorium publicznym (13.11.2026, decyzja właściciela).
# raw/** i data/kp.sqlite.gz zawierają pełne treści ogłoszeń pracodawców - w repo leżą tylko wersje *.enc.
# Klucz: sekret RAW_KEY (zmienna środowiskowa). Szyfrowanie deterministyczne (AES-GCM, nonce = HMAC z treści):
# ten sam plik daje ten sam szyfrogram, więc niezmienione pliki nie tworzą zmian w git.
# Użycie: python3 kod/szyfr.py szyfruj | odszyfruj
import os, sys, hmac, hashlib, glob
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

CELE = ['raw', 'data/kp.sqlite.gz', 'data/dzien', 'data/panel']   # 13.11.2026: także lista dnia i panel (informacje o ofertach)
MAGIC = b'KNJ1'

def klucze():
    s = os.environ.get('RAW_KEY', '')
    if len(s) < 16:
        if not any(True for _ in pliki_enc()):   # przed migracją (brak plików .enc) - bez zmian w działaniu robota
            print('UWAGA: brak sekretu RAW_KEY - szyfrowanie jeszcze nie włączone'); sys.exit(0)
        sys.exit('Brak sekretu RAW_KEY (min. 16 znaków) - przerywam, żeby nie zapisać jawnych treści w repozytorium publicznym.')
    k = hashlib.pbkdf2_hmac('sha256', s.encode(), b'keura-nuclear-jobs-raw', 200_000, dklen=64)
    return k[:32], k[32:]

def pliki_jawne():
    for c in CELE:
        if os.path.isfile(c): yield c
        for p in glob.glob(c + '/**/*', recursive=True):
            if os.path.isfile(p) and not p.endswith('.enc'): yield p

def pliki_enc():
    for c in CELE:
        if os.path.isfile(c + '.enc'): yield c + '.enc'
        for p in glob.glob(c + '/**/*.enc', recursive=True): yield p

def szyfruj():
    k, km = klucze(); a = AESGCM(k); n = z = 0
    for p in pliki_jawne():
        d = open(p, 'rb').read()
        nonce = hmac.new(km, p.encode() + b'\0' + d, hashlib.sha256).digest()[:12]
        wyj = MAGIC + nonce + a.encrypt(nonce, d, p.encode())
        e = p + '.enc'
        if not (os.path.exists(e) and open(e, 'rb').read() == wyj):
            open(e, 'wb').write(wyj); z += 1
        n += 1
    print(f'szyfruj: plików {n}, zmienionych {z}')

def odszyfruj():
    k, _ = klucze(); a = AESGCM(k); n = 0
    for e in pliki_enc():
        p = e[:-4]; b = open(e, 'rb').read()
        if b[:4] != MAGIC: sys.exit(f'nieznany format: {e}')
        d = a.decrypt(b[4:16], b[16:], p.encode())
        if not (os.path.exists(p) and open(p, 'rb').read() == d):
            open(p, 'wb').write(d)
        n += 1
    print(f'odszyfruj: plików {n}')

if __name__ == '__main__':
    {'szyfruj': szyfruj, 'odszyfruj': odszyfruj}[sys.argv[1]]()
