# Kindle-to-Anki

Import from kindle vocabulary to anki-ready csv file. Uses LingvoLeo service to
get translataion, transcription, pronounciation and some image.

Find all lookups (words you've been looking for while reading Kindle) and contexts. Retrieve translations from LinguaLeo, export to `csv` file.

Take first three translations for each word.

Written in Python3.

# Usage

```
usage: export.py [-h] [--kindle KINDLE] [--src SRC] [-m MEDIA_PATH] [-o OUT]
                 [-s SKIP]
                 email pwd

positional arguments:
  email                 LinguaLeo account email/login
  pwd                   LinguaLeo account password

optional arguments:
  -h, --help            show this help message and exit
  --kindle KINDLE       Path to kindle db file (usually vocab.db)
  --src SRC             Path to plain text file with newline separated list of
                        words
  -m MEDIA_PATH, --media-path MEDIA_PATH
                        Where to store media files (sounds/images)
  -o OUT, --out OUT     Output filename
```

Use `--kindle` switch to export from recent Kindle lookups. Use `--src` switch to export from
plain text file.

It should be formatted as follows:

    word1 context1
    word2 context2
    ...
    wordN contextN

Word and context are splitted by space. So, first occurence is word and remaining is context.

When using Kindle as input last timestamp is written to `~/.kindle`. During next import only new lookups are exported. One can manipulate value written to `~/.kindle` to get only needed words from Kindle.