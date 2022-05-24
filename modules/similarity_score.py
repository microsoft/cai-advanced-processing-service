import logging
import jellyfish
import numpy as np

def levenshtein(s1, s2):
    '''Levenshtein distance between two strings'''
    m = np.zeros((len(s2) + 1, len(s1) + 1))
    m[:, 0] = np.arange(len(s2) + 1)
    m[0, :] = np.arange(len(s1) + 1)
    for i in range(1, m.shape[0]):
        for j in range(1, m.shape[1]):
            if s2[i - 1] == s1[j - 1]:
                m[i, j] = min(m[i - 1, j - 1], m[i, j - 1] + 1, m[i-1, j] + 1)
            else:
                m[i, j] = min(m[i - 1, j - 1] + 1, m[i, j - 1] + 1, m[i - 1, j] + 1)
    return m[-1, -1]

def phonetic_match(input1, input2, jaro_d, damerau_d):
    '''Phonetic matching of input strings'''
    # Set distances if not passed
    if jaro_d is None:
        jaro_d = 0.9
    if damerau_d is None:
        damerau_d = 1
    logging.info(f'Processing Jaro distance with max distance of {jaro_d}, Damerau distance with max distance of {damerau_d}.')

    # Preprocess and define steps
    input1.replace(" ", "")
    input2.replace(" ", "")
    input1_soundex = jellyfish.soundex(input1)
    input1_nysiis = jellyfish.nysiis(input1)
    input1_match_rating_codex = jellyfish.match_rating_codex(input1)
    input2_soundex = jellyfish.soundex(input2)
    input2_nysiis = jellyfish.nysiis(input2)
    input2_match_rating_codex = jellyfish.match_rating_codex(input2)
    
    jaro_soundex = jellyfish.jaro_distance(input1_soundex, input2_soundex)
    logging.info(f"Phontetic match - jaro_soundex: {jaro_soundex}")
    if jaro_soundex >= jaro_d:      
        return True
    
    jaro_nysiis = jellyfish.jaro_distance(input1_nysiis, input2_nysiis)
    logging.info(f"Phontetic match - jaro_nysiis: {jaro_nysiis}")
    if jaro_nysiis >= jaro_d:
        return True
    
    jaro_match_rating_codex = jellyfish.jaro_distance(input1_match_rating_codex, input2_match_rating_codex)
    logging.info(f"Phontetic match - jaro_match_rating_codex: {jaro_nysiis}")
    if jaro_match_rating_codex >= jaro_d:
        return True
    
    damerau_soundex = jellyfish.damerau_levenshtein_distance(input1_soundex, input2_soundex)
    logging.info(f"Phontetic match - damerau_soundex: {damerau_soundex}")
    if damerau_soundex <= damerau_d:
        return True
    
    damerau_nysiis = jellyfish.damerau_levenshtein_distance(input1_nysiis, input2_nysiis)
    logging.info(f"Phontetic match - damerau_nysiis: {damerau_nysiis}")
    if jellyfish.damerau_levenshtein_distance(input1_nysiis, input2_nysiis) <= damerau_d:
        return True
    
    damerau_match_rating_codex = jellyfish.damerau_levenshtein_distance(input1_match_rating_codex, input2_match_rating_codex)
    logging.info(f"Phontetic match - damerau__match_rating_codex: {damerau_match_rating_codex}")
    if damerau_match_rating_codex <= damerau_d:
        return True 
    return False

'''CHECKS'''
def check_item_exact(token_input, token_truth):
    if token_input == token_truth:
        return True
    else:
        return False

def check_item_dist(token_input, token_truth, d):
    '''Levenshtein distance'''
    if d is None:
        d = 2
    logging.info(f'Processing Levenshtein distance with max distance of {d}.')
    if levenshtein(token_input, token_truth) > d:
        return False
    else:
        return True

def check_item_phonetic(token_input, token_truth, jaro_d, damerau_d):
    '''Phonetic matching'''
    if not phonetic_match(token_input, token_truth, jaro_d, damerau_d):
        return False
    else:
        return True

'''APPLIED CHECKS'''
def apply_check_exact(customer_data, cleaned, manifest=None):
    '''Apply check for exact match'''
    return {key:(value.lower() == cleaned[key]) for key, value in customer_data.items()}

def apply_check_levensthein(customer_data, cleaned, manifest):
    '''Apply check for Levenshtein distance'''
    return {key:check_item_dist(cleaned[key], value.lower(), manifest[key].get('max_distance_levenshtein')) if not manifest[key]['exact_match'] else (value.lower() == cleaned[key]) for key, value in customer_data.items()}

def apply_check_phonetic(customer_data, cleaned, manifest):
    '''Apply check for phonetic matching'''
    return {key:check_item_phonetic(cleaned[key], value.lower(), manifest[key].get('max_distance_jaro'), manifest[key].get('max_distance_damerau')) if not manifest[key]['exact_match'] else (value.lower() == cleaned[key]) for key, value in customer_data.items()}
