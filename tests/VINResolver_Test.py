import json
import logging
import time
import sys
sys.path.insert(1, '..')
from  modules.libvin import Vin
import VINResolver


"""
Valid NA/US VIN (validvin = true): 1FAHP26W49G252740
Invalid NA/US VIN (validvin = false): 1FAHP26W49G252788
Invalid NA/Canada VIN (validvin = false): 2WMCGH3B2CES5C8T2
Valid NA/Canada VIN (validvin = true): 2WMCGH3B5CES5C8T2
Valid Asia/Japan VIN (validvin = true): JN1CV6EP0A0013908
Valid EU/Germany VIN (validvin = true): WDBJF65J71B325157
Invalid VINs (validvin = false): XXXCV6EP0A00139089, WDBJF65J71B3251579
Invalid Chinese VIN (validvin = false): LDNCGH3B2CES5C8T2
Valid Chinese VIN (validvin = true): LDNCGH3B5CES5C8T2

"""

test_query = [
    '1FAHP26W49G252788 ja',
    '2WMCGH3B2CES5C8T2 ja',
    'XXXCV6EP0A00139089 ja',
    'WDBJF65J71B3251579 ja',
    'LDNCGH3B2CES5C8T2 ja',
    'fünfe achte amerika zwo gee einse zwo marie zacharias niklaus zwo acht whiskey kaiser madagaskar whiskey ein ja',
    'zweie tripoli gallipoli florida madagaskar sieben fünf willem dora mercedes uniform werner daimler ein washington neun petra ja',
    'einse golf sechs dieter erhard bertha papa neune christoph luxemburg fünf achte foxtrot alfa valencia deutsch yankie ist mein fahrzeugidentnummer.',
    'xray uniform friedrich golf zwo sophie heinrich alfa kaufmann gallipoli wilhelm xylophon valencia washington viere kilogramm new york ist mein vin',
    'juliett historisch delta marie helmut ypsilon lima yankie daniel drei einse peter drei dora julius sechs charly genau',
    'LHBF5FLSLR4SXN98H ist mein fahrzeugidentnummer.',
    'willem valencia drei sechs nikolaus christian zweie dreie viere victor havana konrad sieben willem erika mercedes sechs ist das.',
    'ein x-ray kaiser zwo romeo helmut drei zweie achte fünfe südpol liverpool marta bertha charlotte null wilhelm ist das.',
    'JMBY6GTNDYLCC470N ist mein vin',
    '2B7TUG1LXSMK2058T ist mein vin',
    'martin alex bertha norbert new york cärsa elektroauto jerusalem sechse dreie marie washington upsala erhard bernd tango amsterdam genau',
    'YBWCPUJWUNCLBE8AB ist das.',
    '2A4RZSRR8PZ3U9XVN ja',
    'MMS9N0H4M4B5KG2MD ja',
    'udin udin eins ein gustav roma ebert richard drei echo zulu amsterdam cärsa kaufmann norbert niklaus null ja',
    'einse valencia eins leopold ypsilon daniel drei heinrich norbert havana foxtrot vier nikolaus null drei bertram whiskey ja',
    'VNEG55YL257X6SB3P ist mein fahrzeugidentnummer.',
    'KMHJ6PYVET0W6VPKU ist mein vin',
    'YV2BJ9W9HFAB8WYL3 ist mein fahrzeugidentnummer.',
    'WA15EXFDF2Y2RPDNK ja',
    'SFDXNAKVDPZ2VSAAJ ja',
    '4VZREJ62BC8PZRJPL ja',
    '6U9UPHZ7R23XA3FKN ist mein vin',
    'lima romeo whiskey havana konrad sophie neun viere tango norbert gee historisch wilhelm tim neune martha romeo ist das.',
    'stefan upsala luxemburg nordpol victor cäsar zeppelin null rosa xray mercedes richard victor viktor null einse tripoli ja',
    'W0LFRV848B0SWK66H genau',
    'valencia werner anja xaver martin delta yokohama kaufmann foxtrot fünfe drei tim zwo fünfe tripoli peter dänemark ist mein fahrzeugidentnummer.',
    'kilogramm nordpol mercedes vier tripoli sieben eins viktor ein dreie kaiser tripoli gallipoli erika willem upsala new york ja',
    'jerusalem havana zürich leopold julius havana fünfe acht sieben zwei peter eins martin zoro acht dreie emil ist mein vin',
    '1C6JBHJ3SW6A1356P ist mein vin',
    'mercedes emil charlotte juliet kaufmann zweie dieter drei fünf paris peter ein victor elektrisch anja fünf sieben genau',
    'WD311XHJUXAYULMZD ist mein fahrzeugidentnummer.',
    'lima berta petra valencia vier friedrich bernd amerika tango sechs zweie siegfried rosa friedrich acht yokohama neun ist das.',
    'JNVAGXCFD3VYN5ZWC ist mein fahrzeugidentnummer.',
    'viere victor viere zwo hotel zürich neun viktor siebene petra friedrich null alpha kilogramm sieben valencia petra ist mein fahrzeugidentnummer.',
    '4A4TAZJXVKM4WPG41 ist mein fahrzeugidentnummer.',
    'zorro liverpool albert washington sierra papa marta kilo sechse papa null xray liverpool whiskey washington siebene yverdon genau',
    'LBPJ4VY8WVD2W3WLY ist mein fahrzeugidentnummer.',
    '9BD585YWCM2YYR2KF ja',
    'LDDCG50A3XBHA25PR ist das.',
    'sechse ulrich neune vier deutschland dreie kaufmann null siebene neune tristan daniel nordpol sechs whiskey willem achte ja',
    'zweie foxtrott tim null gallipoli sechs tristan x-ray sechse fünf berta acht wilhelm elektrisch sieben zweie julius ja',
    'zeppelin golf upsala dreie hotel upsala theodor achte roma paris wilhelm zacharias madagaskar dieter acht fünfe siegfried ist mein fahrzeugidentnummer.',
    'zwei delta vier bernd echo mercedes sechs victor fünfe juliett drei gee roma null fünf neun ein ist mein vin',
    'KM1NZH8J2FZCNCUZP ja',
    '4V2ANN3WXLMMEXMS2 ist das.',
    'LDCLJTVXNW9X36U77 ist mein fahrzeugidentnummer.',
    'ein madagaskar viere lima ludwig yankee zoro achte dieter siebene zulu err drei golf heinrich zwei zeppelin ist mein fahrzeugidentnummer.',
    'KNCURVXEJYAEXT3X4 genau',
    '1M943VZRST9BTJKXV ist das.',
    '1F9G80GZKBP0ZWJHZ ist mein vin',
    'XLBATBZ2CM8WRECMB ist das.',
    '5J6X0HENHXY6LMZ60 genau',
    'XLR1L4GW019811SUL ist mein vin',
    'ZDFX41W6KPPG45WWS ja',
    'zeppelin deutschland drei martin sierra tristan zoro berta stefan vier zürich tango elektrisch acht new york bertha norbert ist das.',
    'neun bravo madagaskar zwo viere paula anja valencia err vier viktor x-ray tristan amerika err upsala werner genau',
    '3HCAVXFCE3F2DA543 ist mein fahrzeugidentnummer.',
    'zoro alfa marie udin petra new york siebene julius ludwig neune charly sechse gustav konrad gee leopold juliett ist das.',
    '9BDLFX976NVVA4TVC ist mein vin',
    'VANTVW2763AN0A9VA ist das.',
    'JA41SSLM4SSA86G5T ist mein fahrzeugidentnummer.',
    'MB81XPZNWBP0V1GK5 ist mein fahrzeugidentnummer.',
    'washington berta yankie zwo sechs gee stefan friedrich viktor paris baltimore juliett upsala achte ulrich kilo null ist mein fahrzeugidentnummer.',
    'WD4A8YVK2VVWFX6NB genau',
    'südpol julius niklaus udin wilhelm peter drei foxtrot drei erich heinrich paula yankie sechs achte sieben foxtrot ja',
    '2G6MV2GG9ANUTHSNS ist mein vin',
    'drei golf yankee roma heinrich x-ray neune sechse drei err hotel xray jakob madagaskar marie cerca sechs ja',
    'zwei helmut marta xaver new york fünf viktor sechse vier siegfried null udin xaver einse charlie ein sieben ja',
    'ZAMGF0YANKWXVSUY3 genau',
    'victor foxtrot sieben viktor upsala xanthippe liverpool nordpol chiasso xylophon fünf vier golf roma peter fünfe heinrich ja',
    'NLNZLX9YGBUC7G2LS ist das.',
    'YH4FHLBNNVN1P4Y54 genau',
    'MMTRZG443MT1F0H1B ist mein fahrzeugidentnummer.',
    'drei dänemark dreie x-ray siebene victor romeo benz nikolaus viktor vier zeppelin dora golf kaufmann null viere ist mein vin',
    '2V4JB2ZJKVZ6JX7KV ist mein fahrzeugidentnummer.',
    'lima foxtrott paula sechse karl historisch xanthippe golf dreie mike deutsch hotel petra viere peter foxtrot kilo ist mein fahrzeugidentnummer.',
    'WDCNNC9MGY8CPXXXJ ist das.',
    'LVVXBWTCX5EDP6WH7 genau',
    '3FAYFDTANE5SWWKYA genau',
    'R2PKAHE2FHWV0RYFT ja',
    'leopold bravo benz alpha null erhard siegfried luxemburg xylophon havana bertram heinrich achte fünfe madagaskar null mercedes genau',
    'kaufmann mercedes achte berta dieter viktor willem november foxtrott florida drei dreie foxtrott berta yankie gustav bertram ist mein vin',
    '8BR51PKVB41SMN8PM ja',
    'viere foxtrot juliett alpha sechse gustav albert kaiser hotel fünf neun juliett alpha norbert juliett achte nikolaus ist mein vin',
    '93HF7NKBCNKSV7BCX ist mein vin',
    '46JFM3WBMSXVUVD0B ist mein fahrzeugidentnummer.',
    'WD4GHEJWS6E67UTCG ja',
    'tim nordpol emil zeppelin viktor dänemark victor uniform mercedes sechse einse vier siebene bernd sechse fünfe golf ist mein fahrzeugidentnummer.',
    '2GXHBULTKLL0NER8E ist das.',
    'VTLESP70Y7K6MLYFU ist mein vin',
    'JHNRFER9BBJD92Z43 ist mein vin',
    'JHBV2NBZJ3KY0UJPC ist das.',
    'neune golf amerika roma vier drei luxemburg hotel eins fünfe alpha einse victor marta yankee santiago berta ist das.',
    'MMAYP4EAX1X5CFFBG ist mein vin',
    'LFYJRZGJRTNBSHCL9 genau',
    'TNEFJ2D0JG9W4W33B ist mein fahrzeugidentnummer.',
    'UU5H8NCEW7K0KHX5Z genau',
    'neune baltimore golf theodor uniform zürich nordpol papa sieben martha achte sechs x-ray fünf echo emil anja genau',
    '93VEA0B6U147E4G8A genau'
    ]

test_vin = [
            '1FAHP26W49G252788',
            '2WMCGH3B2CES5C8T2',
            'XXXCV6EP0A00139089',
            'WDBJF65J71B3251579',
            'LDNCGH3B2CES5C8T2',
            '58A2G12MZN28WKMW1', '2TGFM75WDMUWD1W9P', '1G6DEBP9CL58FAVDY', 'XUFG2SHAKGWXVW4KN', 
            'JHDMHYLYD31P3DJ6C', 'LHBF5FLSLR4SXN98H', 'WV36NC234VHK7WEM6', '1XK2RH3285SLMBC0W',
            'JMBY6GTNDYLCC470N', '2B7TUG1LXSMK2058T', 'MABNNCEJ63MWUEBTA', 'YBWCPUJWUNCLBE8AB', 
            '2A4RZSRR8PZ3U9XVN', 'MMS9N0H4M4B5KG2MD', 'UU11GRER3EZACKNN0', '1V1LYD3HNHF4N03BW', 
            'VNEG55YL257X6SB3P', 'KMHJ6PYVET0W6VPKU', 'YV2BJ9W9HFAB8WYL3', 'WA15EXFDF2Y2RPDNK', 
            'SFDXNAKVDPZ2VSAAJ', '4VZREJ62BC8PZRJPL', '6U9UPHZ7R23XA3FKN', 'LRWHKS94TNGHWT9MR', 
            'SULNVCZ0RXMRVV01T', 'W0LFRV848B0SWK66H', 'VWAXMDYKF53T25TPD', 'KNM4T71V13KTGEWUN', 
            'JHZLJH5872P1MZ83E', '1C6JBHJ3SW6A1356P', 'MECJK2D35PP1VEA57', 'WD311XHJUXAYULMZD', 
            'LBPV4FBAT62SRF8Y9', 'JNVAGXCFD3VYN5ZWC', '4V42HZ9V7PF0AK7VP', '4A4TAZJXVKM4WPG41', 
            'ZLAWSPMK6P0XLWW7Y', 'LBPJ4VY8WVD2W3WLY', '9BD585YWCM2YYR2KF', 'LDDCG50A3XBHA25PR', 
            '6U94D3K079TDN6WW8', '2FT0G6TX65B8WE72J', 'ZGU3HUT8RPWZMD85S', '2D4BEM6V5J3GR0591', 
            'KM1NZH8J2FZCNCUZP', '4V2ANN3WXLMMEXMS2', 'LDCLJTVXNW9X36U77', '1M4LLYZ8D7ZR3GH2Z', 
            'KNCURVXEJYAEXT3X4', '1M943VZRST9BTJKXV', '1F9G80GZKBP0ZWJHZ', 'XLBATBZ2CM8WRECMB', 
            '5J6X0HENHXY6LMZ60', 'XLR1L4GW019811SUL', 'ZDFX41W6KPPG45WWS', 'ZD3MSTZBS4ZTE8NBN', 
            '9BM24PAVR4VXTARUW', '3HCAVXFCE3F2DA543', 'ZAMUPN7JL9C6GKGLJ', '9BDLFX976NVVA4TVC', 
            'VANTVW2763AN0A9VA', 'JA41SSLM4SSA86G5T', 'MB81XPZNWBP0V1GK5', 'WBY26GSFVPBJU8UK0', 
            'WD4A8YVK2VVWFX6NB', 'SJNUWP3F3EHPY687F', '2G6MV2GG9ANUTHSNS', '3GYRHX963RHXJMMC6', 
            '2HMXN5V64S0UX1C17', 'ZAMGF0YANKWXVSUY3', 'VF7VUXLNCX54GRP5H', 'NLNZLX9YGBUC7G2LS', 
            'YH4FHLBNNVN1P4Y54', 'MMTRZG443MT1F0H1B', '3D3X7VRBNV4ZDGK04', '2V4JB2ZJKVZ6JX7KV', 
            'LFP6KHXG3MDHP4PFK', 'WDCNNC9MGY8CPXXXJ', 'LVVXBWTCX5EDP6WH7', '3FAYFDTANE5SWWKYA', 
            'R2PKAHE2FHWV0RYFT', 'LBBA0ESLXHBH85M0M', 'KM8BDVWNFF33FBYGB', '8BR51PKVB41SMN8PM', 
            '4FJA6GAKH59JANJ8N', '93HF7NKBCNKSV7BCX', '46JFM3WBMSXVUVD0B', 'WD4GHEJWS6E67UTCG', 
            'TNEZVDVUM6147B65G', '2GXHBULTKLL0NER8E', 'VTLESP70Y7K6MLYFU', 'JHNRFER9BBJD92Z43', 
            'JHBV2NBZJ3KY0UJPC', '9GAR43LH15A1VMYSB', 'MMAYP4EAX1X5CFFBG', 'LFYJRZGJRTNBSHCL9', 
            'TNEFJ2D0JG9W4W33B', 'UU5H8NCEW7K0KHX5Z', '9BGTUZNP7M86X5EEA', '93VEA0B6U147E4G8A']

test_validin =[False, False, False, False, False,
               False, False, False, True, True, False, True, True, True, False, True, 
               True, False, True, True, False, True, True, True, True, True, False, 
               True, False, True, True, True, True, True, False, True, True, False, 
               True, False, False, True, False, True, False, True, False, True, True, 
               True, False, False, False, True, False, False, True, False, True, True,
               True, True, False, True, True, True, True, True, True, True, True, False,
               False, False, True, True, True, True, True, False, False, False, True, False,
               False, True, False, True, True, False, True, False, True, True, False, True,
               True, True, True, True, False, True, True, True, True]

start =  time.time()
errors = []
luis_err = []
validvin_err = []
status_err = []
for query, vin in zip(test_query, test_vin):
    try:
        res, status_code = VINResolver.test_VINResolver(query)
        resVIN = res['vinQuery'].upper()
        v = Vin(resVIN)
        if resVIN != vin.upper():
            logging.warning(f'[ERROR Luis] VIN mismatch for {query} -> {vin} != {resVIN}')
            errors.append(query)
            luis_err.append(query)
        if not v.is_valid:
            logging.warning(f'[ERROR vinvalid] false VIN:')
            validvin_err.append(query)
        if status_code:
            logging.warning(f'[ERROR] VIN mismatch for {query} -> {vin} != {resVIN}')
            status_err.append(query)
    except Exception as e:
        logging.warning(query, e, res)
        errors.append(query)

end = time.time() - start

logging.warning(f'[INFO] DONE -> {1 - (len(errors)/len(test_query)):.2%}. \n\tTotal duration \t\t{end:.3}s \n\tDuration per loop \t{end/len(test_query):.3}s')