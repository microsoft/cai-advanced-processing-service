''' GERMAN MODULE FOR LICENSE PLATE RECOGNIZER '''
import logging
import re
import azure.functions as func
import sys

# Define logger
logger = logging.getLogger(__name__)

try:
    from __app__.assets import characters
    from __app__.modules import resolve_spelling as resolve
except Exception as e:
    logger.info('[INFO] Helper: Using local imports.')
    sys.path.append('./')
    from assets import characters
    from modules import resolve_spelling as resolve

class LicensePlateRecognizer(object):
    def __init__(self, region="de", locale="de", clean=True):
        # Set region for license plate recognition
        if region == "de":
            self.cleaner = resolve.CleanText(locale)
            self.matcher = self.DE_LP(self.cleaner)

        elif region == "nl":
            self.matcher = self.NL_LP()

        else:
            self.matcher = None

    class UK_LP(object):
        def __init__(self):
            self.dict_area = {}

        def get_lp(self):
            return None

        def format_lp(self):
            return None

    class NL_LP(object):
        def __init__(self):
            self.dict_area = {}

        def get_lp(self):
            return None

        def format_lp(self):
            return None

    class DE_LP(object):
        """License Plate Recognizer for German License Plates - Supports input in different languages"""
        def __init__(self, cleaner):
            # Import main classes
            self.cleaner = cleaner

            # Import dictionaries
            self.dict_area = characters.areas
            self.dict_ambg = characters.ambiguous
            self.list_excl = characters.exclude
            self.list_landtag = characters.landtag
        
        def clean(self, phrase):
            """Cleaning steps for extracted phrase, with area detection in between"""
            # Reduce string
            phrase = self.cleaner.reduce_string(phrase)
            # Detect area (we have to do this before further cleaning due to ngram area)
            phrase, ambig = self.detect_area(phrase)
            # Further clean string
            phrase = self.cleaner.clean_repeats(
                        self.cleaner.resolve_spelling_alphabet(
                            self.cleaner.resolve_numbers_as_words(phrase)))
            return phrase, ambig

        def detect_area(self, phrase):
            """Detect area name in phrase"""
            # Search for area code
            for key in self.dict_area:
                if (' ' + key + ' ') in (' ' + phrase + ' '):
                    match  = re.search(key, phrase)
                    start  = match.span(0)[0]
                    stop   = match.span(0)[1]
                    phrase = phrase[start:]
                    logger.info(f'[DETECT AREA] {phrase} -> {match}')
                    break
            
            # Detect ambiguous license plate area
            for key in self.dict_ambg:
                if (' ' + key + ' ') in (' ' + phrase + ' '):
                    ambig = True
                    break
                else:
                    ambig = False

            return phrase, ambig

        def get_lp(self, query, entity):
            """Orchestrate license plate formatting and validation"""
            # Translate and clean input
            string, number, extra, reduced = self.reduce_area(entity) 

            # Check for LP type
            if (len(string) < 1) or (string[0] == 'y'):
                ## Treat as special LP
                lp, split, valid = self.get_lp_special(entity, extra, reduced)
            else:
                ## Treat as standard LP
                lp, split, valid = self.get_lp_standard(entity, string, number, extra)

            return entity, lp, split, valid

        def reduce_area(self, phrase):
            """Extract number/area splits from phrase"""
            # Letter number split
            entity_reduced = list(phrase)
            entity_str = []
            for e in entity_reduced:
                if e.isdigit():
                    break
                entity_str.append(e)
            entity_num = ''.join([n for n in entity_reduced[len(entity_str):] if n.isdigit()])
            entity_str = (''.join(entity_str)).split()
            
            # Extract electric and histroical vehicle LPs
            entity_extra = ''
            if entity_reduced[-1] in ['e', 'h', 'c']:
                entity_extra = entity_reduced[-1]

            # Check for incomplete LP
            if entity_num == '':
                entity_extra = ''
            
            # Remove noise from reduced
            phrase = phrase.replace(" ", "")

            return entity_str, entity_num, entity_extra, phrase

        def area_lookup(self, area):
            """Lookup full area name from area code"""
            try:
                area_full = next(k for k, v in self.dict_area.items() if v == area)
            except Exception as e:
                area_full = 'FALSE'
            return area_full

        def check_area_ngram(self, entity_split, n):
            """Search for ngram areas"""
            if n == 1:
                area_split = entity_split
                letter_replace = None
            else:
                area_split = [' '.join(entity_split[:n])]
                letter_replace = ' '.join(area_split)
            area = ' '.join([str(self.dict_area.get(i, i)) for i in area_split if i not in self.list_excl and i in self.dict_area]) 
            return area_split, letter_replace, area

        def multi_area_lookup(self, entity, length):
            """Lookup for multiple area options"""
            # Extract area options
            areas_full = []
            letters = []
            areas = []
            if length < 4:
                _areas = [entity[:1], entity[:2], entity[:3]]
            elif length == 4:
                _areas = [entity[:2], entity[:3]]
            elif length == 5:
                _areas = [entity[:3]]
            else:
                areas_full = ['UNKNOWN']
                _areas = areas
                letters = [entity]
            
            # Lookup areas
            for a in _areas:
                _area_full = self.area_lookup(a)
                if _area_full != 'FALSE':
                    areas.append(a)
                    areas_full.append(_area_full)
                    letters.append(entity[len(a):])
                
            if len(areas_full) == 0:
                areas_full.append('FALSE')
                letters.append(entity)
            
            return letters, areas, areas_full

        def get_lp_area(self, entity, entity_split):
            """Extract area code"""
            # N-gram Area Lookup
            area = []
            ngram = 4
            while len(area) == 0 and ngram != 0:
                ## Fetch areas with n-gram
                area_split, letter_replace, area = self.check_area_ngram(entity_split, ngram)
                ## Special treatment for unigram
                if len(area) != 0 and ngram == 1:
                    area_len = len(area.split(" ")) - 1
                    if area_len > 0:
                        area = area.split(" ")[0]
                        entity_split = entity_split[area_len:]
                        area_split = area_split[area_len:]
                ngram -= 1
            entity_join = ''.join(entity_split)
            entity_len = len(entity_join)
            
            # Area post processing & validation
            if len(area) > 0:
                area_full = ' '.join([i for i in area_split if i not in self.list_excl and i in self.dict_area])
                if letter_replace is not None:
                    letter = str(' '.join(entity_split)).replace(letter_replace, '')
                    letter = ' '.join([i for i in letter.split() if i not in self.list_excl])
                else:
                    letter = ' '.join([i for i in entity_split if i not in self.list_excl and i not in self.dict_area])
            
            elif '-' in entity_split:
                area = entity_join.split('-')[0]
                area_full = self.area_lookup(area)
                if area_full == 'FALSE':
                    area = ''
                    letter = entity_join
                else:
                    letter = entity_join.replace(area,'',1).replace("-","")

            else:
                ## Area detection for multiple areas
                letter, area, area_full = self.multi_area_lookup(entity_join, entity_len)

            return letter, area, area_full

        def format_lp(self, area, letter, number, extra='', lp_type='standard'):
            """Merge and format license plate"""
            if lp_type == 'diplomat':
                return f'{area}-{letter}-{number}{extra}'.replace(' ','').upper()
            elif lp_type == 'bundeswehr':
                return f'{area}-{letter}{extra}'.replace(' ','').upper()
            else:
                return f'{area}-{letter}{number}{extra}'.replace(' ','').upper()

        def validate_lp(self, lp, lp_type='standard'):
            """Final validation of formatted license plate"""

            # Check LP type and set regex
            if lp_type == 'diplomat':
                regex = r'^0\-[0-9]{1,2}\-[0-9]{1,3}(E|H|C)?$'
            elif lp_type == 'bundeswehr':
                regex = r'^Y\-[0-9]{1,6}(E|H|C)?$'
            elif lp_type == 'bp':
                regex = r'^BP\-[0-9]{1,5}(E|H|C)?$'
            elif lp_type in self.list_landtag:
                regex = r'^[A-ZÄÖÜ]{1,3}\-(([A-Z]{1,2}[0-9]{1,4})|([0-9]{1,6}))(E|H|C)?$'
            else:
                regex = r'^[A-ZÄÖÜ]{1,3}\-[A-Z]{1,2}[0-9]{1,4}(E|H|C)?$'
            
            # Match regex
            if re.match(regex, lp):
                valid = True
            else:
                valid = False
            return valid

        def get_lp_standard(self, entity, string, number, extra):
            """Handling of standard (common) license plates"""
            # Get LP Area
            letter, area, area_full = self.get_lp_area(entity, string)
            # Delete duplicates in letter combination
            if isinstance(letter, str):
                if len(letter.replace(" ", "")) == 4: 
                    letter = letter.replace(" ", "")
                    if letter[0] == letter[2] and letter[1] == letter[3]:
                        letter = letter[0] + letter[1]

            # Prepare for next steps
            if isinstance(area, list):
                number = [number for n in area]
            else:
                letter, area, area_full, number = [letter], [area], [area_full], [number]
            
            # Output
            _lp = []
            _split = []
            _valid = []
            for a, l, n, af in zip(area, letter, number, area_full):

                # Format LP
                lp_formatted = self.format_lp(a, l, n, extra)
                _lp.append(lp_formatted)

                # Validate LP
                v = self.validate_lp(lp_formatted, lp_type=a)
                _valid.append(v)

                if not v:
                    if len(l) > 2:
                        l = ''
                    if len(n) > 4:
                        n = ''
                
                _split.append(dict(
                    area_full   =   af,
                    area        =   a,
                    letter      =   l,
                    number      =   n, 
                    extra       =   extra
                    ))
            
            # Only pass valid LPs
            lp = []
            split = []
            valid = []
            if any(_valid) != all(_valid):
                for _v, _l, _s in zip(_valid, _lp, _split):
                    if _v:
                        lp.append(_l)
                        split.append(_s)
                        valid.append(_v)
            else:
                lp = _lp
                split = _split
                valid = _valid

            return lp, split, all(valid)

        def get_lp_special(self, entity, extra, reduced):
            """Handling of special license plate types, such as diplomat"""
            # Check for missing connection
            if reduced[1] != '-':
                reduced = reduced[0] + '-' + reduced[1:]
                print(reduced)
            
            third = ''
            if reduced[0] == '0':
                lp_type = 'diplomat'
                try:
                    first = reduced[0]
                    second = reduced.split('-')[1]
                    third = ''.join([n for n in reduced.split('-')[2] if n.isdigit()])
                except IndexError:
                    first = reduced[0]
                    second = ''.join([n for n in reduced.split('-')[1] if n.isdigit()])

            elif reduced[0] == 'y':
                lp_type = 'bundeswehr'
                first = reduced[0]
                second = ''.join([n for n in reduced[1:] if n.isdigit()])
            
            # Create LP
            lp = [self.format_lp(first, second, third, extra, lp_type)]

            # Validate LP
            valid = self.validate_lp(lp[0], lp_type)

            # Create split
            split = [dict(
                area_full = lp_type,
                area = first,
                letter = '',
                number = second + third,
                extra = extra
            )]

            return lp, split, valid

        def format_output(self, query, lp, split, valid, start, end, ambig):
            """Format the request response of the Azure Function"""
            out = []
            cpl_query = query
            for l, s in zip(lp, split):
                lps = dict()
                if not valid:
                    lps['entity'] = ''
                else:
                    lps['entity'] = l
                    cpl_query = cpl_query[:start] + lps.get('entity') + cpl_query[end+1:]                        
                lps['type'] = 'licensePlate'
                lps['entitySplit'] = dict(
                    fullAdminDistrict = s.get('area_full'),
                    adminDistrict = s.get('area'),
                    letterCombination = s.get('letter'),
                    numberCombination = s.get('number'),
                    extra = s.get('extra'),
                    ambiguous = ambig
                )
                out.append(lps)
            return out, cpl_query

def main(entity, region="de", lang="de"):
    # Create instance of class with locale
    matcher = LicensePlateRecognizer(region, lang).matcher

    # Recognize license plates
    entity, ambig   =   matcher.clean(entity)
    raw, lp, split, valid    =   matcher.get_lp(entity.lower(), entity)
    
    # Format response            
    cpl_entities, cpl_query = matcher.format_output(entity.lower(), lp, split, valid, 0, -0, ambig)

    # Return LP
    return cpl_entities, cpl_query

if __name__ == "__main__":
    cpl_entities, cpl_query = main("stuttgart anton dora 22")
    logging.warning(cpl_entities, cpl_query)