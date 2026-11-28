#!/usr/bin/env python3
"""Fetch only published immutable Zenodo v1.0.0 UVB data and verify byte identity."""
from pathlib import Path
import hashlib
import urllib.request
import zipfile

HERE=Path(__file__).resolve().parent
URL="https://zenodo.org/api/records/15367103/files/tairaeli/Metagalactic_Ultraviolet_Background_Data_Tables-v1.0.0.zip/content"
SHA="afd470b9fd934234e7f6e815d6887814a2ff8767e61f0d2a8e6187efde8d0d55"
MD5="2c8790767866ca446d13660043224d67"
DEST=HERE/"source_original_v1.zip"
def main():
    if DEST.is_file():
        b=DEST.read_bytes()
    else:
        with urllib.request.urlopen(URL,timeout=90) as f:
            b=f.read()
    if hashlib.sha256(b).hexdigest()!=SHA or hashlib.md5(b).hexdigest()!=MD5:
        raise ValueError("original Zenodo source identity mismatch: refuse use")
    if not DEST.is_file():
        DEST.write_bytes(b)
    with zipfile.ZipFile(DEST) as z:
        if z.testzip() is not None: raise ValueError("source ZIP CRC mismatch")
    print("PASS original Zenodo source",len(b),SHA)
if __name__=="__main__":main()
