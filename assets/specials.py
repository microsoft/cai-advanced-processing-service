from typing import Dict, List

"""Special meanings interpreted in reduce stage"""

obj: Dict[str, str] = {
	".":" ",
	"*":" mal ",
	" bindestrich ": " ",
	" binde strich ": " ",
	"-": " ",
	" komma ": " ",
	"einmal":"1 mal",
	"zweimal":"2 mal",
	"dreimal":"3 mal",
	"viermal":"4 mal",
	"fünfmal":"5 mal",
	"sechsmal":"6 mal",
	"siebenmal":"7 mal",
	"achtmal":"8 mal",
	"neunmal":"9 mal",
	"zehnmal":"10 mal"
}

# date specials

months: Dict[str, str] = {
	'Januar': '01',
	'Jänner': '01',
	'Februar': '02',
	'März': '03',
	'April': '04',
	'Mai': '05',
	'Juni': '06',
	'Juli': '07',
	'August': '08',
	'September': '09',
	'Oktober': '10',
	'November': '11',
	'Dezember': '12',
	'januar': '01',
	'jänner': '01',
	'februar': '02',
	'märz': '03',
	'april': '04',
	'mai': '05',
	'juni': '06',
	'juli': '07',
	'august': '08',
	'september': '09',
	'oktober': '10',
	'november': '11',
	'dezember': '12'
}


__base_ordinal_numbers: Dict[str, str] = {
	" erste": " 1.",
	" zweite": " 2.",
	" dritte": " 3.",
	" vierte": " 4.",
	" fünfte": " 5.",
	" sechste": " 6.",
	" siebte": " 7.",
	" achte": " 8.",
	" neunte": " 9.",
	" zehnte": " 10.",
	" elfte": " 11.",
	" zwölfte": " 12.",
	" dreizehnte": " 13.",
	" vierzehnte": " 14.",
	" fünfzehnte": " 15.",
	" sechzehnte": " 16.",
	" siebzehnte": " 17.",
	" achtzehnte": " 18.",
	" neunzehnte": " 19.",
	" zwanzigste": " 20.",
	" einundzwanzigste": " 21.",
	" zweiundzwanzigste": " 22.",
	" dreiundzwanzigste": " 23.",
	" vierundzwanzigste": " 24.",
	" fünfundzwanzigste": " 25.",
	" sechsundzwanzigste": " 26.",
	" siebenundzwanzigste": " 27.",
	" achtundzwanzigste": " 28.",
	" neunundzwanzigste": " 29.",
	" dreißigste": " 30.",
	" einunddreißigste": " 31."
}

# add additional declinations
ordinal_number_mapping: Dict[str, str] = {}
declination_forms: List[str] = ['r', 'n', 'm']
for key, value in __base_ordinal_numbers.items():
	ordinal_number_mapping[key + ' '] = value + ' '

	for suffix in declination_forms:
		ordinal_number_mapping[key + suffix + ' '] = value + ' '