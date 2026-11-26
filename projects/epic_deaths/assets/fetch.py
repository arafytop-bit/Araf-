"""Find and download freely licensed images from Wikimedia Commons.

  python3 fetch.py search            -> candidates/<key>/*.jpg + candidates/index.json + contact sheets
  python3 fetch.py pick key=idx ...  -> copies chosen files into picked/ and writes credits.json
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'EpicDeathsVideoBuild/1.0 (educational video production; uses Commons API politely)'
API = 'https://commons.wikimedia.org/w/api.php'

QUERIES = {
    # intro
    'tycho': 'Tycho Brahe portrait painting',
    'chrysippus': 'Chrysippus bust',
    'rasputin': 'Grigori Rasputin photograph',
    # Harald
    'stamford_arbo': 'Peter Nicolai Arbo Stamford Bridge',
    'harald_portrait': 'Harald Hardrada',
    'varangian': 'Varangian Guard Skylitzes',
    'constantinople': 'Constantinople medieval painting walls',
    'golden_horn_chain': 'Golden Horn chain Istanbul Archaeology Museum',
    'longship': 'Oseberg ship Viking Ship Museum',
    'heimskringla': 'Heimskringla manuscript',
    'snorri': 'Snorri Sturluson statue',
    'anglo_saxon_chronicle': 'Anglo-Saxon Chronicle manuscript page',
    'stamford_bridge_site': 'Stamford Bridge battlefield memorial',
    'bayeux_harold': 'Bayeux Tapestry Harold death arrow',
    'york': 'York city walls Micklegate',
    # Attila
    'leo_attila': 'Raphael Meeting between Leo the Great and Attila',
    'feast_attila': 'Mór Than Feast of Attila',
    'delacroix_attila': 'Delacroix Attila Italy',
    'attila_death': 'Death of Attila painting',
    'solidus': 'Theodosius II solidus gold coin',
    'hun_archer': 'Hun horse archer reenactment',
    # Crassus
    'crassus_bust': 'Marcus Licinius Crassus bust Louvre',
    'fire_rome': 'Hubert Robert Fire of Rome',
    'spartacus_statue': 'Spartacus Foyatier Louvre',
    'parthian_archer': 'Parthian horse archer relief',
    'aquila': 'Roman aquila eagle standard',
    'greek_theater': 'Epidaurus ancient theatre',
    'theater_masks': 'Roman theatre masks mosaic',
    # Arrichion
    'pankration_vase': 'pankration amphora',
    'olympia_stadium': 'Olympia ancient stadium',
    'kouros_phigalia': 'Kouros Phigalia Olympia museum',
    'olive_wreath': 'olive wreath kotinos',
    # Midroll
    'pyrrhus': 'Pyrrhus of Epirus bust',
    # Yi Sun-sin
    'nelson': 'Horatio Nelson portrait Lemuel Francis Abbott',
    'yi_statue': 'Statue of Admiral Yi Sun-sin Gwanghwamun',
    'turtle_ship': 'Geobukseon turtle ship replica',
    'myeongnyang': 'Uldolmok strait Myeongnyang',
    'hideyoshi': 'Toyotomi Hideyoshi portrait',
    'atakebune': 'Atakebune Japanese warship',
    'korean_navy_painting': 'Battle of Hansan Island painting',
    'hundred_won': '100 won coin South Korea',
    'seoul_gwanghwamun': 'Gwanghwamun Square Seoul',
}

PACE = 7.0
OK_LICENSES = ('public domain', 'pd', 'cc0', 'cc by', 'cc-by', 'attribution')


def _get(url, timeout=60):
    delay = 30
    for attempt in range(9):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                data = r.read()
            time.sleep(PACE)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get('retry-after')
                wait = max(delay, int(ra) + 3 if ra and ra.isdigit() else 0)
                print('  429, waiting', wait, 's', flush=True); time.sleep(wait); delay = min(delay * 2, 300); continue
            raise
        except urllib.error.URLError as e:
            print('  url error', e, 'retry', flush=True); time.sleep(15); continue
    raise RuntimeError('gave up ' + url)


def api(params):
    params = dict(params, format='json')
    return json.loads(_get(API + '?' + urllib.parse.urlencode(params), 30))


def download(url, path):
    data = _get(url)
    with open(path, 'wb') as f:
        f.write(data)


def strip_html(s):
    import re
    return re.sub(r'<[^>]+>', '', s or '').strip()


def thumb_url(ii, width=1280):
    """The API's own thumbnail URL (iiurlwidth) - always a size the image servers accept."""
    return ii.get('thumburl') or ii.get('url')


def search_all(n=4, width=1280):
    os.makedirs(os.path.join(HERE, 'candidates'), exist_ok=True)
    index = {}
    for key, q in QUERIES.items():
        done = os.path.join(HERE, 'candidates', 'done_' + key)
        if os.path.exists(done):
            index[key] = json.load(open(done)); continue
        res = api(dict(action='query', generator='search', gsrsearch=q + ' filetype:bitmap', gsrnamespace=6, gsrlimit=10,
                       prop='imageinfo', iiprop='url|extmetadata|size|mime', iiurlwidth=width))
        pages = sorted(res.get('query', {}).get('pages', {}).values(), key=lambda p: p.get('index', 99))
        cands = []
        for p in pages:
            ii = (p.get('imageinfo') or [{}])[0]
            md = ii.get('extmetadata', {})
            lic = strip_html(md.get('LicenseShortName', {}).get('value', ''))
            if ii.get('mime') not in ('image/jpeg', 'image/png', 'image/tiff', 'image/webp'):
                continue
            if not any(k in lic.lower() for k in OK_LICENSES):
                continue
            cands.append(dict(title=p['title'], thumb=thumb_url(ii, width), page=ii.get('descriptionurl'), license=lic,
                              artist=strip_html(md.get('Artist', {}).get('value', ''))[:120],
                              credit=strip_html(md.get('Credit', {}).get('value', ''))[:160], w=ii.get('width'), h=ii.get('height')))
            if len(cands) >= n:
                break
        d = os.path.join(HERE, 'candidates', key)
        os.makedirs(d, exist_ok=True)
        for i, c in enumerate(cands):
            fp = os.path.join(d, f'{i}.jpg')
            try:
                download(c['thumb'], fp)
                c['file'] = fp
            except Exception as e:
                c['file'] = None; print('dl fail', key, i, str(e)[:120], flush=True)
        index[key] = cands
        json.dump(cands, open(done, 'w'))
        print(key, len(cands), sum(1 for c in cands if c.get('file')), flush=True)
    json.dump(index, open(os.path.join(HERE, 'candidates', 'index.json'), 'w'), indent=1, ensure_ascii=False)


def sheets(per_sheet=8):
    import cv2
    import numpy as np
    index = json.load(open(os.path.join(HERE, 'candidates', 'index.json')))
    keys = list(index)
    for s in range(0, len(keys), per_sheet):
        rows = []
        for key in keys[s:s + per_sheet]:
            tiles = []
            for i, c in enumerate(index[key][:6]):
                im = cv2.imread(c['file']) if c.get('file') else None
                if im is None:
                    im = np.zeros((180, 240, 3), np.uint8)
                h, w = im.shape[:2]
                k = 180 / h
                im = cv2.resize(im, (max(1, int(w * k)), 180))
                im = im[:, :300] if im.shape[1] > 300 else np.hstack([im, np.zeros((180, 300 - im.shape[1], 3), np.uint8)])
                cv2.putText(im, f'{i} {c["license"][:14]}', (4, 172), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
                tiles.append(im)
            while len(tiles) < 6:
                tiles.append(np.zeros((180, 300, 3), np.uint8))
            row = np.hstack(tiles)
            lab = np.zeros((24, row.shape[1], 3), np.uint8)
            cv2.putText(lab, key, (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            rows.append(np.vstack([lab, row]))
        cv2.imwrite(os.path.join(HERE, 'candidates', f'sheet_{s // per_sheet}.jpg'), np.vstack(rows), [cv2.IMWRITE_JPEG_QUALITY, 80])
    print('sheets written')


def pick(args):
    import shutil
    index = json.load(open(os.path.join(HERE, 'candidates', 'index.json')))
    os.makedirs(os.path.join(HERE, 'picked'), exist_ok=True)
    cp = os.path.join(HERE, 'credits.json')
    credits = json.load(open(cp)) if os.path.exists(cp) else {}
    for a in args:
        key, idx = a.split('=')
        c = index[key][int(idx)]
        shutil.copy(c['file'], os.path.join(HERE, 'picked', key + '.jpg'))
        credits[key] = {k: c[k] for k in ('title', 'page', 'license', 'artist', 'credit')}
    json.dump(credits, open(cp, 'w'), indent=1, ensure_ascii=False)
    print('picked', len(args))


if __name__ == '__main__':
    if sys.argv[1] == 'search':
        search_all()
        sheets()
    elif sys.argv[1] == 'sheets':
        sheets()
    elif sys.argv[1] == 'pick':
        pick(sys.argv[2:])
