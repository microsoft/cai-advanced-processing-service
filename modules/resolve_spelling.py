''' SPELLING RESOLVER MODULE '''
import re
import logging
import string
import sys
sys.path.append('./')

# Define logger
logger = logging.getLogger(__name__)

# Import custom modules and helpers
from assets import characters

class CleanText(object):
    def __init__(self, locale, 
                 allowed_symbols, 
                 additional_symbols, 
                 extra_specials=dict(), 
                 extra_spelling_alphabet=None
                 ):
        
        self.allowed_symbols = allowed_symbols
        self.additional_symbols = additional_symbols
        # Create lookup table for accellerated cleaning
        self.table = str.maketrans({key: None for key in string.punctuation if key not in allowed_symbols})        

        # TODO: return a False if the locale is not supported at all

        # Import dictionaires
        if extra_spelling_alphabet is None:
            extra_spelling_alphabet = characters.extra_spelling_alphabet.get(locale)
        self.dict_char = characters.alphabet.get(locale)
        ## adding additional spelling alphabet to default dict
        self.dict_char.update(extra_spelling_alphabet)
        
        self.dict_symbols = characters.symbols.get(locale)
        ## adding additional symbols to default dict
        self.dict_symbols.update(additional_symbols)
        
        self.dict_spec = characters.specials.get(locale)
        ## adding additional special replacement to default dict
        self.dict_spec.update(extra_specials)
        
        self.list_excl = characters.exclude.get(locale)

        # Collect characters from assets
        self.numbers_dict = characters.numbers_dict.get(locale)
        self.numbers_repeat = characters.numbers_repeat.get(locale)

        # Replacement mapping table
        self.replacements = str.maketrans(dict.fromkeys(''.join(['.', ',', '-', '!', '?', ' ']), ''))
        
    def clean(self, text, convertsymbols=False, convertnumbers=True, ignorealphabet=True, convertmultiplications=True):
        if convertsymbols:
        # converting spelling symbels to the coresponding signs and keep the allowed symbols
            text = self.clean_symbols(text)
            
        # Reduce string (replacing specials)
        text = self.reduce_string(text)
            
        # Resolve spelling alphabet
        if ignorealphabet:
            text = self.resolve_spelling_alphabet(text)
        
        # Resolve numbers as words
        if convertnumbers:
            text = self.resolve_numbers_as_words(text) 
        
        # Clean numbers (3*3 = 333)
        if convertmultiplications:
            text = self.clean_repeats(text)
            
        return text
        
    def clean_symbols(self, text):
        ''' 
        this function do the following:
        1) convert symbols spelling words to corresponding sign
        2) removed all symbols (including punctuation) except those in the allowed_symbols list
        '''
        text = ' '.join([str(self.dict_symbols.get(i, i)) for i in text.lower().translate(self.table).split() if i not in self.list_excl])
        logger.warning(f'[SPELLING - SYMBOLS] - {text}')
        return text
    
    def resolve_spelling_alphabet(self, text):
        '''Reduce License Plate'''
        # Reduce spelling alphabet
        text = ' '.join([str(self.dict_char.get(i, i)) for i in text.translate(self.table).split() if i not in self.list_excl])
        logger.warning(f'[SPELLING - ALPHABET] - {text}')
        return text
    
    def reduce_string(self, text):
        # Reduce special characters
        text = ' '.join([str(self.dict_spec.get(i, i)) for i in text.translate(self.table).split() if i not in self.list_excl])
        #text = text.replace("*", " * ") # TODO
        logger.warning(f'[REDUCE STRING] - {text}')
        return text

    def resolve_numbers_as_words(self, text):
        # Resolve numbers as words to numbers
        text = ' '.join([str(self.numbers_dict.get(i, i)) for i in text.translate(self.table).split() if i not in self.list_excl])
        logger.warning(f'[NUMBERS AS WORDS] - {text}')
        return text

    def extract_first_character(self, text, sep=" "):
        '''Extract first character of every word'''
        return sep.join([token[0] if not token.isdigit() else token for token in text.split(' ')])

    def validate_reduce(self, phrase, letter, start, stop):
        """Validate single letter word comparisons"""
        if len(letter) == 1:
            if letter != phrase[start:stop].strip().split()[2][0]:
                letter = phrase[start:stop].strip().split()[2][0]
        return letter

    def clean_repeats(self, phrase):
        '''Replaces spelling by numbers
        Transform, e.g., "My number is: AK dash six 8 4*9 3 double 9 3." to 6899993993
        '''
        
        # Replace general "wie"-comparisons
        while True:
            match = re.search(r'(\s|^)([a-z]{1,3}) (wie|f??r|von|wir|for|like) \w+', phrase)
            logger.info(f'[COMPARISON] - {phrase} -> {match}')
            if match:
                start = match.span(0)[0]
                stop = match.span(0)[1]
                letter = self.validate_reduce(phrase, phrase[start:stop].strip().split()[0], start, stop)
                phrase = phrase[:start] + ' ' + letter + phrase[stop:]
            else:
                break

        # Replace letter multiplication
        for repeat in self.numbers_repeat.keys():
            while True:
                match = re.search(r'(' + repeat  + r' [a-z]\b)', phrase)
                logger.info(f'[LETTER MULTIPLICATION] - {phrase} ->{match}')
                if match:
                    start = match.span(0)[0]
                    stop = match.span(0)[1]
                    letter = self.numbers_repeat[repeat] * phrase[start:stop][-1]
                    phrase = phrase[:start] + letter + phrase[stop:]
                else:
                    break

        # Replace number multiplication based on word
        for repeat in self.numbers_repeat.keys():
            while True:
                phrase = phrase.replace(" die ", " ") # TODO REMOVE/FIX THIS
                match = re.search(r'(' + repeat + r'( die)? [0-9]{1,2}\b)', phrase)
                logger.info(f'[NUMBER MULTI WORD] - {phrase} -> {match}')
                if match:
                    start = match.span(0)[0]
                    stop = match.span(0)[1]
                    letter = self.numbers_repeat[repeat] * phrase[start + len(repeat):stop].strip()
                    phrase = phrase[:start] + letter + phrase[stop:]
                else:
                    break

        # Replace number multiplication based on number
        while True:
            match = re.search(r'([1-9]( |)(mal|times|\*)( die)?( |)[0-9]\b)', phrase)
            logger.info(f'[NUMBER MULTI NR] - {phrase} -> {match}')
            if match:
                start = match.span(0)[0]
                stop = match.span(0)[1]
                number = int(phrase[start:stop][0:1]) * phrase[start:stop][-1:].strip()
                phrase = phrase[:start] + number + phrase[stop:]
            else:
                break

        # Replace letter multiplication
        while True:
            match = re.search(r'([1-9]( |)(mal|times|\*)( die)? [a-z])', phrase)
            if match:
                start = match.span(0)[0]
                stop = match.span(0)[1]
                char = int(phrase[start:stop][0:1]) * phrase[start:stop][-2:].strip()
                phrase = phrase[:start] + char + phrase[stop:]
            else:
                break
                
        return phrase
    
    def clean_attribute(self, text):
        return str(text).lower().translate(self.replacements).replace(" ", "")

def main(locale, phrase):
    # Create instance of class
    cleaner = CleanText(locale)
    # Remove punctuation
    _text = cleaner.remove_punctuation(phrase)
    logger.warning(f'Removed punctuation -> {_text}')
    # Resolve spelling alphabet
    _text = cleaner.resolve_spelling_alphabet(_text)
    logger.warning(f'Resolved spelling alphabet -> {_text}')
    # Resolve numbers as words
    _text = cleaner.resolve_numbers_as_words(_text)
    logger.warning(f'Resolved numbers as words punctuation -> {_text}')
    # Clean numbers (3*3 = 333)
    _text = cleaner.clean_repeats(_text)
    logger.warning(f'Resolved repeats -> {_text}')
    # Extract first characters
    _text = cleaner.extract_first_character(_text)
    logger.warning(f'Extracted first characters -> {_text}')

if __name__ == '__main__':
    main('en', 'anton, dora 3 * two double d')