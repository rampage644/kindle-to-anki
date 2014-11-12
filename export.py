#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import pprint
import re
import service
import sqlite3
import sys
import urllib
import urllib.parse
import urllib.request

def get_lookups(db, timestamp=0):
    conn = sqlite3.connect(db)
    res = []
    for row in conn.execute('select w.stem,l.usage from LOOKUPS as l JOIN WORDS as w on l.word_key=w.id where l.timestamp>?;', (timestamp, )):
        res.append(row)
    conn.close()
    return res

def get_last_timestamp_from_lookup(db):
    conn = sqlite3.connect(db)
    res = conn.execute('select timestamp from WORDS order by timestamp desc limit 1;').fetchall()
    conn.close()
    return res[0][0] if len (res) > 0 else None

def get_last_timestamp(db):
    conn = sqlite3.connect(db)
    res = conn.execute('select time from timestamps order by time desc limit 1;').fetchall()
    conn.close()
    return res[0][0] if len (res) > 0 else None

def update_last_timestamp(db, timestamp):
    conn = sqlite3.connect(db)
    conn.execute('create table if not exists timestamps (time timestamp);')
    conn.execute('insert into timestamps values(?);', (timestamp,))
    conn.commit()
    conn.close()
    


def translate(lingualeo, word):
    result = lingualeo.get_translates(word)

    sound_url = result['sound_url']
    pic_url = result['translate'][0]['pic_url']
    # tr = result['translate'][0]['value']
    tr = [i['value'] for i in result['translate']][:3]
    tr = '<br>'.join(tr)
    transcription = result['transcription']

    return (tr, transcription, sound_url, pic_url)

def extract_filename_from_url(url):
    path = urllib.parse.urlparse(url).path
    return os.path.split(path)[-1]

def download_file(url, path=''):
    try:
        res = urllib.request.urlretrieve(url,
                                         os.path.join(path,
                                                      extract_filename_from_url(url)))
    except:
        res = urllib.request.urlretrieve(url,
                                         os.path.join(path,
                                                      extract_filename_from_url(url)))
    return res

def write_to_csv(file, data):
    with open(file, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter='\t', dialect='unix',
            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            spamwriter.writerow(row)

def highlight_word_in_context(word, context):
    return re.sub(r'{}'.format(word), '<span class=highlight>{}</span>'.format(word), context)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--kindle', help='Path to kindle db file (usually vocab.db)', default='vocab.db')
    parser.add_argument('-m', '--media-path', help='Where to store media files (sounds/images)')
    parser.add_argument('email', help='LinguaLeo account email/login')
    parser.add_argument('pwd', help='LinguaLeo account password')
    parser.add_argument('-o', '--out', help='Output filename', default='output.csv')
    parser.add_argument('-s', '--skip', help='Number of words to skip', default=0, type=int)
    args = parser.parse_args()
    kindle = args.kindle
    media_path = args.media_path if args.media_path else ''
    output = args.out if args.out else sys.stdout
    email = args.email if args.email else ''
    password = args.pwd if args.pwd else ''

    lingualeo = service.Lingualeo(email, password)
    res = lingualeo.auth()
    if 'error_msg' in res and res['error_msg']:
        print (res['error_msg'])
        sys.exit(1)

    lookups = get_lookups(kindle)

    data = []
    for i, (word, context) in enumerate(lookups):
        if i < args.skip:
            continue

        progress = int(100.0 * i / len(lookups))
        print ('[{}%]\ttranslate {}...'.format(progress, word), 
               end='', flush=True)
        tr, transcription, sound_url, img_url = translate(lingualeo, word)
        if sound_url:
            print ('ok, get sound...', end='', flush=True)
            sound, _ = download_file(sound_url, media_path)
            sound = os.path.basename(sound)
        if img_url:
            print ('ok, get image...', end='', flush=True)
            img, _ = download_file(img_url, media_path)
            img = os.path.basename(img)
        print ('ok!')
        data.append((word, transcription, '[sound:{}]'.format(sound),
                     tr, img, highlight_word_in_context(word, context)))

    print ('[100%]\tWrite to file {}...'.format(output), end='', flush=True)
    write_to_csv(output, data)
    print ('ok!')
    sys.exit(0)