"""Word-keyed storyboard for "Most Epic Deaths". Host shots fill every gap automatically
(build.py); callouts (C) overlay whatever is on screen."""
from cast import *  # noqa: F401,F403

BEATS, CALLS, HOSTS, OVERLAYS = [], [], [], []


def B(trigger, kind, **kw):
    BEATS.append(dict(trigger=trigger, kind=kind, **kw))


def C(trigger, text, hold=2.3):
    CALLS.append(dict(trigger=trigger, text=text, hold=hold))


def H(trigger, **kw):           # force host-shot settings at this phrase (zoom/expr/pose/look)
    HOSTS.append(dict(trigger=trigger, **kw))


def S(trigger, chars=(), props=(), bg='black', **kw):
    B(trigger, 'scene', chars=list(chars), props=list(props), bg=bg, **kw)


def CH(pal, x, **kw):
    return dict(pal=pal, x=x, **kw)


def PR(name, x, y, size=100, **kw):
    return dict(name=name, x=x, y=y, size=size, **kw)


def PH(trigger, img, **kw):
    B(trigger, 'photo', img=img, **kw)


def CARD(trigger, type_, **kw):
    B(trigger, 'card', type=type_, **kw)


def MAP(trigger, region, **kw):
    B(trigger, 'map', region=region, **kw)


# ============================== INTRO ==============================
B('These are the most epic', 'kinetic', until="Now, if you've", lines=[
    (250, [('THE', 70, 'silver', 'the most'), ('MOST', 70, 'silver', 'most epic'), ('EPIC', 118, 'red', 'epic deaths')], 0.62),
    (470, [('DEATHS', 150, 'silver', 'deaths in')], 0.50),
    (680, [('IN', 78, 'silver', 'in human'), ('HUMAN', 92, 'silver', 'human history'), ('HISTORY', 92, 'silver', 'history. Now')], 0.74)])
H("Now, if you've", expr='talk')
CARD('the greatest hits', 'playlist', title='HISTORY YOUTUBE: GREATEST HITS', until="This isn't one", items=[
    dict(text="Tycho Brahe's bladder", img='tycho', meta='4.1M views · every year', at="Tycho Brahe's"),
    dict(text='Died laughing at a donkey', img='chrysippus', meta='3.8M views · every year', at='The philosopher'),
    dict(text="Rasputin won't stay dead", img='rasputin', meta='6.2M views · every year', at='Rasputin refusing')],
    overlay_icon='recycle', overlay_at='recycles')
H("This isn't one of those", zoom=True, expr='smug', pose='point')
S('people who wrote them down', bg='hall', chars=[CH(SCRIBE, 760, expr='shock'), CH(SCRIBE, 1160, expr=[(None, 'nervous'), ('barely believe', 'shock')], flip=True)],
  props=[PR('book', 960, 760, 80)])
C('wins a fight', 'WINS A FIGHT... AFTER DYING')
C('wins a battle', 'WINS A BATTLE... THE SAME WAY')
H('every entry tops', expr='grin', pose='hips')
H("Let's get into it", zoom=True, expr='smile', pose='wave')

# ============================== HARALD ==============================
B('Harald Hardrada.', 'title', num=1, name=['HARALD', 'HARDRADA'], img='harald_portrait', pal=HARALD, sfx='hit', hold=2.0)
C('hard ruler', 'HARDRADA = "HARD RULER"')
CARD('no small talk', 'bio', pal=HARALD, name='Harald Hardrada', handle='@hard_ruler · Norway', until="And if you're", lines=[
    dict(text='King of Norway (eventually)'), dict(text='Professional Viking'), dict(text='NO SMALL TALK', at='no small talk')])
H("I've seen Vikings", expr='skeptic', pose='chin')
S('TV Vikings', props=[PR('tv', 960, 520, 230)], chars=[CH(VIK_TEE, 960, R=70, y=470, expr='grin')])
PH('Harald was real', 'harald_portrait')
S('final boss', chars=[CH(HARALD, 960, R=140, expr='angry', pose='hips')], boss='HARALD HARDRADA', boss_sub='FINAL BOSS OF THE VIKING AGE')
H('speedrun his', expr='grin', pose='point')
OVERLAYS.append(dict(trigger='speedrun his', kind='timer', until="that's just the warm-up"))
C('At about fifteen', 'AGE 15')
S('his half-brother Olaf', bg='field', chars=[CH(HARALD_YOUNG, 720, tag='HARALD (15)', expr='talk'), CH(OLAF, 1200, tag='OLAF', expr='angry', flip=True)])
S('They lose. Olaf dies.', bg='field', chars=[CH(HARALD_YOUNG, 720, expr=[(None, 'shock'), ('Olaf dies', 'sad')]), CH(OLAF, 1200, flip=True, expr='sad', exit_at='Olaf dies')])
S('hides out at a farm', bg='forest', props=[PR('house', 1250, 700, 160)], chars=[CH(HARALD_YOUNG, 760, expr='nervous', pose='idle')])
MAP('flees all the way', 'viking_route', until='and joins the Varangian', icon='longship', stops=[
    ('Farm', 'NORWAY', None), ('Novgorod', 'RUSSIA', 'Russia and Ukraine'), ('Kyiv', 'KYIV', 'Ukraine'),
    ('Constantinople', 'CONSTANTINOPLE', 'turns up in Constantinople')])
PH('Varangian Guard', 'varangian', until="the Byzantine emperor's")
S("Byzantine emperor's elite", bg='hall', chars=[CH(VARANGIAN, 560, expr='deadpan'), CH(BYZ, 960, expr='smug', tag='EMPEROR'), CH(VARANGIAN, 1360, expr='deadpan', flip=True)],
  tag_all='VARANGIAN GUARD')
MAP('all over the Mediterranean', 'viking_route', pins=[('Sicily', 'SICILY', 'Mediterranean'), ('Bulgaria', 'BULGARIA', 'Mediterranean and'),
                                                      ('Jerusalem', 'JERUSALEM', 'piles up')], hold=2.2)
S('piles up a fortune', chars=[CH(HARALD, 700, expr='grin', pose='hips')], props=[PR('gold_pile', 1250, 700, 160, at='fortune')])
S('thrown in prison', chars=[CH(HARALD, 960, expr=[(None, 'deadpan'), ('breaks out', 'smug')])],
  props=[PR('jail', 960, 560, 330, z=5, kw={'broken': False}, exit_at='breaks out'), PR('jail', 960, 560, 330, z=5, at='breaks out', kw={'broken': True})])
S('blind an emperor', bg='hall', chars=[CH(BYZ, 960, expr='shock')], censor=(960, 370, 330, 80))
S('escapes by sailing', bg='sea', props=[PR('chain', 960, 700, 220), PR('longship', 520, 560, 170, at='escapes by sailing', move=(820, -30), move_frames=60)], until='giant iron chain')
PH('giant iron chain', 'golden_horn_chain', pip=True, until='One ship snaps')
S('One ship snaps', bg='sea', props=[PR('longship', 820, 620, 150, rot=-24), PR('longship', 1120, 640, 150, rot=28)], hold=1.4)
H('His makes it', zoom=True, expr='grin', pose='wave')
S('marries a princess', bg='hall', chars=[CH(HARALD, 720, expr='smile'), CH(PRINCESS, 1200, expr='smile', flip=True, tag='PRINCESS OF KYIV')],
  props=[PR('icon', 960, 330, 60, kw={'kind': 'heart'})], until='becomes King of Norway')
S('becomes King of Norway', chars=[CH(HARALD_CROWN, 960, R=130, expr='smug', pose='hips', tag='KING OF NORWAY')])
H("that's just the warm-up", zoom=True, expr='smug')
C('1066', '1066')
S('King of England dies', bg='hall', props=[PR('bed', 960, 760, 190)], chars=[CH(EDWARD, 900, y=690, R=70, rot=-90, expr='sleep')], hold=1.8)
S('three different men', bg='hall', until='So Harald sails', props=[PR('crown', 960, 220, 90)], chars=[
    CH(GODWINSON, 520, tag='HAROLD GODWINSON', at='Harold Godwinson', expr='smug'),
    CH(WILLIAM, 960, tag='WILLIAM OF NORMANDY', at='William of Normandy', expr='angry'),
    CH(HARALD, 1400, tag='HARALD HARDRADA', at='the third is our guy', expr='grin', flip=True)])
MAP('sails for England', 'north_sea', icon='longship', stops=[('Norway', 'NORWAY', None), ('Humber', '', 'with around 300')], until='smashes the first')
C('300 ships', '~300 SHIPS')
S('smashes the first English', bg='field', chars=[CH(HARALD, 640, expr='angry', pose='point'), CH(ENG, 1180, expr='shock', flip=True), CH(ENG, 1480, expr='nervous', flip=True)])
PH('takes York', 'york', caption='YORK')
H('pretty much thinks', expr='smug', pose='hips')
H("here's the problem", zoom=True, expr='skeptic', pose='chin')
PH('comes from one book', 'heimskringla', until='written in Iceland')
PH('Snorri Sturluson', 'snorri')
C('160 years after', '160 YEARS LATER')
S('grain of salt', props=[PR('salt', 960, 540, 230)], hold=1.6, sfx='pop')
H('what Snorri describes', zoom=True, expr='shock')
C('September 25th', 'SEPTEMBER 25TH, 1066')
MAP('a place called Stamford Bridge', 'north_sea', zoom=2.2, focus='York', pins=[('York', 'YORK', None), ('Stamford Bridge', 'STAMFORD BRIDGE', 'Stamford Bridge')], hold=2.4)
S('weather is gorgeous', bg='field', props=[PR('sun', 330, 230, 120)], chars=[CH(VIK_TEE, 1100, expr='grin', pose='hips')])
S('leave their armor back', bg='sea', props=[PR('longship', 1300, 600, 200)], chars=[CH(VIK_TEE, 640, expr='smile', pose='wave', look=(0.25, 0))])
CARD('just shields', 'inventory', title='LOADOUT: STAMFORD BRIDGE', until='very merry', items=[
    dict(name='SHIELD', rarity='COMMON', at='shields'), dict(name='HELMET', rarity='COMMON', at='helmets'),
    dict(name='SPEAR + SWORD', rarity='COMMON', at='spears'), dict(name='ARMOR', rarity='LEFT ON SHIP', at='swords')], strike=3, strike_at='swords')
S('very merry', bg='field', props=[PR('sun', 300, 220, 110)], chars=[CH(VIK_TEE, 600, expr='grin'), CH(VIK_TEE2, 960, expr='smile', pose='wave'), CH(VIK_TEE, 1320, expr='grin', flip=True)])
MAP('racing north', 'north_sea', icon='crown', stops=[('London', 'LONDON', None), ('York', 'YORK', 'something like 40')], hold=3.0)
C('40 miles a day', '40 MILES A DAY')
H('Nobody warns', expr='nervous', pose='cheeks')
S('chilling in the sun', bg='field', props=[PR('sun', 330, 220, 110)], chars=[CH(VIK_TEE, 700, expr='grin', pose='hips'), CH(VIK_TEE2, 1200, expr='smile', flip=True)])
S('a cloud of dust rises', bg='field', props=[PR('dust', 1300, 740, 160, at='cloud of dust'), PR('sun', 300, 210, 100)],
  chars=[CH(VIK_TEE, 640, expr=[(None, 'smile'), ('shine of a whole', 'shock')], look=(0.3, 0))], until='So what does')
H('scariest Viking alive', expr='skeptic', pose='chin')
S('left his armor in the car', props=[PR('car', 1250, 760, 200)], chars=[CH(HARALD, 640, expr='shock', pose='cheeks')], hold=2.0)
H('go to the saga itself', zoom=True, expr='smug', pose='inspect')
S('his horse stumbles', bg='field', chars=[CH(HARALD, 960, y=800, rot=-82, expr='shock')], props=[PR('dust', 1120, 900, 120)])
S('A fall is lucky', bg='field', chars=[CH(HARALD, 760, expr='smug', pose='hips', say='"A fall is lucky for a traveller."', say_x=860, say_y=300)], until='Which is the most')
H('cover for eating dirt', zoom=True, expr='grin')
S('asks who the big man', bg='field', chars=[CH(GODWINSON, 760, pose='point', expr='skeptic', say='"Who\'s the big man in blue?"', say_x=820, say_y=270)], until='They tell him')
S('And he says, roughly', bg='field', chars=[CH(GODWINSON, 760, expr='smug', pose='chin', say='"His luck has left him."', say_x=820, say_y=270)], until='Then twenty')
C('twenty English riders', '20 ENGLISH RIDERS')
S('seven feet of English ground', props=[PR('tombstone', 960, 560, 230, text='HARALD', ty=40, tcap=40)], until='Translation')
C('seven feet', '7 FEET OF ENGLISH GROUND')
H('Translation', expr='deadpan', pose='hips')
S('English king himself', bg='field', chars=[CH(GODWINSON, 960, R=130, expr='smug', pose='hips', tag='THE RIDER = THE KING')], hold=2.0)
CARD('chooses violence', 'text', lines=['HARALD HAS', 'CHOSEN VIOLENCE'], color='#E0393E', hold=1.6)
S('charged out ahead', bg='field', chars=[CH(HARALD, 760, expr='angry', pose='shrug')], props=[PR('sword', 1060, 560, 90, rot=30)])
S('an arrow hits him', bg='field', chars=[CH(HARALD, 760, expr='shock')], props=[PR('arrow', 1650, 330, 90, at='arrow hits', move=(-700, 40), move_frames=8)], sfx='thud')
PH('The last great Viking king', 'stamford_arbo', zoom='in')
C('armor was optional', 'ARMOR: "OPTIONAL"')
H('own version of this battle', expr='talk', pose='point')
PH('Anglo-Saxon Chronicle', 'anglo_saxon_chronicle', until="not exactly bodycam")
PH('bodycam footage', 'stamford_arbo', bodycam=True, hold=1.8)
S('held the bridge', bg='field', props=[PR('bridge', 960, 820, 230)], chars=[CH(VIK_ARMOR, 960, y=430, expr='angry', pose='hips'),
                                                                          CH(ENG, 360, expr='nervous'), CH(ENG, 560, expr='shock')])
C('about forty men', '~40 MEN')
S('underneath the bridge', bg='field', props=[PR('bridge', 960, 760, 230)], chars=[CH(VIK_ARMOR, 960, y=380, expr='shock'), CH(ENG, 960, y=860, R=70, expr='smug')], hold=2.0)
S('floating barrel', bg='sea', props=[PR('barrel', 960, 720, 130, z=2)], chars=[CH(ENG, 960, y=560, R=75, expr='smug', z=1)])
S('arrive so exhausted', bg='field', props=[PR('sun', 300, 200, 100)], chars=[CH(VIK_ARMOR, 760, expr='nervous'), CH(VIK_ARMOR, 1180, expr='nervous', flip=True)])
B('had shown up with around 300', 'ships', n=60, n2=5, ship='longship', change_at='They needed 24', label=('300 SHIPS', '24 SHIPS HOME'), until="But here's the craziest")
H("here's the craziest part", zoom=True, expr='shock', pose='cheeks')
MAP('William of Normandy lands', 'north_sea', icon='longship', stops=[('Normandy', 'NORMANDY', None), ('Pevensey', '', 'lands in the south')], until='Harold Godwinson has')
C('Three days later', '3 DAYS LATER')
MAP('drag his exhausted army', 'north_sea', icon='crown', stops=[('York', 'YORK', None), ('London', 'LONDON', 'all the way back'), ('Hastings', 'HASTINGS', 'nineteen days')], until='Battle of Hastings')
C('nineteen days', '19 DAYS LATER')
PH('Battle of Hastings', 'bayeux_harold', until="So Harald's death")
CARD('end of the Viking Age', 'text', lines=['END OF THE', 'VIKING AGE'], style='silver', hold=1.8)
CARD('full of French words', 'dict', word='ENGLISH', pos='(thanks to the Normans)', defs=['beef, pork, mutton', 'justice, court, jury', 'royal, government, crown'], until='Not bad for')
S('lost to the weather', bg='field', props=[PR('sun', 960, 420, 190)], hold=2.0)
C('lost to the weather', 'WINNER: THE WEATHER')

# ============================== ATTILA ==============================
B('Attila the Hun.', 'title', num=2, name=['ATTILA', 'THE HUN'], img='leo_attila', pal=ATTILA, sfx='hit', hold=2.0)
S('written by people who hated him', bg='hall', chars=[CH(PRISCUS, 700, expr='angry'), CH(ROMAN_EMP, 1220, expr='angry', flip=True)], props=[PR('book', 960, 800, 70)])
S('a Roman diplomat named Priscus', chars=[CH(PRISCUS, 960, R=130, expr='smile', tag='PRISCUS', pose='wave')], hold=1.8)
PH('had dinner with him', 'feast_attila', until='Which is a sentence')
C('in 449', '449 AD')
H('sentence I need you to appreciate', zoom=True, expr='smug', pose='point')
PH('horse archers from the steppe', 'hun_archer', until='rode into Europe')
MAP('rode into Europe', 'europe_huns', icon='crown', stops=[('Steppe', 'THE STEPPE', None), ('Pannonia', 'EUROPE', 'into Europe')], until='paying them')
S('paying them to go away', bg='hall', chars=[CH(ROMAN_EMP, 700, expr='nervous', pose='point'), CH(ATTILA, 1220, expr='smug', flip=True)], props=[PR('coin', 960, 560, 50)])
PH('2,100 pounds of gold', 'solidus', until="He wasn't conquering")
C('2,100 pounds', '2,100 LBS OF GOLD')
C('Per year', 'PER. YEAR.', hold=1.6)
CARD('charging it a subscription', 'sub', title='HUN+ PREMIUM', price='2,100 lbs of gold / year', lines=['No Huns at your gates*', 'Billed to: The Roman Empire', 'Auto-renews annually'],
     button='CANCEL', note='*terms may change at any time', hold=3.0)
S('his brother, Bleda', chars=[CH(ATTILA, 720, tag='ATTILA', expr='talk'), CH(BLEDA, 1200, tag='BLEDA', flip=True, expr='smile', exit_at='until Bleda died')], until="one ancient writer")
S("Attila's treachery", chars=[CH(ATTILA, 960, R=150, expr='evil', pose='hips')], hold=1.6)
MAP("invaded what's now France", 'europe_huns', icon='crown', stops=[('Pannonia', 'HUN EMPIRE', None), ('Gaul', 'FRANCE', 'France'), ('Pannonia', '', 'invaded Italy'), ('Italy', 'ITALY', 'Italy')], until='He even had')
C('most feared man in Europe', 'MOST FEARED MAN IN EUROPE')
S('a herdsman noticed', bg='field', chars=[CH(HERDSMAN, 700, expr=[(None, 'neutral'), ('found a sword', 'shock')])], props=[PR('sword', 1200, 760, 110, rot=180, at='found a sword')])
S('sword of the war god', props=[PR('sword', 1200, 520, 160, kw={'glow': True})], chars=[CH(ATTILA, 700, expr='smug', pose='point')], until='And yet')
S('silver plates', bg='hall', until='Final boss energy', props=[PR('plate', 560, 760, 120, kw={'c': '#C9CED3'}), PR('cup', 760, 700, 70, kw={'c': '#E8B83A'}),
                                                                PR('cup', 380, 700, 70, kw={'c': '#C9CED3'}),
                                                                PR('plate', 1360, 760, 120, at='wooden plate', kw={'c': '#9A6B3F'}), PR('cup', 1560, 700, 70, at='wooden cup', kw={'c': '#9A6B3F'})],
  chars=[CH(ATTILA, 1360, y=330, R=90, expr='deadpan', at='Attila ate plain')])
CARD('starter-gear', 'inventory', title='ATTILA — EQUIPMENT', hold=2.6, items=[
    dict(name='WOODEN PLATE', rarity='COMMON'), dict(name='WOODEN CUP', rarity='COMMON'), dict(name='SWORD OF THE WAR GOD', rarity='LEGENDARY')])
C('died of a nosebleed', 'DIED OF A... NOSEBLEED')
H("that's how Attila died", expr='deadpan', pose='hips')
C('In 453', '453 AD')
S('a young woman named Ildico', bg='hall', chars=[CH(ATTILA, 720, expr='smile'), CH(ILDICO, 1200, flip=True, expr='smile', tag='ILDICO')], props=[PR('icon', 960, 300, 55, kw={'kind': 'heart'})])
CARD('regular Tuesday', 'calendar', text='TUESDAY', sub='another wedding', hold=1.8)
PH('partied hard', 'feast_attila', zoom='out', until='went to bed')
S('went to bed drunk', bg='night', props=[PR('bed', 960, 780, 200)], chars=[CH(ATTILA, 900, y=700, R=70, rot=-90, expr='sleep')], until='During the night')
PH('his nose started bleeding', 'attila_death', until='The next morning')
S('broke down the door', bg='hall', props=[PR('door', 960, 600, 200, kw={'broken': True})], chars=[CH(HUN, 560, expr='shock'), CH(HUN, 1360, expr='shock', flip=True)])
S('crying beneath her veil', bg='hall', chars=[CH(ILDICO, 960, R=140, expr='cry')])
S('claimed she killed him', bg='hall', chars=[CH(ILDICO, 760, expr='smug')], props=[PR('icon', 1150, 420, 70, kw={'kind': 'question'})], until='So that')
H('Embarrassing', zoom=True, expr='grimace')
H('But the funeral', expr='smug', pose='point')
S('the historian Jordanes', chars=[CH(SCRIBE, 960, R=130, tag='JORDANES', expr='talk')], props=[PR('book', 1250, 640, 70)], hold=1.8)
S('cut off their hair', bg='night', chars=[CH(HUN_BALD, 560, expr='sad'), CH(HUN_BALD, 960, expr='cry'), CH(HUN_BALD, 1360, expr='sad', flip=True)])
CARD('mourned not with tears', 'quote', text='Mourned not with tears, but with the blood of men.', who='Jordanes', quote_at='not with tears', until='Then they sealed')
S('three coffins', until='They buried him', props=[PR('coffin', 560, 560, 170, at='one of gold', kw={'c': '#E8B83A'}),
                                                  PR('coffin', 960, 560, 170, at='one of silver', kw={'c': '#C9CED3'}),
                                                  PR('coffin', 1360, 560, 170, at='one of iron', kw={'c': '#5E6469'})])
S('buried him at night', bg='night', props=[PR('gold_pile', 1150, 820, 120), PR('shovel', 760, 700, 150, rot=20), PR('sword', 1450, 760, 90, rot=80)], until='they killed the men')
S('killed the men who dug', bg='night', props=[PR('shovel', 900, 700, 140, rot=-20), PR('icon', 1100, 460, 80, kw={'kind': 'skull'})], hold=1.8)
MAP("nobody has found Attila's", 'europe_huns', zoom=1.8, focus='Pannonia', pins=[('Pannonia', "ATTILA'S TOMB: ???", None)], until='Within about a year')
C('fifteen hundred years', '1,500+ YEARS: STILL MISSING')
CARD('least epic death', 'versus', left='DEATH: NOSEBLEED', right='FUNERAL: THREE COFFINS', items=[dict(at='least epic death'), dict(at='most epic funeral')], until='He walked')
CARD('heavy metal album cover', 'album', band='ATTILA', title='THREE COFFINS', hold=2.6)

# ============================== CRASSUS ==============================
B('Marcus Licinius Crassus.', 'title', num=3, name=['MARCUS', 'LICINIUS', 'CRASSUS'], img='crassus_bust', pal=CRASSUS, sfx='hit', hold=2.2)
S('uncle at Thanksgiving', bg='hall', chars=[CH(UNCLE, 960, R=125, expr='grin', pose='point', say='"Back in my day..."', say_x=1060, say_y=330)], hold=2.0)
CARD('crassus means', 'dict', word='crassus', pos='(Latin, adjective)', defs=['1. fat', '2. thick'], items=[dict(at='fat'), dict(at='thick')], until='Which is a wild')
S('richest man in Rome', chars=[CH(CRASSUS, 760, expr='smug', pose='hips', tag='CRASSUS')], props=[PR('gold_pile', 1250, 720, 170)], until='How rich')
H('How rich', zoom=True, expr='skeptic')
S('biographer Plutarch', chars=[CH(SCRIBE, 960, R=130, tag='PLUTARCH', expr='talk')], hold=1.6)
PH('catching fire or collapsing', 'fire_rome', until='So he bought')
C('more than 500', '500+ BUILDERS & ARCHITECTS')
S('house went up in flames', bg='field', until="That's how he ended up",
  props=[PR('house', 600, 680, 150, kw={'burning': True}), PR('house', 960, 660, 160, kw={'burning': True}, at='the houses next'), PR('house', 1320, 680, 150, kw={'burning': True}, at='houses next to it')],
  chars=[CH(CRASSUS, 1640, R=95, expr='smug', flip=True, say='"I\'ll take it. Cheap."', say_x=1180, say_y=230, say_at='for almost nothing')])
C('while it was on fire', 'BUYING YOUR HOUSE WHILE IT BURNS')
PH('Spartacus, the gladiator', 'spartacus_statue', until='Crassus is the general')
S('the general who crushed it', chars=[CH(LEGIONARY, 560, expr='angry'), CH(CRASSUS, 960, R=125, expr='evil', tag='CRASSUS'), CH(LEGIONARY, 1360, expr='angry', flip=True)])
C('six thousand', '~6,000 REBELS')
H("who we're dealing with", expr='grimace')
S('He had money', chars=[CH(CRASSUS, 760, expr=[(None, 'smug'), ("didn't have was glory", 'sad')])], props=[PR('gold_pile', 1250, 720, 170)], until='His two political')
S('Pompey and Julius Caesar', until='So at around sixty', chars=[CH(POMPEY, 560, tag='POMPEY', expr='smug'), CH(CAESAR, 960, tag='JULIUS CAESAR', expr='smug', at='Julius Caesar'),
                                                                  CH(CRASSUS, 1360, tag='CRASSUS', expr=[(None, 'neutral'), ('bank account', 'sad')], flip=True, at='could not stand')])
C('sixty years old', 'AGE ~60: MIDLIFE CRISIS')
S('sports chariot', props=[PR('chariot', 960, 650, 190)], chars=[CH(CRASSUS, 840, y=360, R=80, expr='grin')], hold=1.8)
MAP('invading the Parthian Empire', 'rome_parthia', highlight=('Iran', 'Iraq'), icon='crown', stops=[('Rome', 'ROME', None), ('Carrhae', '', 'superpower'), ('Ctesiphon', 'PARTHIA', 'Iran and Iraq')], until='It did not go')
H('It did not go well', zoom=True, expr='grimace', pose='cheeks')
C('In 53 BC', '53 BC')
MAP('a town called Carrhae', 'rome_parthia', zoom=2.0, focus='Carrhae', pins=[('Carrhae', 'CARRHAE', None)], hold=1.8)
PH('Parthian horse archers', 'parthian_archer', until='Picture this')
S('Roman legionary', bg='field', until="That's the plan", chars=[CH(LEGIONARY, 560, expr='nervous'), CH(LEGIONARY, 960, expr='nervous'), CH(LEGIONARY, 1360, expr='nervous')],
  props=[PR('shield', 600, 700, 90, kw={'c': '#B03A2E', 'c2': '#E8C27A'}), PR('shield', 1000, 700, 90, kw={'c': '#B03A2E', 'c2': '#E8C27A'}),
         PR('shield', 1400, 700, 90, kw={'c': '#B03A2E', 'c2': '#E8C27A'}), PR('arrow', 1700, 300, 60, rot=160, at='run out of arrows', move=(-500, 220), move_frames=10)])
H("That's the entire plan", zoom=True, expr='deadpan')
CARD('camels loaded with fresh arrows', 'ammo', until='The Parthians would')
S('fire backward', bg='field', chars=[CH(PARTHIAN, 1150, expr='smug', look=(-0.3, 0))], props=[PR('arrow', 900, 420, 80, rot=180, at='fire backward', move=(-700, 0), move_frames=10)])
CARD('Parthian shot', 'dict', word='Parthian shot', pos='(noun, 53 BC)', defs=['→ "parting shot"'], items=[dict(at='parting shot')], until="Crassus's son")
S("Crassus's son led", bg='field', chars=[CH(LEGIONARY, 960, R=125, tag="CRASSUS'S SON", pose='point', expr='angry')], hold=1.8)
H("son's head on a spear", expr='grimace', pose='cheeks')
S('lured into peace talks', bg='field', chars=[CH(CRASSUS, 720, expr=[(None, 'nervous'), ('he was killed', 'dead')]), CH(PARTHIAN, 1200, flip=True, expr='smug')], until='Plutarch says')
C('twenty thousand Romans', '20,000 ROMANS DEAD')
C('ten thousand were captured', '10,000 CAPTURED')
PH('sacred eagle standards', 'aquila', until="And that's not even")
C('thirty years of diplomacy', '30+ YEARS TO GET THEM BACK')
H("that's not even the wild part", zoom=True, expr='smug', pose='point')
S('royal wedding feast', bg='hall', chars=[CH(PARTHIAN_KING, 960, R=130, expr='smug', tag='PARTHIAN KING')], until='watching a performance')
PH('Greek tragedy called the Bacchae', 'greek_theater', until='The next scene')
PH('The next scene features', 'theater_masks', until='So the lead actor')
S('uses it as the prop', props=[PR('stage', 960, 560, 230)], chars=[CH(ACTOR, 960, y=520, R=95, expr='talk', pose='wave')], until='Then the Parthian')
S('snatches the head', props=[PR('stage', 960, 560, 230)], chars=[CH(PARTHIAN, 960, y=520, R=95, expr='angry', pose='point', say='"I\'m saying the line!"', say_x=1060, say_y=200)], until='The king loved')
S('gave the actor a fortune', bg='hall', chars=[CH(PARTHIAN_KING, 700, expr='grin'), CH(ACTOR, 1220, expr='shock', flip=True)], props=[PR('gold_pile', 960, 800, 120)])
C('ended up as a stage prop', "ROME'S RICHEST MAN: STAGE PROP")
S('fake Roman victory parade', bg='field', chars=[CH(PARTHIAN, 560, expr='grin'), CH(CRASSUS_FAKE, 960, tag='"CRASSUS"', expr='deadpan'), CH(PARTHIAN, 1360, expr='grin', flip=True)], until='Oh, and another')
C('250 years later', '250+ YEARS LATER')
S('poured molten gold', props=[PR('cup', 1000, 420, 120, rot=120, kw={'c': '#E8B83A'}), PR('coin', 880, 700, 50), PR('coin', 940, 800, 40)], hold=1.8)
C('some say', '"SOME SAY..."')
H('moral writes itself', expr='talk', pose='hips')
S('chasing gold', bg='field', chars=[CH(CRASSUS, 760, pose='walk', expr='grin')], props=[PR('coin', 1250, 600, 60)], until='more than he could swallow')
H('more than he could swallow', zoom=True, expr='grin')

# ============================== ARRICHION ==============================
B('Arrichion of Phigalia.', 'title', num=4, name=['ARRICHION', 'OF PHIGALIA'], img='kouros_phigalia', pal=ARRICHION, sfx='hit', hold=2.0)
H('without armor felt hardcore', expr='smug', pose='hips')
S('He was an athlete', bg='arena', chars=[CH(ARRICHION, 960, R=130, expr='smile', pose='hips', tag='ARRICHION')], until='And not in')
PH('He competed in pankration', 'pankration_vase', until='It had been part')
PH('part of the Games', 'olympia_stadium')
C('since 648 BC', 'SINCE 648 BC')
S('superstars of their day', bg='arena', chars=[CH(ARRICHION_WREATH, 960, R=130, expr='smug', pose='wave')], hold=2.0)
CARD('think MMA', 'text', lines=['PANKRATION', '= MMA WITH NO LAWYERS'], hold=2.6)
CARD("Here's what was illegal", 'list', title='ILLEGAL', title_color='#E0393E', mark='x', until="Here's what was legal", items=[
    dict(text='Biting', at='biting'), dict(text='Gouging out eyes', at='gouging')])
CARD("Here's what was legal", 'list', title='LEGAL', title_color='#7FD16A', mark='check', cap=30, until='One famous champion', items=[
    dict(text='Punching', at='punching'), dict(text='Kicking', at='kicking, choking'), dict(text='Choking', at='choking'),
    dict(text='Joint locks', at='joint locks'), dict(text='Kicking a guy in the stomach', at='in the stomach'),
    dict(text="Snapping your opponent's fingers", at='bending back')])
H('One famous champion', expr='grimace', pose='cheeks')
MAP('in Sparta', 'greece', pins=[('Sparta', 'SPARTA', None)], hold=1.6)
C("didn't even bother banning", 'SPARTA: NO RULES. AT ALL.')
CARD('No weight classes', 'list', title='ALSO...', mark='x', until='You won when', items=[
    dict(text='No weight classes', at='weight classes'), dict(text='No rounds', at='No rounds'), dict(text='No time limit', at='time limit')])
PH('A wreath of olive leaves', 'olive_wreath', until='In my completely')
H('completely unqualified opinion', zoom=True, expr='smug', pose='point')
S('He was the guy', bg='arena', chars=[CH(ARRICHION_WREATH, 960, R=130, expr='smug', pose='hips')], hold=1.6)
C('in 572 BC', '572 BC: CHAMPION', hold=1.6)
C('Then again in 568', '568 BC: CHAMPION AGAIN', hold=1.6)
C('in 564 BC', '564 BC: GOING FOR #3', hold=2.0)
S('makes it to the final', bg='arena', chars=[CH(ARRICHION, 700, expr='angry', tag='ARRICHION'), CH(OPPONENT, 1220, expr='angry', flip=True, tag='OPPONENT')], until='And in the final')
H('it all goes wrong', zoom=True, expr='shock')
S('wraps his legs around', bg='arena', chars=[CH(OPPONENT, 900, R=110, rot=-25, expr='angry', z=0), CH(ARRICHION, 1020, R=115, expr=[(None, 'shock'), ('fading', 'sad')], z=1)], until='And this is where')
S('a man named Eryxias', bg='arena', chars=[CH(ERYXIAS, 960, R=125, expr='angry', pose='point', tag='ERYXIAS (COACH)')], until='Quote')
S('What a noble epitaph', bg='arena', chars=[CH(ERYXIAS, 700, R=115, expr='talk', pose='point', say='"What a noble epitaph..."', say_x=800, say_y=270)], until='An epitaph')
S('carve on your gravestone', props=[PR('tombstone', 960, 560, 230, text='UNDEFEATED', ty=30, tcap=30)], until='So his coach')
S('your tombstone is going to look amazing', bg='arena', chars=[CH(ERYXIAS, 640, expr='grin', pose='wave', say='"Your tombstone will look AMAZING!"', say_x=700, say_y=270)],
  props=[PR('tombstone', 1350, 650, 160, text='UNDEFEATED', ty=20, tcap=24)], until='Respectfully')
H('Respectfully', zoom=True, expr='shock', pose='cheeks')
H('Your fighter is being', expr='skeptic', pose='shrug')
H("That's not coaching", zoom=True, expr='deadpan')
S("wrenched his opponent's foot", bg='arena', chars=[CH(OPPONENT, 960, R=125, expr='cry')], props=[PR('icon', 1250, 420, 70, kw={'kind': 'bang'})], until='The sources disagree')
C('a toe or an ankle', 'TOE? ANKLE? (SOURCES DISAGREE)')
H('died from the chokehold', expr='sad')
S('judges with an awkward', bg='arena', chars=[CH(JUDGE, 760, expr='nervous'), CH(JUDGE, 1160, expr='nervous', flip=True)], until='The winner was dead')
S('The winner was dead', bg='arena', chars=[CH(ARRICHION, 640, y=840, R=85, rot=-90, expr='dead', tag='WINNER'), CH(OPPONENT, 1300, expr='cry', tag='LOSER', flip=True)], until='History')
C("loser's name", 'LOSER: [NAME NOT FOUND]')
S('named Pausanias', chars=[CH(PAUSANIAS, 760, expr='smug', tag='PAUSANIAS', say='"...whoever he was."', say_x=880, say_y=280)], until='So the judges')
S('crowned the corpse', bg='arena', chars=[CH(ARRICHION_WREATH, 960, y=840, R=95, rot=-90, expr='dead')], until='Pausanias says the win')
C('crowned the corpse', 'THEY CROWNED THE CORPSE')
C('third time', '3x OLYMPIC CHAMPION')
C('seven hundred years', '~700 YEARS LATER')
MAP("visited Arrichion's hometown", 'greece', zoom=1.6, focus='Phigalia', pins=[('Phigalia', 'PHIGALIA', None), ('Olympia', 'OLYMPIA', 'museum at Olympia')], until='A statue many')
PH('A statue many believe', 'kouros_phigalia', pip=True, until='As far as we know')
C('win an Olympic final after dying', 'WON AN OLYMPIC FINAL AFTER DYING')
H('impossible to top', expr='smug', pose='hips')
B('with an entire fleet', 'ships', n=13, ship='turtle_ship', hold=2.2)

# ============================== MID-ROLL ==============================
H('I owe you a confession', zoom=True, expr='nervous', pose='chin')
C('ten deaths, not five', '10 DEATHS → 5')
CARD('split it in two', 'split', hold=1.8)
S('a Viking who was killed', chars=[CH(GHOST_VIKING, 960, R=125, expr='shock', alpha_dim=True)], props=[PR('icon', 1250, 360, 70, kw={'kind': 'question'})], until='and one of the greatest')
PH('greatest generals in history', 'pyrrhus', until='by an old woman')
S('an old woman with a roof tile', props=[PR('tile', 1200, 420, 90, rot=-30)], chars=[CH(OLD_WOMAN, 840, expr='evil', pose='wave')], until='Some of them sound')
H("They're not", zoom=True, expr='smug')
CARD('drop a comment', 'comment', text='part two', until='And if we get')
CARD('25,000 likes', 'likes', target=25000, until='Alright')
H('Final entry. Well', expr='smile', pose='wave')

# ============================== YI SUN-SIN ==============================
B('Yi Sun-sin.', 'title', num=5, name=['YI', 'SUN-SIN'], img='yi_statue', pal=YI, sfx='hit', hold=2.0)
H('Quick question', expr='skeptic', pose='chin')
PH('Horatio Nelson', 'nelson', until='If you said Captain')
S('Captain Hook', bg='sea', chars=[CH(HOOK, 960, R=125, expr='smug', pose='hips')], until='please leave')
H('please leave', zoom=True, expr='deadpan', pose='point')
MAP('outside Korea', 'korea', highlight=('South Korea', 'North Korea'), hold=2.2)
H('most epic death in recorded', zoom=True, expr='talk')
C('In 1592', '1592')
MAP('Japan invades Korea', 'korea', icon='jp_ship', stops=[('Japan', 'JAPAN', None), ('Busan', 'BUSAN', 'invades Korea'), ('Seoul', 'SEOUL', 'Seoul, falls')], until='But at sea')
C('150,000 soldiers', '150,000+ SOLDIERS')
C('three weeks', 'SEOUL FALLS IN ~3 WEEKS')
S('one Korean admiral starts', bg='sea', chars=[CH(YI, 960, R=130, expr='smug', pose='hips', tag='YI SUN-SIN')], until='He brings out')
PH('called turtle ships', 'turtle_ship', until='covered decks')
S('covered decks studded', bg='sea', props=[PR('turtle_ship', 960, 600, 300)], labels=[('IRON SPIKES', 900, 330, 'iron spikes'), ('CANNONS', 700, 780, 'cannons'), ('DRAGON HEAD', 1450, 420, "dragon's head")], until='At Hansan')
MAP('At Hansan Island', 'korea', zoom=1.8, focus='Hansan', pins=[('Hansan', 'HANSAN ISLAND', None)], until='wrapped his ships')
CARD('crane wing formation', 'formation', until='His wins cut')
MAP("cut Japan's supply lines", 'korea', stops=[('Japan', 'JAPAN', None), ('Busan', 'SUPPLY LINES', 'supply lines')], until='By most counts')
C('twenty-three naval battles', '~23 NAVAL BATTLES')
C('never losing a single one', 'LOSSES: 0')
S('his own government arrested', chars=[CH(YI, 960, R=125, expr='sad')], props=[PR('jail', 960, 560, 330, z=5)], until='Earlier in his career')
C('Again', 'AGAIN.', hold=1.4)
C('In 1597', '1597')
S('an enemy tip he suspected', chars=[CH(YI, 760, expr='skeptic', pose='chin')], props=[PR('icon', 1150, 420, 70, kw={'kind': 'question'})], until='So he was hauled')
S('demoted to a common foot soldier', bg='field', chars=[CH(YI_SOLDIER, 960, R=125, expr='sad', tag='DEMOTED (AGAIN)')], until='While he was')
H('his mother died', expr='sad')
S('straight into a Japanese ambush', bg='sea', props=[PR('jp_ship', 500, 580, 110), PR('jp_ship', 850, 640, 120), PR('jp_ship', 1250, 600, 110), PR('jp_ship', 1550, 650, 100)], hold=2.0)
B('more than 160 warships', 'ships', n=160, n2=12, ship='turtle_ship', change_at='about a dozen escaped', label=('160 WARSHIPS', '12 LEFT'), until='So the king')
S('gave Yi his old job back', bg='hall', chars=[CH(JOSEON_KING, 700, expr='nervous', tag='THE KING'), CH(YI, 1220, flip=True, expr='smug')], until='And things looked')
H('giving up on the navy', expr='shock', pose='cheeks')
CARD('Your servant still has', 'quote', text='Your servant still has twelve ships.', who='Yi Sun-sin, 1597', quote_at='Your servant', until='Twelve. Plus')
B('Thirteen ships, against', 'ships', n=13, ship='turtle_ship', label=('13 SHIPS',), hold=2.2)
MAP('Battle of Myeongnyang', 'korea', zoom=2.0, focus='Myeongnyang', pins=[('Myeongnyang', 'MYEONGNYANG', None)], hold=1.8)
CARD('133 Japanese warships', 'versus', left='YI: 13 SHIPS', right='JAPAN: 133 WARSHIPS (+200 SUPPORT)', items=[dict(at='133 Japanese'), dict(at='133 Japanese')], until='Before the battle')
CARD('Those who seek death', 'quote', text='Those who seek death shall live, and those who seek life shall die.', who='Yi Sun-sin', quote_at='Those who seek', until='He picked his')
PH('a narrow strait', 'myeongnyang', until="And here's the part")
H("here's the part that gets me", zoom=True, expr='talk', pose='point')
S('captains hung back', bg='sea', props=[PR('turtle_ship', 1450, 640, 90), PR('turtle_ship', 1650, 700, 80)], chars=[CH(YI_SOLDIER, 1500, y=430, R=60, expr='nervous')], until="So for a while")
S("Yi's flagship held off", bg='sea', props=[PR('turtle_ship', 500, 640, 150)] + [PR('jp_ship', 1000 + k * 170, 560 + (k % 2) * 90, 90) for k in range(5)], until='Then the tide')
C('the tide turned', 'THE TIDE TURNED (LITERALLY)')
S('crashing into each other', bg='sea', props=[PR('jp_ship', 820, 600, 130, rot=-20), PR('jp_ship', 1080, 620, 130, rot=25), PR('turtle_ship', 400, 700, 120)], until='When it was over')
C('31 Japanese ships', '31 JAPANESE SHIPS WRECKED')
C("Yi didn't lose a single", 'KOREAN SHIPS LOST: 0')
H('killed his youngest son', expr='sad')
S('In his war diary', chars=[CH(YI, 760, expr='cry')], props=[PR('book', 1200, 600, 90)], until='And then he kept')
C('brings us to 1598', '1598')
PH("Japan's ruler has died", 'hideyoshi', until='Plenty of')
H("Yi didn't", zoom=True, expr='angry', pose='hips')
C('December 16th', 'DECEMBER 16TH, 2 AM')
MAP('the Noryang Strait', 'korea', zoom=1.8, focus='Noryang', pins=[('Noryang', 'NORYANG STRAIT', None)], hold=1.8)
S('raged until daylight', bg='night', props=[PR('jp_ship', 700, 620, 120), PR('turtle_ship', 1250, 650, 120), PR('flames', 760, 560, 70)], hold=2.0)
H('a bullet struck Yi', zoom=True, expr='shock', pose='cheeks')
H('He knew right away', expr='sad')
CARD('The battle is at its height', 'quote', text='The battle is at its height. Do not announce my death.', who='Yi Sun-sin, 1598', quote_at='The battle is at its', until='He was fifty-three')
C('fifty-three years old', 'AGE 53')
S('picked up the war drum', bg='sea', props=[PR('drum', 1150, 680, 130, kw={'hit': False})], chars=[CH(NEPHEW, 760, expr='angry', pose='wave', tag='NEPHEW')], drum=True, until='The fleet fought')
C('hundreds of Japanese ships', 'HUNDREDS OF SHIPS DESTROYED')
C('seven-year war', 'END OF A 7-YEAR WAR')
S('the Chinese admiral Chen Lin', bg='sea', chars=[CH(CHEN_LIN, 960, R=130, expr='smile', tag='CHEN LIN')], until='When they told him')
S('fell to the deck three times', bg='sea', chars=[CH(CHEN_LIN, 960, R=130, expr='cry')], until='Think about that')
H('Think about that', zoom=True, expr='talk', pose='chin')
CARD('Arrichion won one fight', 'versus', left='ARRICHION: WON 1 FIGHT AFTER DYING', right='YI SUN-SIN: WON A WHOLE WAR', items=[dict(at='Arrichion won'), dict(at='Yi Sun-sin won')], until='Korea gave him')
C('Chungmugong', '"LORD OF LOYALTY AND WARFARE"')
PH('100-won coin', 'hundred_won', until='and his statue')
PH('his statue stands', 'seoul_gwanghwamun', until='He earned')
H('He earned all of it', expr='smile', pose='hips')

# ============================== OUTRO ==============================
CARD('Five deaths', 'list', title="PART ONE: THE DEATHS", cap=30, until='If you already knew', items=[
    dict(text='A Viking king who skipped armor day', at='A Viking king'), dict(text='A warlord beaten by a nosebleed', at='A warlord'),
    dict(text="Rome's richest man, now a theater prop", at="Rome's richest"), dict(text='An Olympic champion crowned as a corpse', at='An Olympic champion'),
    dict(text='An admiral who won after he was gone', at='And an admiral')], mark='check')
H('If you already knew', expr='smile', pose='point')
H('good news', zoom=True, expr='grin')
CARD('life lessons', 'list', title='LIFE LESSONS', title_color='#F2C94C', mark='check', cap=30, until='Sources', items=[
    dict(text='Invading England? Wear the armor.', at='wear the armor'), dict(text='Pace yourself at your own wedding.', at='pace yourself'),
    dict(text='Richest guy in Rome? Just buy a boat.', at='Just buy a boat'), dict(text='Coach talks tombstones? New coach.', at='find a new coach'),
    dict(text='Twelve ships is enough.', at='prove them wrong')])
S('Sources: a pile', bg='hall', chars=[CH(SCRIBE, 760, expr='smug')], props=[PR('book', 1150, 760, 70), PR('book', 1150, 640, 70, rot=8), PR('book', 1150, 520, 70, rot=-6)], until='Ever.')
H('Ever.', zoom=True, expr='deadpan')
B("if it's two in the morning", 'end', hold=12.0, channel='')


# ---------- gag SFX (BLUEPRINT 7: sound marks moments, not every edit) ----------
# beat trigger -> [(kind, sub-event key or None, delay in frames, gain dB vs. the voice)]
SFX = {
    'final boss': [('hit', None, 0, -4)],
    'thrown in prison': [('thud', 'p1', 0, -6)],
    'grain of salt': [('pop', None, 0, -8)],
    'chooses violence': [('hit', None, 0, -7)],
    'an arrow hits him': [('thud', 'p0', 8, -4)],
    'seven feet of English ground': [('thud', None, 0, -7)],
    'broke down the door': [('thud', None, 0, -4)],
    'three coffins': [('pop', 'p0', 0, -8), ('pop', 'p1', 0, -8), ('pop', 'p2', 0, -8)],
    'killed the men who dug': [('thud', None, 0, -6)],
    "wrenched his opponent's foot": [('thud', None, 0, -5)],
}


# ---------- real photo backdrops behind character scenes (falls back to the cartoon set if the image is missing) ----------
REAL_BG = {
    "Byzantine emperor's elite": 'hagia_sophia', 'blind an emperor': 'hagia_sophia', 'marries a princess': 'hagia_sophia',
    'weather is gorgeous': 'stamford_river', 'very merry': 'stamford_river', 'chilling in the sun': 'stamford_river',
    'a cloud of dust rises': 'stamford_river', 'held the bridge': 'stamford_river', 'underneath the bridge': 'stamford_river',
    'a herdsman noticed': 'puszta',
    'Roman legionary': 'carrhae', 'fire backward': 'carrhae', "Crassus's son led": 'carrhae', 'lured into peace talks': 'carrhae',
    'He was an athlete': 'olympia_stadium', 'He was the guy': 'olympia_stadium', 'makes it to the final': 'olympia_stadium',
    'wraps his legs around': 'olympia_stadium', "wrenched his opponent's foot": 'olympia_stadium',
    'judges with an awkward': 'olympia_stadium', 'The winner was dead': 'olympia_stadium', 'crowned the corpse': 'olympia_stadium',
    'gave Yi his old job back': 'gyeongbokgung',
    'captains hung back': 'myeongnyang', "Yi's flagship held off": 'myeongnyang', 'crashing into each other': 'myeongnyang',
}
for _b in BEATS:
    if _b['kind'] == 'scene' and _b['trigger'] in REAL_BG:
        _b['bg'] = f"img:{REAL_BG[_b['trigger']]}|{_b.get('bg', 'black')}"
