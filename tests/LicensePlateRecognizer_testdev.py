import json
import logging
import time
import sys
import os
sys.path.append('./')
import LicensePlateRecognizer.main as lp
import azure.functions as func

# set environmental variables
with open('./local.settings.json', 'r') as f:
  setting = json.load(f)

evns = setting['Values']
for key, value in evns.items():
    os.environ[key] = value # visible in this process + all children
    
test_query = [
    "n wie marta mm 123",
    "row wie rotenburg wümme n 2 mal 2",
    "frankfurt oder dora berta 3 und 2 Mal die 7.",
    'Nürnberg doppel nordpol zwo 4 5',
    'Ist B Strich SP Strich 7 7 9	',
    'Hamburg AT 3048.',
    'HH X 2048',
    "Mein Kennzeichen is essen dora berta 3 Mal  3 und 4 Mal die 7.",
    "mein kennzeichen ist münchen dora dora  2 4",
    "Mein Kennzeichen ist HH A C 15 5.",
    "Mein Kennzeichen ist Hamburg d d 15 4.",
    "Mein Nummernschild ist Hannover Dora M 132.",
    "Ich lebe in Hamburg aber mein Nummernschild ist köln mm 231.",
    "Mein Kennzeichen ist MM, 3 Mal die 3 und 2 Mal die 7.",
    "Mein Kennzeichen ist HH M T, 3 Mal die 3 und 2 Mal die 7.",
    "Mein Kennzeichen ist M A T, 3 Mal die 3 und 2 Mal die 7.",
    "München Dora Berta 2 3 44",
    "Balingen Berta 333",
    "Freudenstadt doppel Berta 333",
    "Göttingen Berta 333",
    "Das ist Bremen d 333",
    "dortmund dora 222",
    "frankfurt christian 291",
    "das ist GErOlzhofen cäsar emil 222",
    "das kennzeichen ist stadtsteinach julius santiago 762",
    "das kennzeichen ist hamburg a wie anton c wie christian 2048",
    "das kennzeichen ist hh anton cäsar 2048",
    "das kennzeichen ist hh m cäsar dora 248",
    "das kennzeichen ist hamburg ac 2048",
    "BBB 3 mal die 9.",
    "Dreimal B dreimal die 9.",
    "HH B125.",
    "mein kennzeichen ist neustadt an der weinstraße ca zwo 33.",
    "SE für Sägewerk JM 252",
    "hh von hamburg tm 3 zwo 2",
    "row wie rotenburg wümme doppel n 2 mal 2",
    'hh hansestadt hamburg xp 123',
    'Bhw Diepholz Doppel d 160',
    'HB Bremen SW 446',
    'row wie rotenburg wümme ak 61',
    'hamburg hg ein 660',
    'hh wie hamburg gh ein 550',
    'Hamburg AH 7 1 8 H',
    'Hamburg AH 7 1 8 E',
    'doch klar hkl 123',
    'doppel h ks 542',
    'doppel hks 542',
    'HHHL 1 Doppel 03',
    'Aha am 6440',
    'hh wie hamburg tr 234',
    'aero wzz 821',
    'hannover hannover hannover ad anton dora 777',
    'stuttgart stuttgart stuttgart xd 2131',
    'münchen münchen münchen mk 124',
    'das wäre die freie und hansestadt hamburg gustav theodor 3*3',
    'mein kennzeichen ist h.de 382',
    'mein kennzeichen ist 0 strich 75 strich 03',
    'mein kennzeichen is null minus 92 minus 1',
    'mein kennzeichen ist BWL minus 4 1234',
    'mein kennzeichen ist 0 23 - 231',
    ' Y - 23 231',
    'Y - 88',
    'mein kennzeichen ist 0 minus 98 - 873 e',
    'Y 493',
    'y 23 - 34',
    'mein kennzeichen ist landkreis Rostock dora albert 410',
    'mein kennzeichen ist Hansestadt Rostock berta berta 763',
    'mein kennzeichen ist Rostock zulu xaver 812',
    'mein kennzeichen ist HH BA 4324 c',
    'M BA 4324 c',
    'mein kennzeichen ist bundespolizei 23114',
    'HG AD 342',
    'HH 2343',
    'Hamburg 12343',
    'bw l 123',
    'hgak 1400',
    'h 0630',
    'GW MP 83',
    'FB IN 1103',
    'FB - IN 1103',
    'BP 16 - 892',
    'oh man keine ahnung',
    'd i e 1 2 3 4',
    'de ih eh 1 2 3 4'
]

test_lp = [
    "M-MM123",
    "ROW-N22",
    'FF-DB377',
    'N-NN245',
    'B-SP779',
    'HH-AT3048',
    'H-HX2048',
    '',
    'M-DD24',
    'HH-AC155',
    'HH-DD154',
    'H-DM132',
    'K-MM231',
    '',
    '',
    '',
    'M-DB2344',
    'BL-B333',
    'FDS-BB333',
    'GÖ-B333',
    'HB-D333',
    'DO-D222',
    'F-C291',
    'GEO-CE222',
    'SAN-JS762',
    'HH-AC2048',
    'HH-AC2048',
    'HHM-CD248',
    'HH-AC2048',
    'B-BB999',
    'B-BB999',
    'H-HB125',
    'NW-CA233',
    'SE-JM252',
    'HH-TM322',
    "ROW-NN22",
    "HH-XP123",
    "DH-DD160",
    "HB-SW446",
    "ROW-AK61",
    "HH-HG1660",
    "HH-GH1550",
    "HH-AH718H",
    "HH-AH718E",
    "H-KL123",
    "HH-KS542",
    "",
    "HH-HL1003",
    "HH-AM6440",
    "HH-TR234",
    "ROW-ZZ821",
    "H-AD777",
    "S-XD2131",
    "M-MK124",
    "HH-GT333",
    "H-DE382",
    "0-75-03",
    "0-92-1",
    "BWL-41234",
    "0-23-231",
    "Y-23231",
    "Y-88",
    "0-98-873E",
    "Y-493",
    "Y-2334",
    "LRO-DA410",
    "HRO-BB763",
    "ROS-ZX812",
    "HH-BA4324C",
    "M-BA4324C",
    "BP-23114",
    "HG-AD342",
    "H-H2343",
    "HH-12343",
    "B-WL123",
    "HG-AK1400",
    "H-0630",
    "GW-MP83",
    "FB-IN1103",
    "FB-IN1103",
    "BP-16892",
    "",
    "DI-E1234",
    "DI-E1234"
]

start =  time.time()
errors = []
for query, lps in zip(test_query, test_lp):
    try:
        body = {'query':query,
                 "language": "de-de",
                 "locale": "de"
                 }
        
        # Build HTTP request
        req = func.HttpRequest(
            method  = 'GET',
            body    = json.dumps(body).encode('utf8'),
            url     = '/api/LicensePlateRecognizer',
            params  = {}
        )
        # Call the function.
        res = json.loads(lp.main(req).get_body())
        try: 
            res_entity = res['cplEntities'][0]['entity']
        except:
            res_entity = ''
        if res_entity != lps:
            print(print('\033[91m' + query + '\033[0m'))
            print(print('\033[100m' + lps + '\033[0m'))
            logging.warning(f'[ERROR] LP Recognition mismatch for {query} -> {lps} != {res}')
            errors.append(query)
    except Exception as e:
        logging.warning(query, e, res)
        errors.append(query)

end = time.time() - start

print(f'[INFO] DONE -> {1 - (len(errors)/len(test_query)):.2%}. \n\tTotal duration \t\t{end:.3}s \n\tDuration per loop \t{end/len(test_query):.3}s')