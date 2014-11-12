# Kindle-to-Anki

Import from kindle vocabulary to anki-ready csv file. Uses LingvoLeo service to
get translataion, transcription, pronounciation and some image.

Find all lookups (words you've been looking for while reading Kindle) and contexts. Retrieve translations from LinguaLeo, export to `csv` file.

Take first three translations for each word.

Written in Python3.

# Usage

```
usage: export.py [-h] [--kindle KINDLE] [-m MEDIA_PATH] [-o OUT] [-s SKIP]
                 email pwd

positional arguments:
  email                 LinguaLeo account email/login
  pwd                   LinguaLeo account password

optional arguments:
  -h, --help            show this help message and exit
  --kindle KINDLE       Path to kindle db file (usually vocab.db)
  -m MEDIA_PATH, --media-path MEDIA_PATH
                        Where to store media files (sounds/images)
  -o OUT, --out OUT     Output filename
  -s SKIP, --skip SKIP  Number of words to skip
```

    export.py -m <path-to-your-kindle-vocab.db> -m <path-to-anki-collection.media> -o output.csv <login> <pass>