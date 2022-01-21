import string
import re
from edit_distance import SequenceMatcher
from typing import List, Dict, Tuple, Union, DefaultDict
from modules import similarity_score as simscore

from assets import character as ch
from assets import exclude as exc
from assets import specials as sp
from assets import digits as dg
from assets import cities as ct 

# Table to efficiently remove punctuations
table: Dict = str.maketrans({key: None for key in string.punctuation if key != '-'})

# Lookup objects
dict_char: Dict[str, str] = ch.obj
dict_spec: Dict[str, str] = sp.obj
list_excl: Dict[str, str] = exc.obj
list_digits: Dict[str, str] = dg.obj
dict_months: Dict[str, str] = sp.months
dict_day_ord: Dict[str, str] = sp.ordinal_number_mapping
dict_zip_codes: DefaultDict[str, List[str]] = ct.zip_mapping
dict_cities: DefaultDict[str, List[str]] = ct.city_mapping

##############################
##### Input Processing
##############################

def pp_normalize_street_name(phrase: Union[None, str, List[str]]) -> Union[str, None]:
    if phrase is None:
        return None

    # if phrase is not a list convert it to list
    if not isinstance(phrase, list):
        phrase = phrase.split(' ')

    result = []
    # separate weg, allee, strasse etc. from the rest of the word
    # hauptstrasse -> haupt strasse
    for p in phrase:
        match = re.search(r'(str)|(straße)|(strasse)|(platz)|(allee)|(promenade)|(gasse)|(ring)|(platz)|(weg)\s', p.lower())
        if match:
            start=match.span(0)[0]
            # skip if match starts in the beginning
            if start > 0:
                p = p[0:start] + ' ' + p[start:]
        result.append(p)
    
    return ' '.join(result).lower().replace('straße', 'str').replace('strasse', 'str')



def match_zip_to_city(zip_code: str, city_phrase: str, matching_threshold: float =0.6) -> Union[str, None]:
    if zip_code is None:
        return None

    if zip_code in dict_zip_codes:
        city_list = dict_zip_codes[zip_code]

        # return the city that matches the city phrase closest
        best_match = get_closest_sequence_match(city_phrase, city_list, matching_threshold)
        return best_match

    else:
        return None

def get_city_name_list_for_zip_code(zip_code: str) -> List[str]:
    """Given a zip code return all cities that belong to that zip code

    Args:
        zip_code (str): City zip code

    Returns:
        List[str]: List of city names and Landkreise
    """    

    if not zip_code in dict_zip_codes:
        return []
    
    return dict_zip_codes[zip_code]

def get_closest_sequence_match(input_term: str, option_list: List[str], matching_threshold: float) -> Union[str, None]:
    ratios = []
    lev_dist = []
    for option in option_list:
        sm = SequenceMatcher(option.lower().replace(' ', ''), input_term.lower().replace(' ', ''))
        ratios.append(sm.ratio())
        ld = simscore.levenshtein(option.lower().replace(' ', ''), input_term.lower().replace(' ', ''))
        lev_dist.append(ld)

    best_match_ratio = max(ratios)
    min_lev_dist = min(lev_dist)

    # there was no city name that satisfies our matching threshold
    if best_match_ratio < matching_threshold:
        if min_lev_dist <= 2:
            return option_list[lev_dist.index(min_lev_dist)]
        return None

    best_match_idx = ratios.index(best_match_ratio)
    return option_list[best_match_idx]
    
def pp_insurance_number(query: str) -> str:
    return pp_remove_chars(query)

def pp_remove_chars(query: str) -> str:
    return ''.join(c for c in query if c.isdigit())

##############################
##### General PP
##############################

def get_edit_distance(q1: str, q2: str) -> float:
    sm = SequenceMatcher(q1.lower(), q2.lower())
    return sm.ratio()

def validate_reduce(phrase: Union[str, None], letter: str, start: int, stop: int) -> str:
    if phrase is None:
        return ''
    """Validate single letter word comparisons"""
    if len(letter) == 1:
        if letter != phrase[start:stop].strip().split()[2][0]:
            letter = phrase[start:stop].strip().split()[2][0]
    return letter

def reduce_ordinals(phrase: Union[str, None], strip: bool=False) -> str:
    if phrase is None:
        return ''
    for key in dict_day_ord.keys():
        phrase = phrase.replace(key, dict_day_ord[key])
        if strip:
            phrase = phrase.replace(key.strip(), dict_day_ord[key])

    return phrase

def reduce_months(phrase: Union[str, None], strip: bool=False) -> str:
    if phrase is None:
        return ''
    for key in dict_months.keys():
        phrase = phrase.replace(key, dict_months[key])
        if strip:
            phrase = phrase.replace(key.strip(), dict_months[key])
    return phrase

def reduce_dates(phrase: Union[str, None]) -> str:
    if phrase is None:
        return ''
    
    # reduce date specials
    phrase = reduce_ordinals(phrase)
    phrase = reduce_months(phrase)
    return phrase

def reduce_query(phrase: Union[str, None]) -> str:
    """Reduce Query"""
    if phrase is None:
        return ''

    # Reduce special characters
    for key in dict_spec.keys():
        phrase = phrase.replace(key, dict_spec[key])

    phrase = reduce_dates(phrase)

    # remove stopwords
    phrase = ' '.join([str(dict_char.get(i, i)) for i in phrase.translate(table).split() if i not in list_excl])

    # replace spoken single digits
    phrase_r = []
    for word in phrase.split(' '):
        if word.lower() in list_digits:
            phrase_r.append(list_digits[word.lower()])
        else:
            phrase_r.append(word)
    phrase = ' '.join(phrase_r)

    # Replace general "wie"-comparisons
    while True:
        match = re.search(r'(\s|^)([a-z]{1,3}) (wie|für|von|wir) \w+', phrase)
        if match:
            start = match.span(0)[0]
            stop = match.span(0)[1]
            letter = validate_reduce(phrase, phrase[start:stop].strip().split()[0], start, stop)
            phrase = phrase[:start] + ' ' + letter + phrase[stop:]
        else:
            break

    # Replace letter multiplication
    while True:
        match = re.search(r'(doppel [a-z])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            letter = 2 * phrase[start:stop][-1]
            phrase = phrase[:start] + letter + phrase[stop:]
        else:
            break

    # Replace number multiplication
    while True:
        match = re.search(r'(doppel [0-9])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            letter = 2 * phrase[start:stop][-1]
            phrase = phrase[:start] + letter + phrase[stop:]
        else:
            break

    # Replace number multiplication
    while True:
        match = re.search(r'([1-9] mal( die)? [0-9])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            number = int(phrase[start:stop][0:1]) * phrase[start:stop][-2:].strip()
            phrase = phrase[:start] + number + phrase[stop:]
        else:
            break

    # Replace letter multiplication
    while True:
        match = re.search(r'([1-9] mal( die)? [a-z])', phrase)
        if match:
            start=match.span(0)[0]
            stop=match.span(0)[1]
            char = int(phrase[start:stop][0:1]) * phrase[start:stop][-2:].strip()
            phrase = phrase[:start] + char + phrase[stop:]
        else:
            break

    # Remove noise from reduced
    phrase = phrase.replace("  ", " ")

    return phrase

def split_street_and_number(phrase: str) -> Tuple[str, str]:
    # Letter number split
    entity_reduced = list(phrase)
    entity_str = []
    i = 0
    for e in entity_reduced:
        if e.isdigit():
            break
        entity_str.append(e)
        i += 1
    entity_num = ''.join([n for n in entity_reduced[len(entity_str):]])
    entity_str = ''.join(entity_str)
    return entity_str, entity_num


def split_numbers_pos(phrase: Union[str, None]) -> Tuple[str, str]:
    if phrase is None:
        return '', ''

    # Letter number split
    entity_reduced = list(phrase)
    entity_str = []
    for e in entity_reduced:
        if e.isdigit():
            break
        entity_str.append(e)
    entity_num = ''.join([n for n in entity_reduced[len(entity_str):] if n.isdigit()])
    entity_str = ''.join(entity_str)
    return entity_str.strip(), entity_num

def split_numbers_naive(phrase: Union[str, None]) -> Tuple[str, str]:
    if phrase is None:
        return '', ''
    
    # Letter number split
    entity_reduced = list(phrase)
    entity_str = []
    entity_int = []
    for e in entity_reduced:
        if e.isdigit():
            entity_int.append(e)
        else:
            entity_str.append(e)
    str_result = ''.join(entity_str)
    int_result = ''.join(entity_int)
    return str_result.strip(), int_result.strip()


def prepend_chars(s: str, target_length: int, char: str) -> str:
    s_len = len(s)
    if s_len < target_length:
        diff = target_length - s_len
        return char * diff + s  
    return s