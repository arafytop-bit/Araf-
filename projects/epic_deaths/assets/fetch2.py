"""Slow, metadata-first fetch from Wikimedia Commons (the image host throttles unidentified clients hard).

Phase 1 (API, commons.wikimedia.org): search each key, keep ranked candidates + licence metadata -> meta/<key>.json
Phase 2 (upload.wikimedia.org): download ONE candidate per key (original if small, else the 1280px thumb),
         paced and honouring Retry-After -> picked/<key>.jpg + credits.json

  python3 fetch2.py run            # both phases, resumable
  python3 fetch2.py next KEY       # mark current pick for KEY as wrong and fetch the next candidate
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
UA = 'EpicDeathsVideoBuild/1.1 (educational video production; low-rate Commons API client)'
API = 'https://commons.wikimedia.org/w/api.php'
META = os.path.join(HERE, 'meta')
PICKED = os.path.join(HERE, 'picked')
CREDITS = os.path.join(HERE, 'credits.json')
API_PACE, DL_PACE = 15.0, 12.0

# ordered by first appearance in the video
QUERIES = [
    ('tycho', 'Tycho Brahe portrait', ['File:Tycho Brahe.JPG']),
    ('chrysippus', 'Chrysippus bust British Museum', []),
    ('rasputin', 'Grigori Rasputin photograph', []),
    ('harald_portrait', 'Harald Hardrada', []),
    ('varangian', 'Varangian Guard Skylitzes', []),
    ('golden_horn_chain', 'chain Golden Horn Istanbul Archaeology Museum', []),
    ('york', 'York Minster city walls', []),
    ('heimskringla', 'Heimskringla manuscript', []),
    ('snorri', 'Snorri Sturluson Vigeland statue', []),
    ('stamford_arbo', 'Arbo Slaget ved Stamford bridge', []),
    ('anglo_saxon_chronicle', 'Anglo-Saxon Chronicle Peterborough manuscript', []),
    ('bayeux_harold', 'Bayeux Tapestry Harold death', ['File:Bayeux Tapestry scene57 Harold death.jpg']),
    ('leo_attila', 'Raphael Meeting between Leo the Great and Attila', []),
    ('feast_attila', 'Than Mór Attila lakomája', []),
    ('hun_archer', 'Hungarian horse archer reenactment', []),
    ('solidus', 'Theodosius II solidus', []),
    ('attila_death', 'Ferenc Paczka death of Attila', []),
    ('crassus_bust', 'Marcus Licinius Crassus bust Louvre', []),
    ('fire_rome', 'Hubert Robert Fire of Rome', []),
    ('spartacus_statue', 'Spartacus Foyatier Louvre', []),
    ('parthian_archer', 'Parthian shot horse archer', []),
    ('aquila', 'Roman legion aquila standard reenactment', []),
    ('greek_theater', 'Epidaurus theatre', []),
    ('theater_masks', 'mosaic theatrical masks tragedy comedy', []),
    ('kouros_phigalia', 'Arrhachion kouros', []),
    ('pankration_vase', 'pankration Panathenaic amphora', []),
    ('olympia_stadium', 'Olympia stadium entrance tunnel', []),
    ('olive_wreath', 'olive wreath kotinos', []),
    ('pyrrhus', 'Pyrrhus bust Naples', []),
    ('yi_statue', 'Statue of Admiral Yi Sun-sin Gwanghwamun', []),
    ('nelson', 'Horatio Nelson Lemuel Francis Abbott portrait', ['File:HoratioNelson1.jpg']),
    ('turtle_ship', 'Geobukseon', []),
    ('myeongnyang', 'Uldolmok Myeongnyang strait', []),
    ('hideyoshi', 'Toyotomi Hideyoshi portrait Kodai-ji', []),
    ('hundred_won', '100 won coin Yi Sun-sin', []),
    ('seoul_gwanghwamun', 'Gwanghwamun Square Seoul', []),
    # real backdrops for character scenes (BLUEPRINT 5.4 SCENE: characters composited on a real photo)
    ('stamford_river', 'River Derwent Stamford Bridge', []),
    ('hagia_sophia', 'Hagia Sophia interior', []),
    ('puszta', 'Hortobágy puszta grassland', []),
    ('carrhae', 'Harran plain Turkey', []),
    ('gyeongbokgung', 'Geunjeongjeon Gyeongbokgung throne hall', []),
    # ---- v3 rebuild: real environments and artifacts for every scene ----
    ('olav_stiklestad', 'Arbo Olav den helliges fall Stiklestad', []),
    ('fjord', 'Geirangerfjord', []),
    ('norway_forest', 'Norwegian spruce forest', []),
    ('theodosian_walls', 'Theodosian Walls Constantinople', []),
    ('dungeon', 'dungeon prison cell castle', []),
    ('golden_horn', 'Golden Horn Istanbul', []),
    ('st_sophia_kyiv', 'Saint Sophia Cathedral Kyiv', []),
    ('bayeux_edward', 'Bayeux Tapestry Edward death bed', []),
    ('bayeux_harold_crown', 'Bayeux Tapestry Harold crowned', []),
    ('william_statue', 'William the Conqueror statue Falaise', []),
    ('harald_glass', 'Harald Hardrada stained glass', []),
    ('salt_shaker', 'salt shaker table', []),
    ('oseberg_ship', 'Oseberg ship Vikingskipshuset', []),
    ('yorkshire_field', 'Yorkshire countryside summer field', []),
    ('gravestone', 'old gravestone churchyard', []),
    ('roman_forum', 'Roman Forum view', []),
    ('grey_cattle', 'Hungarian grey cattle', []),
    ('silver_dish', 'Mildenhall Great Dish', []),
    ('wooden_bowl', 'wooden bowl spoon', []),
    ('old_door', 'old wooden door', []),
    ('plutarch', 'Plutarch Chaeronea bust Delphi', []),
    ('rome_model', 'Plastico di Roma antica', []),
    ('appian_way', 'Via Appia Antica', []),
    ('pompey_bust', 'Pompey bust Ny Carlsberg', []),
    ('caesar_bust', 'Tusculum portrait Caesar', []),
    ('legion_reenact', 'Roman legionaries reenactment', []),
    ('camel', 'dromedary camel', []),
    ('prima_porta', 'Augustus Prima Porta cuirass detail', []),
    ('orodes_coin', 'Orodes II drachm', []),
    ('boxer_rest', 'Boxer at Rest Quirinal', []),
    ('leonidas', 'Leonidas statue Sparta', []),
    ('palaestra', 'Palaestra Olympia', []),
    ('olympia_museum', 'Archaeological Museum of Olympia statue', []),
    ('busanjin', 'Busanjin Sunjeoldo', []),
    ('hansan', 'Hansan-do battle', []),
    ('nanjung_ilgi', 'Nanjung ilgi', []),
    ('korean_drum', 'Korean traditional drum buk', []),
    ('noryang', 'Noryang Namhae', []),
    ('night_sea', 'sea at night moon waves', []),
    ('tv_set', 'vintage television set', []),
]
PREFER = {
    'tycho': ['tycho'], 'chrysippus': ['chrysippus', 'crisip'], 'rasputin': ['rasputin'], 'harald_portrait': ['harald', 'hardr'],
    'varangian': ['varang'], 'golden_horn_chain': ['chain', 'zincir'], 'york': ['york'], 'heimskringla': ['kringla'],
    'snorri': ['snorri'], 'stamford_arbo': ['stamford', 'arbo'], 'anglo_saxon_chronicle': ['chronicle'], 'bayeux_harold': ['bayeux'],
    'leo_attila': ['leo', 'attila'], 'feast_attila': ['attila', 'lakom', 'feast'], 'hun_archer': ['archer', 'íjász', 'horse'],
    'solidus': ['solidus'], 'attila_death': ['attila'], 'crassus_bust': ['crassus'], 'fire_rome': ['fire', 'incendie'],
    'spartacus_statue': ['spartac'], 'parthian_archer': ['parthian'], 'aquila': ['aquila', 'eagle'],
    'greek_theater': ['epidaur'], 'theater_masks': ['mask'], 'kouros_phigalia': ['phigal', 'arrhach', 'arrich'], 'pankration_vase': ['pankration'],
    'olympia_stadium': ['stadium', 'stadion'], 'olive_wreath': ['wreath', 'kotinos'], 'pyrrhus': ['pyrrhus'],
    'yi_statue': ['yi sun', 'sun-sin'], 'nelson': ['nelson'], 'turtle_ship': ['turtle', 'geobuk', 'kobuk'],
    'myeongnyang': ['uldolmok', 'myeongnyang'], 'stamford_river': ['derwent', 'stamford'], 'hagia_sophia': ['hagia', 'sophia', 'ayasofya'],
    'puszta': ['hortob', 'puszta'], 'carrhae': ['harran'], 'gyeongbokgung': ['geunjeongjeon', 'gyeongbok'], 'hideyoshi': ['hideyoshi'], 'hundred_won': ['won'], 'seoul_gwanghwamun': ['gwanghwamun'],
}
PREFER.update({
    'olav_stiklestad': ['stiklestad', 'olav'], 'fjord': ['geiranger'], 'norway_forest': ['forest', 'skog', 'spruce'],
    'theodosian_walls': ['wall', 'theodos'], 'dungeon': ['dungeon', 'cell', 'prison'], 'golden_horn': ['golden horn', 'haliç'],
    'st_sophia_kyiv': ['sophia', 'софі'], 'bayeux_edward': ['bayeux'], 'bayeux_harold_crown': ['bayeux'], 'william_statue': ['william', 'guillaume', 'falaise'],
    'harald_glass': ['harald', 'hardrada'], 'salt_shaker': ['salt'], 'oseberg_ship': ['oseberg'], 'yorkshire_field': ['yorkshire', 'field', 'dales'],
    'gravestone': ['grave', 'tomb', 'headstone'], 'roman_forum': ['forum', 'foro'], 'grey_cattle': ['grey cattle', 'szürke', 'grey'],
    'silver_dish': ['mildenhall', 'dish'], 'wooden_bowl': ['wooden', 'bowl'], 'old_door': ['door'], 'plutarch': ['plutarch'],
    'rome_model': ['plastico', 'model'], 'appian_way': ['appia', 'appian'], 'pompey_bust': ['pompe'], 'caesar_bust': ['caesar', 'tusculum'],
    'legion_reenact': ['legion', 'reenact', 'roman'], 'camel': ['camel', 'dromedar'], 'prima_porta': ['prima porta', 'primaporta'],
    'orodes_coin': ['orodes'], 'boxer_rest': ['boxer', 'pugile'], 'leonidas': ['leonidas'], 'palaestra': ['palaestra', 'palestra'],
    'olympia_museum': ['olympia'], 'busanjin': ['busanjin', '부산진'], 'hansan': ['hansan'], 'nanjung_ilgi': ['nanjung', '난중'],
    'korean_drum': ['drum', 'buk', '북'], 'noryang': ['noryang', '노량'], 'night_sea': ['night', 'moon'], 'tv_set': ['television', 'tv'],
})
OK_LICENSES = ('public domain', 'pd', 'cc0', 'cc by', 'cc-by', 'attribution', 'no restrictions')
BAD_WORDS = ('map', 'coat of arms', 'signature', 'logo', 'flag', 'diagram', 'plan of', 'svg', 'icon', 'chart')


def log(*a):
    print(time.strftime('%H:%M:%S'), *a, flush=True)


def _get(url, timeout=90):
    wait = 30
    for attempt in range(14):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                ra = e.headers.get('retry-after')
                w = int(ra) + 5 if ra and ra.isdigit() else wait
                w = max(w, wait)
                log('  429', str(e.reason)[:50], 'wait', w)
                time.sleep(min(w, 900)); wait = min(wait * 1.5, 300); continue
            if e.code in (500, 502, 503, 504):
                time.sleep(30); continue
            raise
        except urllib.error.URLError as e:
            log('  url error', str(e)[:120]); time.sleep(30); continue
    raise RuntimeError('gave up ' + url)


def api(params):
    params = dict(params, format='json')
    d = json.loads(_get(API + '?' + urllib.parse.urlencode(params), 60))
    time.sleep(API_PACE)
    return d


def strip_html(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', s or '')).strip()


def clean(u):
    return (u or '').split('?')[0]


def candidates_from(pages):
    out = []
    for p in sorted(pages, key=lambda p: p.get('index', 0)):
        ii = (p.get('imageinfo') or [{}])[0]
        md = ii.get('extmetadata', {})
        lic = strip_html(md.get('LicenseShortName', {}).get('value', ''))
        out.append(dict(title=p['title'], url=clean(ii.get('url')), w=ii.get('width', 0), h=ii.get('height', 0),
                        size=ii.get('size', 0), mime=ii.get('mime', ''), page=clean(ii.get('descriptionurl')), license=lic,
                        artist=strip_html(md.get('Artist', {}).get('value', ''))[:160],
                        credit=strip_html(md.get('Credit', {}).get('value', ''))[:200],
                        desc=strip_html(md.get('ImageDescription', {}).get('value', ''))[:300]))
    return out


def usable(c):
    t = c['title'].lower()
    return (c['mime'] in ('image/jpeg', 'image/png') and any(k in c['license'].lower() for k in OK_LICENSES)
            and not any(b in t for b in BAD_WORDS) and min(c['w'], c['h']) >= 450)


def phase1():
    os.makedirs(META, exist_ok=True)
    for key, q, titles in QUERIES:
        fp = os.path.join(META, key + '.json')
        if os.path.exists(fp):
            continue
        cands = []
        prop = dict(prop='imageinfo', iiprop='url|extmetadata|size|mime')
        if titles:
            d = api(dict(action='query', titles='|'.join(titles), **prop))
            cands += candidates_from([p for p in d.get('query', {}).get('pages', {}).values() if 'imageinfo' in p])
        d = api(dict(action='query', generator='search', gsrsearch=q + ' filetype:bitmap', gsrnamespace=6, gsrlimit=10, **prop))
        seen = {c['title'] for c in cands}
        cands += [c for c in candidates_from(d.get('query', {}).get('pages', {}).values()) if c['title'] not in seen]
        cands = [c for c in cands if usable(c)]
        json.dump(dict(key=key, query=q, cands=cands, tried=[]), open(fp, 'w'), indent=1, ensure_ascii=False)
        log('meta', key, len(cands), '|', cands[0]['title'][:70] if cands else '-')


def dl_url(c, width=1280):
    """MediaWiki's thumb.php on the commons host (the media hosts throttle unidentified clients much harder)."""
    name = c['title'].split(':', 1)[1].replace(' ', '_')
    w = min(width, c['w']) if c['w'] else width
    return 'https://commons.wikimedia.org/w/thumb.php?' + urllib.parse.urlencode(dict(f=name, w=w))


def fetch_one(key):
    fp = os.path.join(META, key + '.json')
    m = json.load(open(fp))
    pref = PREFER.get(key, [])
    free = lambda c: any(t in c['license'].lower() for t in ('public domain', 'cc0', 'pd'))  # noqa: E731
    ranked = sorted(m['cands'], key=lambda c: (not any(t in c['title'].lower() for t in pref), min(c['w'], c['h']) < 480,
                                               not free(c)))
    for c in ranked:
        if c['title'] in m['tried']:
            continue
        m['tried'].append(c['title'])
        json.dump(m, open(fp, 'w'), indent=1, ensure_ascii=False)
        if download_cand(key, c):
            return True
    log('no more candidates for', key)
    return False


def download_cand(key, c):
    try:
        data = _get(dl_url(c))
    except Exception as e:
        log('  dl fail', key, c['title'][:60], str(e)[:80]); time.sleep(DL_PACE); return False
    os.makedirs(PICKED, exist_ok=True)
    ext = '.png' if c['mime'] == 'image/png' else '.jpg'
    raw = os.path.join(PICKED, key + '.src' + ext)
    open(raw, 'wb').write(data)
    to_jpg(raw, os.path.join(PICKED, key + '.jpg'))
    cr = json.load(open(CREDITS)) if os.path.exists(CREDITS) else {}
    cr[key] = {k: c[k] for k in ('title', 'page', 'license', 'artist', 'credit')}
    json.dump(cr, open(CREDITS, 'w'), indent=1, ensure_ascii=False)
    log('got', key, '<-', c['title'][:80], len(data) // 1024, 'KB')
    time.sleep(DL_PACE)
    return True


def to_jpg(src, dst, max_side=2200):
    import cv2
    im = cv2.imread(src, cv2.IMREAD_COLOR)
    if im is None:
        raise RuntimeError('unreadable ' + src)
    h, w = im.shape[:2]
    k = min(1.0, max_side / max(h, w))
    if k < 1:
        im = cv2.resize(im, (int(w * k), int(h * k)), interpolation=cv2.INTER_AREA)
    cv2.imwrite(dst, im, [cv2.IMWRITE_JPEG_QUALITY, 92])
    os.remove(src)


def phase2():
    for key, _, _ in QUERIES:
        if os.path.exists(os.path.join(PICKED, key + '.jpg')):
            continue
        fetch_one(key)


LIC_URL = {'cc0': 'https://creativecommons.org/publicdomain/zero/1.0/'}


def license_url(lic):
    m = re.match(r'cc[ -]by(-sa)?[ -]?([\d.]+)?', lic.lower())
    if not m:
        return LIC_URL.get(lic.lower().strip(), '')
    kind = 'by-sa' if m.group(1) else 'by'
    return f'https://creativecommons.org/licenses/{kind}/{m.group(2) or "4.0"}/'


def write_credits(order):
    cr = json.load(open(CREDITS)) if os.path.exists(CREDITS) else {}
    lines = ['IMAGE CREDITS (all via Wikimedia Commons)', '']
    for key in order:
        c = cr.get(key)
        if not c:
            continue
        name = re.sub(r'\.(jpe?g|png|tiff?)$', '', c['title'].split(':', 1)[1], flags=re.I)
        lic = c['license'] or 'see file page'
        who = re.sub(r'^(.+?)\1$', r'\1', c['artist'] or 'unknown author')
        if 'public domain' in lic.lower() or lic.lower() in ('pd', 'cc0'):
            lines.append(f'- {name}: {who}, {lic}. {c["page"]}')
        else:
            lu = license_url(lic)
            lines.append(f'- {name}: {who}, {lic}{" (" + lu + ")" if lu else ""}. {c["page"]}')
    out = os.path.join(HERE, '..', 'CREDITS.md')
    open(out, 'w').write('\n'.join(lines) + '\n')
    return out


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'run':
        phase1()
        phase2()
        log('FETCH2_DONE')
    elif cmd == 'meta':
        phase1()
    elif cmd == 'credits':
        print(write_credits([k for k, _, _ in QUERIES]))
    elif cmd == 'use':                      # use KEY=IDX ... : take a specific candidate
        for a in sys.argv[2:]:
            key, idx = a.split('=')
            m = json.load(open(os.path.join(META, key + '.json')))
            download_cand(key, m['cands'][int(idx)])
    elif cmd == 'next':
        for k in sys.argv[2:]:
            p = os.path.join(PICKED, k + '.jpg')
            if os.path.exists(p):
                os.remove(p)
            fetch_one(k)
