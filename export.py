#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import csv
import os
import pprint
import re
import retrying
import service
import sqlite3
import sys
import urllib
import urllib.parse
import urllib.request

TIMESTAMP_PATH = '/home/ramp/.kindle'

def get_lookups(db, timestamp=0):
    conn = sqlite3.connect(db)
    res = []
    for row in conn.execute('select w.stem,l.usage from WORDS as w LEFT JOIN LOOKUPS as l on w.id=l.word_key where w.timestamp>?;', (timestamp,)):
        res.append(row)
    conn.close()
    return res

def get_lookups_from_file(file):
    lookups = [(line.split()[0], 
                ' '.join(line.split()[1:])) for line in open(file, 'r').readlines()]
    return lookups

def get_last_timestamp_from_lookup(db):
    conn = sqlite3.connect(db)
    res = conn.execute('select timestamp from WORDS order by timestamp desc limit 1;').fetchall()
    conn.close()
    return res[0][0] if len (res) > 0 else None

def get_last_timestamp():
    try:
        with open(TIMESTAMP_PATH, 'r') as tfile:
            return int(tfile.readline().strip())
    except Exception as e:
        print (e)
        return 0

def update_last_timestamp(timestamp):
    with open(TIMESTAMP_PATH, 'w') as tfile:
        tfile.write('{}'.format(timestamp))    


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

@retrying.retry(stop_max_attempt_number=3)
def download_file(url, path=''):
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
    parser.add_argument('--kindle', help='Path to kindle db file (usually vocab.db)')
    parser.add_argument('--src', help='Path to plain text file with newline separated list of words')
    parser.add_argument('-m', '--media-path', help='Where to store media files (sounds/images)')
    parser.add_argument('email', help='LinguaLeo account email/login')
    parser.add_argument('pwd', help='LinguaLeo account password')
    parser.add_argument('-o', '--out', help='Output filename', default='output.csv')
    parser.add_argument('-s', '--skip', help='Number of words to skip', default=0, type=int)
    args = parser.parse_args()
    media_path = args.media_path if args.media_path else ''
    output = args.out if args.out else sys.stdout
    email = args.email if args.email else ''
    password = args.pwd if args.pwd else ''

    lingualeo = service.Lingualeo(email, password)
    res = lingualeo.auth()
    if 'error_msg' in res and res['error_msg']:
        print (res['error_msg'])
        sys.exit(1)

    if args.kindle:
        timestamp = get_last_timestamp()
        lookups = get_lookups(args.kindle, timestamp)
    elif args.src:
        lookups = get_lookups_from_file(args.src)
    else:
        print ("No input specified")
        sys.exit(1)

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
            try:
                sound, _ = download_file(sound_url, media_path)
                sound = os.path.basename(sound)
            except:
                sound = ''
        if img_url:
            print ('ok, get image...', end='', flush=True)
            try:
                img, _ = download_file(img_url, media_path)
                img = os.path.basename(img)
            except:
                img = ''
        print ('ok!')
        if not context:
            context = ''
        data.append((word, transcription, '[sound:{}]'.format(sound),
                     tr, img, highlight_word_in_context(word, context)))

    if len(lookups):
        print ('[100%]\tWrite to file {}...'.format(output), end='', flush=True)
        write_to_csv(output, data)
        if args.kindle:
            update_last_timestamp(get_last_timestamp_from_lookup(args.kindle))
        print ('ok!')
    sys.exit(0)
