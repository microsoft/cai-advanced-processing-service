''' MODULE FOR Vin resolver '''
import logging
import re
import azure.functions as func
import sys

# Define logger
logger = logging.getLogger(__name__)

from assets import characters
from modules import resolve_spelling as resolve

class VinResolver(object):
    def __init__(self, lang="de", clean=True):
        # Set language for VIN resolver
        if lang in ["de", "en"]:
            self.cleaner = resolve.CleanText(lang)

        else:
            self.matcher = None
    
        # Import dictionaries
        self.list_excl = characters.exclude
    
    def clean(self, phrase):
        """Cleaning steps for extracted phrase, with area detection in between"""
        # Reduce string
        phrase = self.cleaner.reduce_string(phrase)
        # Further clean string
        phrase = self.cleaner.clean_repeats(
                    self.cleaner.resolve_spelling_alphabet(
                        self.cleaner.resolve_numbers_as_words(phrase)))
        return phrase


def main(entity, lang="de"):
    # Create instance of class with locale
    matcher = VinResolver(lang, lang).matcher

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