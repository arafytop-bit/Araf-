"""Cast palettes for "Most Epic Deaths" (round-head style, historical costumes)."""
from engine.roundhead import DETECTIVE as HOST

LEGS_BARE = dict(pants='#F8F8F5', shoes='#8A6A45')
HARALD = dict(hat='viking', hat_color='#9AA3AD', hair='viking', hair_color='#C9A25A', facial='beard', top='tunic',
              top_color='#3E6BB5', belt='#4A3326', trim='#C9A050', pants='#5A4A3A', shoes='#4A3329')
HARALD_CROWN = dict(HARALD, hat='crown', hat_color='#E8B83A', cape='#8E2B2B')
HARALD_YOUNG = dict(HARALD, facial=None)
OLAF = dict(hat='viking', hat_color='#8E969F', hair='viking', hair_color='#8A5A2E', facial='beard', top='tunic',
            top_color='#9E3B32', belt='#3A2A20', pants='#4A3E33', shoes='#3A2A20')
VIK_TEE = dict(hat='viking', hat_color='#9AA3AD', hair='viking', hair_color='#B5893E', facial='beard', top='tshirt',
               top_color='#EDEDED', pants='#5A4A3A', shoes='#4A3329')
VIK_TEE2 = dict(VIK_TEE, hair_color='#6B4A35', top_color='#D9E6F2')
VIK_ARMOR = dict(hat='viking', hat_color='#8E969F', hair='viking', hair_color='#7A5432', facial='beard', top='armor',
                 top_color='#8E969F', stud='#5E6469', belt='#3A2A20', pants='#4A3E33', shoes='#3A2A20')
GODWINSON = dict(hat='crown', hat_color='#E8B83A', facial='mustache', hair='short', hair_color='#8A5A2E', top='tunic',
                 top_color='#9E3B32', trim='#C9A050', cape='#2E4A8E', pants='#3A2E25', shoes='#3A2A20')
EDWARD = dict(hat='crown', hat_color='#E8B83A', facial='beard', hair_color='#E8E8E8', top='robe', top_color='#5A3E8E',
              cape='#C9A050')
WILLIAM = dict(hat='viking', hat_color='#7C8590', top='armor', top_color='#8E969F', stud='#5E6469', cape='#2E6B3A',
               pants='#3A2E25', shoes='#3A2A20')
ENG = dict(hat='viking', hat_color='#7C8590', top='armor', top_color='#9AA3AD', stud='#6E747A', belt='#5A1E1E',
           pants='#3A2E25', shoes='#3A2A20')
SCRIBE = dict(hat='hood', hat_color='#5A4636', top='robe', top_color='#5A4636', shirt='#EFEAE0')
SNORRI = dict(hat='hood', hat_color='#6B4F3A', facial='beard', hair_color='#9A9A9A', top='robe', top_color='#6B4F3A')
BYZ = dict(hat='crown', hat_color='#E8B83A', facial='beard', hair_color='#3A2A20', top='robe', top_color='#6B2E7A',
           cape='#C9A050')
VARANGIAN = dict(hat='viking', hat_color='#C9A04A', hair='viking', hair_color='#C9A25A', facial='beard', top='armor',
                 top_color='#9E2B2B', stud='#E8C27A', belt='#3A2A20', pants='#3A2E25', shoes='#3A2A20')
PRINCESS = dict(hat='crown', hat_color='#E8B83A', hair='long', hair_color='#7A5432', top='robe', top_color='#B23A32')
ATTILA = dict(hat='fur', hat_color='#7A2E2A', facial='mustache', hair_color='#1E1612', top='tunic', top_color='#6B4A35',
              trim='#C9A050', belt='#3A2A20', pants='#3A2E25', shoes='#3A2A20')
BLEDA = dict(ATTILA, hat_color='#2E5A3A', top_color='#4A5A35')
HUN = dict(hat='fur', hat_color='#5A4632', top='tunic', top_color='#7A5A3C', belt='#3A2A20', pants='#3A2E25', shoes='#3A2A20')
HUN_BALD = dict(top='tunic', top_color='#7A5A3C', belt='#3A2A20', pants='#3A2E25', shoes='#3A2A20')
PRISCUS = dict(hair='short', hair_color='#6B5A4A', top='toga', top_color='#F1EDE4', stripe='#2E4A8E', **LEGS_BARE)
ROMAN_EMP = dict(hat='laurel', top='toga', top_color='#F1EDE4', stripe='#6B2E7A', cape='#6B2E7A', **LEGS_BARE)
ILDICO = dict(hair='long', hair_color='#3A2A20', hat='veil', top='robe', top_color='#F2EDE4')
HERDSMAN = dict(hair='short', hair_color='#5A4632', top='tunic', top_color='#8A7A5A', belt='#3A2A20', pants='#5A4A3A',
                shoes='#3A2A20')
CRASSUS = dict(hair='balding', hair_color='#8A8A8A', top='toga', top_color='#F1EDE4', stripe='#6B2E7A', **LEGS_BARE)
CRASSUS_FAKE = dict(hair='balding', hair_color='#8A8A8A', top='robe', top_color='#D96A9A', shirt='#F2EDE4')
SPARTACUS = dict(hair='short', hair_color='#3A2A20', facial='beard', top='armor', top_color='#B07A3A', stud='#E8C27A',
                 **LEGS_BARE)
POMPEY = dict(hair='short', hair_color='#6B4A35', top='toga', top_color='#F1EDE4', stripe='#B23A32', **LEGS_BARE)
CAESAR = dict(hat='laurel', top='toga', top_color='#F1EDE4', stripe='#6B2E7A', **LEGS_BARE)
LEGIONARY = dict(hat='roman', hat_color='#C9A04A', top='armor', top_color='#B03A2E', stud='#E8C27A', **LEGS_BARE)
PARTHIAN = dict(hat='fur', hat_color='#C9A04A', facial='beard', hair_color='#1E1612', top='tunic', top_color='#4A6B8E',
                trim='#C9A050', pants='#7A5A3C', shoes='#3A2A20')
PARTHIAN_KING = dict(hat='crown', hat_color='#E8B83A', facial='beard', hair_color='#1E1612', top='robe',
                     top_color='#2E6B5A', cape='#C9A050')
ACTOR = dict(hair='short', hair_color='#3A2A20', top='robe', top_color='#7A3B6B')
UNCLE = dict(hair='balding', hair_color='#6B5A4A', top='tshirt', top_color='#B0563E', pants='#3A3F4B', shoes='#3A3A3A')
ARRICHION = dict(hair='short', hair_color='#3A2A20', top='athlete', top_color='#D9C9A3', pants='#F8F8F5', shoes='#F8F8F5')
ARRICHION_WREATH = dict(ARRICHION, hat='laurel')
OPPONENT = dict(hair='short', hair_color='#8A5A2E', top='athlete', top_color='#B5A07A', pants='#F8F8F5', shoes='#F8F8F5')
ERYXIAS = dict(hair='balding', hair_color='#9A9A9A', facial='beard', top='robe', top_color='#3E6B8E')
JUDGE = dict(hair='short', hair_color='#8A8A8A', facial='beard', top='robe', top_color='#7A3B2E')
PAUSANIAS = dict(hat='hood', hat_color='#5A6B4A', facial='beard', hair_color='#5A4A3A', top='robe', top_color='#5A6B4A')
YI = dict(hat='admiral', hat_color='#3A3F47', facial='goatee', hair_color='#1E1612', top='armor', top_color='#2F3A5A',
          stud='#C9A050', belt='#8E2B2B', cape='#8E2B2B', pants='#2A2A33', shoes='#2A2420')
YI_SOLDIER = dict(hair='short', hair_color='#1E1612', facial='goatee', top='tunic', top_color='#8A8A7A', belt='#3A2A20',
                  pants='#5A5A4A', shoes='#3A2A20')
NEPHEW = dict(hair='short', hair_color='#1E1612', top='armor', top_color='#2F3A5A', stud='#C9A050', pants='#2A2A33',
              shoes='#2A2420')
JOSEON_KING = dict(hat='crown', hat_color='#E8B83A', facial='goatee', hair_color='#1E1612', top='robe', top_color='#B23A32',
                   cape='#2E2E6B')
SAMURAI = dict(hat='kabuto', hat_color='#2E2B2B', top='armor', top_color='#7A2A22', stud='#E8C27A', pants='#2A2420',
               shoes='#2A2420')
NELSON = dict(hat='bicorne', hat_color='#1E2230', top='suit', top_color='#22304D', tie='#EFEAE0', pants='#EFEAE0',
              shoes='#1E1E1E')
HOOK = dict(hat='pirate', top='trench', top_color='#9E2B2B', belt='#2A2A2A', tie=None, pants='#2A2A2A', shoes='#2A2A2A')
CHEN_LIN = dict(hat='admiral', hat_color='#7A2A22', facial='beard', hair_color='#1E1612', top='armor', top_color='#B23A32',
                stud='#E8C27A', pants='#2A2A33', shoes='#2A2420')
OLD_WOMAN = dict(hair='long', hair_color='#B5B5B5', top='robe', top_color='#6B5A4A')
GHOST_VIKING = dict(VIK_ARMOR)
