''' Resolve words to numbers '''
numbers_dict = {
	'en': {
		'oh':		0,
		'zero':		0,
		'one':		1,
		'two':		2,
		'three':	3,
		'four': 	4,
		'five': 	5,
		'six': 		6,
		'seven': 	7,
		'eight': 	8,
		'nine': 	9
	},
	'de': {
		'null':		0,
		'einse':	1,
		'eins':		1,
		'ein':		1,
		'zwo':		2,
		'zweie':	2,
		'zwei':		2,
		'dreie':	3,
		'drei':		3,
		'viere':	4,
		'vier': 	4,
		'fünfe':	5,
		'fünf': 	5,
		'sechse':	6,
		'sechs': 	6,
		'siebene':	7,
		'sieben': 	7,
		'achte':	8,
		'acht': 	8,
		'neune':	9,
		'neun': 	9,
		'zehne':	10,
		'zehn':		10,
		'elfe':		11,
		'zwölfe':	12
		}
}

''' Resolve repeats to numbers '''
numbers_repeat = {
	'en': {
		'double': 		2,
		'triple': 		3,
		'quadruple':	4,
		'quintuple': 	5
	},
	'de': {
		'doppelt':		2,
		'doppel': 		2,
		'zweimal':		2,
		'dreimal':		3,
		'viermal':		4,
		'fünfmal':		5,
		'sechsmal':		6,
		'siebenmal':	7
	}
}

"""List of words used in the reduction stage of text cleaning"""
alphabet = {
	'de': {
		"aero":"ro",
		"alpha":"a",
		"albert":"a",
		"anton":"a",
		"anja":"a",
		"anna":"a",
		"amerika":"a",
		"alex":"a",
		"amsterdam":"a",
		"alfa":"a",
		"alpha umlaut":"ä",
		"ärger":"ä",
		"bravo":"b",
		"bernd":"b",
		"berta":"b",
		"bertha":"b",
		"bertram":"b",
		"baltimore":"b",
		"benz":"b",
		"beka":"bk",
		"cerca":"c",
		"charlie":"c",
		"christine":"c",
		"cäsar":"c",
		"cärsa":"c",
		"christoph":"c",
		"christopher":"c",
		"christian":"c",
		"charly":"c",
		"casablanca":"c",
		"charlotte":"c",
		"chiasso":"c",
		"christian":"c",
		"zeqa":"ck",
		"delta":"d",
		"dora":"d",
		"daniel":"d",
		"daimler":"d",
		"dänemark":"d",
		"dieter":"d",
		"deca":"dk",
		"echo":"e",
		"ebert":"e",
		"emil":"e",
		"edison":"e",
		"elektro":"e",
		"elektrisch":"e",
		"elektroauto":"e",
		"erhard":"e",
		"erich":"e",
		"erika":"e",
		"foxtrott":"f",
		"friedrich":"f",
		"florida":"f",
		"foxtrot":"f",
		"golf":"g",
		"gustav":"g",
		"gallipoli":"g",
		"gee":"g",
		"hotel":"h",
		"heinrich":"h",
		"helmut":"h",
		"havana":"h",
		"hahah":"hh",
		"historisch":"h",
		"haha":"hh",
		"aha":"hh",
		"ahh":"hh",
		"aaah":"hh",
		"india":"i",
		"ida":"i",
		"italia":"i",
		"jan":"j",
		"juliet":"j",
		"julius":"j",
		"johann":"j",
		"jakob":"j",
		"jerusalem":"j",
		"juliett":"j",
		"kilo":"k",
		"kaufmann":"k",
		"konrad":"k",
		"kaiser":"k",
		"karl":"k",
		"kilogramm":"k",
		"caca":"kk",
		"qaqa":"kk",
		"caha":"kh",
		"lima":"l",
		"ludwig":"l",
		"leopold":"l",
		"liverpool":"l",
		"luxemburg":"l",
		"martin":"m",
		"mike":"m",
		"martha":"m",
		"marta":"m",
		"marie":"m",
		"madagaskar":"m",
		"mercedes":"m",
		"emka":"mk",
		"november":"n",
		"nordpol":"n",
		"norbert":"n",
		"nikolaus":"n",
		"niklaus":"n",
		"new york":"n",
		"oscar":"o",
		"oskar":"o",
		"otto":"o",
		"oslo":"o",
		"oscar umlaut":"ö",
		"ökonom":"ö",
		"österreich":"ö",
		"oerlikon":"ö",
		"papa":"p",
		"paula":"p",
		"peter":"p",
		"petra":"p",
		"paris":"p",
		"quebec":"q",
		"quelle":"q",
		"quasi":"q",
		"québec":"q",
		"romeo":"r",
		"richard":"r",
		"rosa":"r",
		"roma":"r",
		"err":"r",
		"err gee":"rg",
		"errou":"ru",
		"sierra":"s",
		"samuel":"s",
		"siegfried":"s",
		"sophie":"s",
		"stefan":"s",
		"santiago":"s",
		"südpol":"s",
		"eska":"sk",
		"schule":"sch",
		"eszett":"ẞ",
		"tango":"t",
		"theodor":"t",
		"tim":"t",
		"tripoli":"t",
		"tristan":"t",
		"theka":"tk",
		"udin":"u",
		"uniform":"u",
		"ulrich":"u",
		"upsala":"u",
		"uniform umlaut":"ü",
		"übermut":"ü",
		"übel":"ü",
		"victor":"v",
		"viktor":"v",
		"valencia":"v",
		"whiskey":"w",
		"wilhelm":"w",
		"willem":"w",
		"werner":"w",
		"washington":"w",
		"x-ray":"x",
		"xray":"x",
		"xylophon":"x",
		"xanthippe":"x",
		"xaver":"x",
		"yankie":"y",
		"ypsilon":"y",
		"yverdon":"y",
		"yokohama":"y",
		"yankee":"y",
		"zulu":"z",
		"zeppelin":"z",
		"zacharias":"z",
		"zürich":"z",
		"zorro":"z",
		"zoro":"z",
		"zetka":"zk",
		"ß":"sz",
		"deutschland":"d",
		"deutsch":"d",
		"strich":"-",
		"minus":"-",
		"bindestrich":"-",
		"trennung":"-"},
	'en': {
		"alpha":"a"
	}
}

""" List of ambiguous areas """
ambiguous = {
    'kreis rostock':'lro',
    'landkreis rostock':'lro',
	'hansestadt rostock':'hro',
	'rostock':'ros',
    'hildesheim':'alf',
	'schaumburg':'ri',
	'nordwestmecklenburg':'gdb',
	'nordwestmecklenburg':'gvm',
	'nordwestmecklenburg':'wis',
	'northeim':'gan',
	'northeim':'ein',
	'rotenburg wuemme':'brv',
	'rendsburg eckernförde':'eck',
	'rendsburg-eckernförde':'eck',
	'dithmarschen':'med',
	'göttingen':'oha',
	'göttingen':'dud',
	'göttingen':'hmü',
	'uslar':'ein',
	'uslar':'gan',
	'frankfurt':'ff'
}

"""List of German Area Codes and short forms"""
areas = {
	'augsburg':'a',
	'augschburg':'a',
	'aalen':'aa',
	'aschaffenburg':'ab',
	'altenburg':'abg',
	'anhalt bitterfeld':'abi',
	'aachen':'ac',
	'auerbach':'ae',
	'ahaus':'ah',
	'aibling':'aib',
	'aichach':'aic',
	'altenkirchen':'ak',
	'alfeld':'alf',
	'alzenau':'alz',
	'amberg':'am',
	'ansbach':'an',
	'annaberg':'ana',
	'angermünde':'ang',
	'anklam':'ank',
	'altötting':'aö',
	'apolda':'ap',
	'arnstadt':'arn',
	'artern':'art',
	'amberg sulzbach':'as',
	'aschersleben':'asl',
	'aue schwarzenberg':'asz',
	'altentreptow':'at',
	'aue':'au',
	'aurich':'aur',
	'ahrweiler':'aw',
	'alzey':'az',
	'anhalt zerbst':'aze',
	'berlin':'b',
	'bamberg':'ba',
	'baden baden':'bad',
	'barnim':'bar',
	'böblingen':'bb',
	'bernburg':'bbg',
	'brandenburgische landesregierung':'bbl',
	'biberach':'bc',
	'buchen':'bch',
	'bundesdienst':'bd',
	'beckum':'be',
	'brand erbisdorf':'bed',
	'bernau':'ber',
	'burgsteinfurt':'bf',
	'berchtesgaden':'bgd',
	'berchtesgadenerland':'bgl',
	'bühl':'bh',
	'bielefeld':'bi',
	'biedenkopf':'bid',
	'bingen':'bin',
	'birkenfeld':'bir',
	'bitburg':'bit',
	'bischofswerda':'biw',
	'backnang':'bk',
	'bernkastel':'bks',
	'balingen':'bl',
	'berleburg':'blb',
	'burgenlandkreis':'blk',
	'bergheim':'bm',
	'rhein erft':'bm',
	'rhein erft':'bm',
	'rendsburg eckenförde':'rd',
	'rendsburg-eckenförde':'rd',
	'hameln-pyrmont':'hm',
	'hameln pyrmont':'hm',
	'nienburg/weser':'ni',
	'nienburg weser':'ni',
	'lauenburg':'rz',
	'bonn':'bn',
	'borna':'bna',
	'bochum':'bo',
	'börde':'bö',
	'bogen':'bog',
	'bocholt':'boh',
	'borken':'bor',
	'bottrop':'bot',
	'bundespolizei':'bp',
	'bundes polizei':'bp',
	'polizei':'bp',
	'brake':'bra',
	'brandenburg':'brb',
	'burg':'brg',
	'brückenau':'brk',
	'braunlage':'brl',
	'bremervörde':'brv',
	'braunschweig':'bs',
	'bersenbrück':'bsb',
	'beeskow':'bsk',
	'bayreuth':'bt',
	'bitterfeld':'btf',
	'büdingen':'büd',
	'burglengenfeld':'bul',
	'büren':'bür',
	'büsingen':'büs',
	'bützow':'büz',
	'bundes wasserstraßen und schifffahrtsverwaltung':'bw',
	'bundes wasserstraßen schifffahrtsverwaltung':'bw',
	'baden württembergischer landtag':'bwl',
	'bayerischer landtag':'byl',
	'bautzen':'bz',
	'chemnitz':'c',
	'calau':'ca',
	'castrop':'cas',
	'cottbus':'cb',
	'celle':'ce',
	'zelle':'ce',
	'cham':'cha',
	'cloppenburg':'clp',
	'clausthal zellerfeld':'clz',
	'coburg':'co',
	'cochem':'coc',
	'coesfeld':'coe',
	'crailsheim':'cr',
	'cuxhaven':'cux',
	'calw':'cw',
	'düsseldorf':'d',
	'darmstadt':'da',
	'dachau':'dah',
	'dannenberg':'dan',
	'daun':'dau',
	'bad doberan':'dbr',
	'doberan':'dbr',
	'dresden':'dd',
	'dessau':'de',
	'deggendorf':'deg',
	'delmenhorst':'del',
	'dingolfing':'dgf',
	'diepholz':'dh',
	'dieburg':'di',
	'dillenburg':'dil',
	'dinslaken':'din',
	'diez':'diz',
	'dinkelsbühl':'dkb',
	'dithmarschen':'hei',
	'döbeln':'dl',
	'dillingen':'dlg',
	'demmin':'dm',
	'düren':'dn',
	'dortmund':'do',
	'donauwörth':'don',
	'duisburg':'du',
	'duderstadt':'dud',
	'dürkheim an der weinstraße':'düw',
	'dippoldiswalde':'dw',
	'delitzsch':'dz',
	'essen':'e',
	'eisenach':'ea',
	'eilenburg':'eb',
	'ebersberg':'ebe',
	'ebern':'ebn',
	'ebermannstadt':'ebs',
	'eckernförde':'eck',
	'erding':'ed',
	'elbe elster':'ee',
	'elmenhorst':'rz',
	'erfurt':'ef',
	'eggenfelden':'eg',
	'eisenhüttenstadt':'eh',
	'eichstätt':'ei',
	'eichsfeld':'eic',
	'eisleben':'eil',
	'einbeck':'ein',
	'eisenberg':'eis',
	'emsland':'el',
	'emmendingen':'em',
	'emden':'emd',
	'ems':'ems',
	'ennepe':'en',
	'erlangen':'er',
	'erbach':'erb',
	'erlangen höchstadt':'erh',
	'erkelenz':'erk',
	'erzgebirge':'erz',
	'esslingen':'es',
	'eschenbach':'esb',
	'eschwege':'esw',
	'euskirchen':'eu',
	'eberswalde':'ew',
	'frankfurt':'f',
	'frankfurt am main':'f',
	'frankfurt main':'f',
	'wetteraukreis':'fb',
	'fulda':'fd',
	'friedberg':'fdb',
	'freudenstadt':'fds',
	'feuchtwangen':'feu',
	'frankfurt oder':'ff',
	'fürstenfeldbruck':'ffb',
	'freiberg':'fg',
	'finsterwalde':'fi',
	'frankenberg':'fkb',
	'flensburg':'fl',
	'flöha':'flö',
	'friedrichshafen':'fn',
	'forchheim':'fo',
	'forst':'for',
	'freiburg':'fr',
	'freyung grafenau':'frg',
	'friesland':'fri',
	'freienwalde':'frw',
	'freising':'fs',
	'frankenthal':'ft',
	'freital':'ftl',
	'fürth':'fü',
	'füssen':'füs',
	'fürstenwalde':'fw',
	'fritzlar':'fz',
	'gera':'g',
	'gardelegen':'ga',
	'bad gandersheim':'gan',
	'gandersheim':'gan',
	'garmisch partenkirchen':'gap',
	'glauchau':'gc',
	'gmünd':'gd',
	'gadebusch':'gdb',
	'gelsenkirchen':'ge',
	'geldern':'gel',
	'gerolzhofen':'geo',
	'germersheim':'ger',
	'gifhorn':'gf',
	'groß gerau':'gg',
	'geithain':'gha',
	'gräfenhainichen':'ghc',
	'gießen':'gi',
	'geilenkirchen':'gk',
	'gladbach':'gl',
	'gladbeck':'gla',
	'gummersbach':'gm',
	'grimmen':'gmn',
	'gelnhausen':'gn',
	'genthin':'gnt',
	'göttingen':'gö',
	'goar':'goa',
	'goarshausen':'goh',
	'göppingen':'gp',
	'görlitz':'gr',
	'grafenau':'gra',
	'großenhain':'grh',
	'griesbach':'gri',
	'grimma':'grm',
	'greiz':'grz',
	'goslar':'gs',
	'gütersloh':'gt',
	'gotha':'gth',
	'güstrow':'gü',
	'guben':'gub',
	'gunzenhausen':'gun',
	'grevenbroich':'gv',
	'grevesmühlen':'gvm',
	'greifswald':'gw',
	'günzburg':'gz',
	'hannover':'h',
	'hanover':'h',
	'hagen':'ha',
	'hammelburg':'hab',
	'halle':'hal',
	'hamm':'ham',
	'hassfurt':'has',
	'bremen':'hb',
	'bremerhaven':'hb',
	'bremerhafen':'hb',
	'hansestadt bremen':'hb',
	'hildburghausen':'hbn',
	'halberstadt':'hbs',
	'hainichen':'hc',
	'hechingen':'hch',
	'heidelberg':'hd',
	'heidenheim':'hdh',
	'haldensleben':'hdl',
	'helmstedt':'he',
	'hersbruck':'heb',
	'hersfeld':'hef',
	'heide':'hei',
	'hessischer landtag':'hel',
	'herne':'her',
	'hettstedt':'het',
	'herford':'hf',
	'herzogtum lauenburg':'rz',
	'bad homburg':'hg',
	'hagenow':'hgn',
	'hansestadt greifswald':'hgw',
	'hamburg':'hh',
	'hansestadt hamburg':'hh',
	'freie und hansestadt hamburg':'hh',
	'freie hansestadt hamburg':'hh',
	'hohenmölsen':'hhm',
	'hildesheim':'hi',
	'heiligenstadt':'hig',
	'hilpoltstein':'hip',
	'heidekreis':'hk',
	'lübeck':'hl',
	'hansestadt lübeck':'hl',
	'hameln':'hm',
	'hann münden':'hmü',
	'hannoversch münden':'hmü', 
	'heilbronn':'hn',
	'hof':'ho',
	'hofgeismar':'hog',
	'hofheim':'hoh',
	'holzminden':'hol',
	'homburg':'hom',
	'horb':'hor',
	'höchstadt':'hös',
	'hohenstein':'hot',
	'heppenheim':'hp',
	'homberg':'hr',
	'landkreis rostock':'lro',
	'hansestadt rostock':'hro',
	'rostock':'ros',
	'heinsberg':'hs',
	'hochsauerlandkreis':'hsk',
	'stralsund':'hst',
	'hansestadt stralsund':'hst',
	'hanau':'hu',
	'havelberg':'hv',
	'havelland':'hvl',
	'höxter':'hx',
	'hoyerswerda':'hy',
	'harz':'hz',
	'harburg':'wl',
	'minden lübbecke':'mi',
	'ingbert':'igb',
	'ilm kreis':'ik',
	'ilmenau':'il',
	'illertissen':'ill',
	'ingolstadt':'in',
	'itzehoe':'iz',
	'jena':'j',
	'jessen':'je',
	'jerichower land':'jl',
	'jülich':'jül',
	'köln':'k',
	'karlsruhe':'ka',
	'korbach':'kb',
	'kronach':'kc',
	'kempten':'ke',
	'kelheim':'keh',
	'kehl':'kel',
	'kemnath':'kem',
	'kaufbeuren':'kf',
	'kissingen':'kg',
	'kreuznach':'kh',
	'kiel':'ki',
	'kirchheimbolanden':'kib',
	'kempen, krefeld':'kk',
	'kaiserslautern':'kl',
	'kleve':'kle',
	'klötze':'klz',
	'kamenz':'km',
	'konstanz':'kn',
	'koblenz':'ko',
	'königshofen':'kön',
	'köthen':'köt',
	'kötzting':'köz',
	'krefeld':'kr',
	'krumbach':'kru',
	'kassel':'ks',
	'kitzingen':'kt',
	'kulmbach':'ku',
	'künzelsau':'kün',
	'kusel':'kus',
	'königs wusterhausen':'kw',
	'kyritz':'ky',
	'kyffhäuser':'kyf',
	'leipzig':'l',
	'landshut':'la',
	'landau':'lan',
	'lauf':'lau',
	'ludwigsburg':'lb',
	'lobenstein':'lbs',
	'lübz':'lbz',
	'luckau':'lc',
	'dingolfing landau':'ld',
	'lahn dill kreis':'ldk',
	'landkreis dahme spreewald':'lds',
	'leonberg':'leo',
	'leer':'ler',
	'leverkusen':'lev',
	'laufen':'lf',
	'lüneburg':'lg',
	'lüdinghausen':'lh',
	'lindau':'li',
	'liebenwerda':'lib',
	'lichtenfels':'lif',
	'lippe':'lip',
	'landsberg am lech':'ll',
	'limburg':'lm',
	'lübben':'ln',
	'lörrach':'lö',
	'löbau':'löb',
	'landkreis oder spre':'los',
	'lippstadt':'lp',
	'lahr':'lr',
	'land sachsen anhalt':'lsa',
	'landtag sachsen':'lsn',
	'langensalza':'lsz',
	'ludwigshafen':'lu',
	'lünen':'lün',
	'ludwigslust, parchim':'lup',
	'ludwigslust':'lwl',
	'münchen':'m',
	'mannheim':'ma',
	'marienberg':'mab',
	'mainburg':'mai',
	'marktredwitz':'mak',
	'mallersdorf':'mal',
	'miesbach':'mb',
	'malchin':'mc',
	'magdeburg':'md',
	'mettmann':'me',
	'meldorf':'med',
	'melsungen':'meg',
	'meißen':'mei',
	'mittlerer erzgebirgskreis':'mek',
	'melle':'mel',
	'merseburg':'mer',
	'mellrichstadt':'met',
	'mönchengladbach':'mg',
	'mergentheim':'mgh',
	'meiningen':'mgn',
	'mülheim':'mh',
	'mühlhausen':'mhl',
	'minden':'mi',
	'minden-lübbecke':'mi',
	'minden lübbecke':'mi',
	'miltenberg':'mil',
	'märkischer kreis':'mk',
	'main kinzig kreis':'mkk',
	'mansfelder land':'ml',
	'memmingen':'mm',
	'mindelheim':'mn',
	'moers':'mo',
	'marktoberdorf':'mod',
	'märkisch oderland':'mol',
	'monschau':'mon',
	'mosbach':'mos',
	'merseburg querfurt':'mq',
	'marburg':'mr',
	'münster':'ms',
	'mecklenburgische seenplatte':'mse',
	'mansfeld südharz':'msh',
	'main spessart':'msp',
	'mecklenburg strelitz':'mst',
	'main taunus kreis':'mtk',
	'muldental':'mtl',
	'mühldorf':'mü',
	'münchberg':'müb',
	'müritz':'mür',
	'mecklenburg vorpommerscher landtag':'mvl',
	'mittweida':'mw',
	'mayen':'my',
	'mayen koblenz':'myk',
	'mainz':'mz',
	'merzig':'mzg',
	'nürnberg':'n',
	'nabburg':'nab',
	'naila':'nai',
	'nauen':'nau',
	'neubrandenburg':'nb',
	'neuburg an der donau':'nd',
	'nordhausen':'ndh',
	'rhein-kreis neuss':'ne',
	'rheinkreis neuss':'ne',
	'rhein kreis neuss':'ne',
	'neuss':'ne',
	'neustadt an der aisch':'nea',
	'nebra':'neb',
	'neustadt bei coburg':'nec',
	'neunburg':'nen',
	'neustadt an der saale':'nes',
	'neustadt an der waldnaab':'new',
	'nordfriesland':'nf',
	'neuhaus':'nh',
	'nienburg':'ni',
	'neunkirchen':'nk',
	'niedersächsischer landtag':'nl',
	'neumarkt':'nm',
	'naumburg':'nmb',
	'neumünster':'nms',
	'nördlingen':'nö',
	'nordhorn':'noh',
	'niederschlesische oberlausitz':'nol',
	'northeim':'nom',
	'norden':'nor',
	'neuruppin':'np',
	'neuwied am rhein':'nr',
	'nordrhein westfalen':'nrw',
	'nürtingen':'nt',
	'neu ulm':'nu',
	'nordvorpommern':'nvp',
	'neustadt an der weinstraße':'nw',
	'nordwestmecklenburg':'nwm',
	'niesky':'ny',
	'neustrelitz':'nz',
	'oberallgäu':'oa',
	'ostallgäu':'oal',
	'oberhausen':'ob',
	'obernburg':'obb',
	'osterburg':'obg',
	'oschersleben':'oc',
	'ochsenfurt':'och',
	'bad oldesloe':'od',
	'bad oldeslö':'od',
	'bad oldeslo':'od',
	'oldesloer':'od',
	'oldeslö':'od',
	'oldesloe':'od',
	'olpe':'oe',
	'offenbach':'of',
	'offenburg':'og',
	'ostholstein':'oh',
	'osterode am harz':'oha',
	'öhringen':'öhr',
	'oberhavel':'ohv',
	'osterholz':'ohz',
	'osterholz scharmbeck':'ohz',
	'osterholz scharmbeek':'ohz',
	'ohrekreis':'ok',
	'oldenburg':'ol',
	'opladen':'op',
	'ostprignitz, ruppin':'opr',
	'osnabrück':'os',
	'oberspreewald lausitz':'osl',
	'oberviechtach':'ovi',
	'obervogtland':'ovl',
	'oschatz':'oz',
	'potsdam':'p',
	'passau':'pa',
	'pfaffenhofen':'paf',
	'pfarrkirchen':'pan',
	'parsberg':'par',
	'paderborn':'pb',
	'parchim':'pch',
	'peine':'pe',
	'pegnitz':'peg',
	'pforzheim':'pf',
	'pinneberg':'pi',
	'pirna':'pir',
	'plauen':'pl',
	'plön':'plö',
	'potsdam mittelmark':'pm',
	'pößneck':'pn',
	'prignitz':'pr',
	'prüm':'prü',
	'pirmasens':'ps',
	'pasewalk':'pw',
	'prenzlau':'pz',
	'querfurt':'qft',
	'quedlinburg':'qlb',
	'regensburg':'r',
	'württemberg':'ra',
	'reichenbach':'rc',
	'rendsburg':'rd',
	'ribnitz damgarten':'rdg',
	'recklinghausen':'re',
	'regen':'reg',
	'rehau':'reh',
	'reichenhall':'rei',
	'rems murr kreis':'wn',
	'rems murr':'wn',
	'riesa großenhain':'rg',
	'roth':'rh',
	'rinteln':'ri',
	'riedenburg':'rid',
	'riesa':'rie',
	'rochlitz':'rl',
	'röbel müritz':'rm',
	'rathenow':'rn',
	'rosenheim':'ro',
	'roding':'rod',
	'rotenburg wuemme':'row',
	'rotenburg':'row',
	'rotenburg an der fulda':'rof',
	'rockenhausen':'rok',
	'rottenburg an der laaber':'rol',
	'rothenburg ob der tauber':'rot',
	'rothenburg':'rot',
	'rhein pfalz':'rp',
	'rheinland pfälzischer landtag':'rpl',
	'remscheid':'rs',
	'rosslau':'rsl',
	'reutlingen':'rt',
	'rudolstadt':'ru',
	'rüdesheim':'rüd',
	'rügen':'rüg',
	'ravensburg':'rv',
	'rottweil':'rw',
	'ratzeburg':'rz',
	'stuttgart':'s',
	'saarburg':'sab',
	'schwandorf':'sad',
	'saarländischer landtag':'sal',
	'stadtsteinach':'san',
	'salzwedel':'saw',
	'saarbrücken':'sb',
	'strasburg':'sbg',
	'schönebeck':'sbk',
	'schwabach':'sc',
	'schleiz':'scz',
	'sondershausen':'sdh',
	'stendal':'sdl',
	'schwedt':'sdt',
	'bad segeberg':'se',
	'segeberg':'se',
	'sebnitz':'seb',
	'seelow':'see',
	'scheinfeld':'sef',
	'selb':'sel',
	'senftenberg':'sfb',
	'staßfurt':'sft',
	'solingen':'sg',
	'sangerhausen':'sgh',
	'schleswig holstein':'sh',
	'schwäbisch hall':'sha',
	'schaumburg':'shg',
	'stadthagen':'shg',
	'saale holzland kreis':'shk',
	'suhl':'shl',
	'siegen':'si',
	'sigmaringen':'sig',
	'simmern':'sim',
	'saalekreis':'sk',
	'schleswig':'sl',
	'schleiden':'sle',
	'saalfeld':'slf',
	'salzlandkreis':'slk',
	'schmölln':'sln',
	'saarlouis':'sls',
	'schlüchtern':'slü',
	'salzungen':'slz',
	'schmalkalden':'sm',
	'schwabmünchen':'smü',
	'schwerin':'sn',
	'soest':'so',
	'schrobenhausen':'sob',
	'schongau':'sog',
	'saale orla kreis':'sok',
	'sömmerda':'söm',
	'sonneberg':'son',
	'speyer':'sp',
	'spremberg':'spb',
	'spree neiße':'spn',
	'straubing':'sr',
	'strausberg':'srb',
	'stadtroda':'sro',
	'steinfurt':'st',
	'starnberg':'sta',
	'sternberg':'stb',
	'stade':'std',
	'staffelstein':'ste',
	'stollberg':'stl',
	'stormarn':'od',
	'siegburg':'su',
	'sulzbach':'sul',
	'südliche weinstraße':'süw',
	'schweinfurt':'sw',
	'schwalbach':'swa',
	'syke':'sy',
	'salzgitter':'sz',
	'schwarzenberg':'szb',
	'tauberbischofsheim':'tbb',
	'torgau delitzsch oschatz':'tdo',
	'tecklenburg':'te',
	'teterow':'tet',
	'teltow fläming':'tf',
	'torgau':'tg',
	'thüringer landtag':'thl',
	'technisches hilfswerk':'thw',
	'tirschenreuth':'tir',
	'torgau oschatz':'to',
	'tölz':'töl',
	'templin':'tp',
	'trier':'tr',
	'traunstein':'ts',
	'tübingen':'tü',
	'tuttlingen':'tut',
	'uckermark':'um',
	'uelzen':'ue',
	'ueckermünde':'uem',
	'uffenheim':'uff',
	'unstrut hainich':'uh',
	'ulm':'ul',
	'unna':'un',
	'usingen':'usi',
	'uslar':'nom',
	'vogtland':'v',
	'vaihingen':'vai',
	'vogelsberg':'vb',
	'vechta':'vec',
	'verden':'ver',
	'vorpommern greifswald':'vg',
	'vilsbiburg':'vib',
	'viersen':'vie',
	'viechtach':'vit',
	'völklingen':'vk',
	'vohenstrauß':'voh',
	'vorpommern rügen':'vr',
	'villingen schwenningen':'vs',
	'wuppertal':'w',
	'waldeck':'wa',
	'warendorf':'waf',
	'wartburgkreis':'wak',
	'wanne':'wan',
	'wattenscheid':'wat',
	'wittenberg':'wb',
	'worbis':'wbs',
	'werdau':'wda',
	'weimar':'we',
	'weilburg':'wel',
	'weiden':'wen',
	'wertingen':'wer',
	'wesel':'wes',
	'wesermarsch':'bra',
	'wolfenbüttel':'wf',
	'wilhelmshaven':'whv',
	'wiesbaden':'wi',
	'wittlich':'wil',
	'wismar':'wis',
	'hansestadt wismar':'hwi',
	'witten':'wit',
	'witzenhausen':'wiz',
	'wittstock':'wk',
	'winsen luhe':'wl',
	'winsen':'wl',
	'wolgast':'wlg',
	'weilheim':'wm',
	'wolmirstedt':'wms',
	'waiblingen':'wn',
	'wendel':'wnd',
	'worms':'wo',
	'wolfsburg':'wob',
	'wolfhagen':'woh',
	'wolfach':'wol',
	'wolfratshausen':'wor',
	'wolfstein':'wos',
	'wernigerode':'wr',
	'waren':'wrn',
	'wasserburg':'ws',
	'weissenfels':'wsf',
	'westerstede':'wst',
	'weisswasser':'wsw',
	'waldshut':'wt',
	'wittlage':'wtl',
	'wittmund':'wtm',
	'würzburg':'wü',
	'weißenburg':'wug',
	'waldmünchen':'wüm',
	'wunsiedel':'wun',
	'wurzen':'wur',
	'westerwald':'ww',
	'wetzlar':'wz',
	'wanzleben':'wzl',
	'bundeswehr':'y',
	'zwickau':'z',
	'zerbst':'ze',
	'zell':'zel',
	'zittau':'zi',
	'ziegenhain':'zig',
	'zschopau':'zp',
	'zeulenroda':'zr',
	'zweibrücken':'zw',
	'zeitz':'zz'
}

"""Stopwords removed in processing"""
exclude = [
    'ist',
    'und',
    'dann',
    'äh',
    'ähm',
    'genau',
    'richtig',
    'punkt',
    'leerzeichen'
]

"""List of German Area Codes that can also be landtag"""
landtag = [
    'h',
    'n',
    'b',
    'bn',
    'bbl',
    'bwl',
    'byl',
    'hb',
    'hel',
    'hh',
    'lsa',
    'lsn',
    'mvl',
    'nl',
    'nrw',
    'rpl',
    'sal',
    'sh',
    'thl'
]

"""Special meanings intepreted in reduce stage"""
specials = {
	".":" ",
	"-":" ",
	"*":" mal ",
	"werden":"verden",
	"färben":"verden"
}