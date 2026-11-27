"""List and fetch CC BY / CC0 sound effects from Wikimedia Commons (Gravity Sound library, CC BY 4.0) for the v3 mix.

  python3 fetch_audio.py list     -> audio_meta/<query>.json (titles, urls, licences)
  python3 fetch_audio.py get KEY TITLE   -> sfx/<KEY>.<ext> + audio_credits.json
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'EpicDeathsVideoBuild/1.1 (educational video production; low-rate Commons API client)'
API = 'https://commons.wikimedia.org/w/api.php'
META = os.path.join(HERE, 'audio_meta')
SFX = os.path.join(HERE, 'sfx')
CRED = os.path.join(HERE, 'audio_credits.json')
QUERIES = ['Gravity Sound whoosh', 'Gravity Sound impact', 'Gravity Sound hit', 'Gravity Sound riser', 'Gravity Sound pop',
           'Gravity Sound click', 'Gravity Sound sword', 'Gravity Sound arrow', 'Gravity Sound cannon', 'Gravity Sound explosion',
           'Gravity Sound crowd', 'Gravity Sound door', 'Gravity Sound wood', 'Gravity Sound splash', 'Gravity Sound water',
           'Gravity Sound fire', 'Gravity Sound drum', 'Gravity Sound bell', 'Gravity Sound coin', 'Gravity Sound punch',
           'Gravity Sound heartbeat', 'Gravity Sound wind', 'Gravity Sound gun', 'Gravity Sound metal', 'Gravity Sound glass',
           'Gravity Sound cash', 'Gravity Sound magic', 'Gravity Sound transition', 'Gravity Sound boom', 'Gravity Sound swoosh']


def get(url, timeout=60):
    wait = 30
    for _ in range(12):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get('retry-after')
                time.sleep(max(wait, int(ra) + 3 if ra and ra.isdigit() else wait))
                wait = min(wait * 1.5, 240)
                continue
            raise
        except urllib.error.URLError:
            time.sleep(20)
    raise RuntimeError('gave up ' + url)


def listing():
    os.makedirs(META, exist_ok=True)
    for q in QUERIES:
        fp = os.path.join(META, q.replace(' ', '_') + '.json')
        if os.path.exists(fp):
            continue
        params = dict(action='query', generator='search', gsrsearch=q + ' filetype:audio', gsrnamespace=6, gsrlimit=40,
                      prop='imageinfo', iiprop='url|extmetadata|size|mime|mediatype', format='json')
        d = json.loads(get(API + '?' + urllib.parse.urlencode(params)))
        out = []
        for p in d.get('query', {}).get('pages', {}).values():
            ii = p['imageinfo'][0]
            md = ii.get('extmetadata', {})
            out.append(dict(title=p['title'], url=ii.get('url'), size=ii.get('size'), mime=ii.get('mime'),
                            license=md.get('LicenseShortName', {}).get('value', ''), page=ii.get('descriptionurl'),
                            artist=md.get('Artist', {}).get('value', '')[:120]))
        json.dump(out, open(fp, 'w'), indent=0)
        print(time.strftime('%H:%M:%S'), q, len(out), flush=True)
        time.sleep(14)
    print('AUDIO_LIST_DONE', flush=True)


def fetch(key, title):
    os.makedirs(SFX, exist_ok=True)
    params = dict(action='query', titles=title, prop='imageinfo', iiprop='url|extmetadata|mime', format='json')
    d = json.loads(get(API + '?' + urllib.parse.urlencode(params)))
    p = list(d['query']['pages'].values())[0]
    ii = p['imageinfo'][0]
    ext = os.path.splitext(ii['url'])[1].lower()
    data = get(ii['url'])
    path = os.path.join(SFX, key + ext)
    open(path, 'wb').write(data)
    cr = json.load(open(CRED)) if os.path.exists(CRED) else {}
    md = ii.get('extmetadata', {})
    cr[key] = dict(title=title, page=ii.get('descriptionurl'), license=md.get('LicenseShortName', {}).get('value', ''),
                   artist=md.get('Artist', {}).get('value', '')[:200])
    json.dump(cr, open(CRED, 'w'), indent=1)
    print('got', key, title, len(data) // 1024, 'KB', flush=True)
    time.sleep(6)


if __name__ == '__main__':
    if sys.argv[1] == 'list':
        listing()
    elif sys.argv[1] == 'get':
        fetch(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'batch':
        for line in open(sys.argv[2]):
            if line.strip() and not line.startswith('#'):
                k, t = line.strip().split('\t')
                if not any(f.startswith(k + '.') for f in os.listdir(SFX)) if os.path.isdir(SFX) else True:
                    try:
                        fetch(k, t)
                    except Exception as e:
                        print('FAIL', k, t, e, flush=True)
        print('AUDIO_BATCH_DONE', flush=True)
