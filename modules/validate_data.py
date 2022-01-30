from assets.constants import LEV_DISTANCE_INIT
from modules.similarity_score import levenshtein
import logging

def get_matching_streets(user_street: str, streets_in_zip_area: list):
    '''Get matching streets considering zip area'''
    result = []

    if user_street in streets_in_zip_area:
        logging.info(f"[INFO] Found direct match")
        result.append(user_street)     
    else:
        logging.info(f"[INFO] No direct match found")
        street_length = len(user_street)

        # Set Levenshtein distance: For every 6 characters in street name increase distance by 1
        LEV_DISTANCE = LEV_DISTANCE_INIT + len(user_street) // 6
        logging.info(f"[INFO] Using maximum Levenshtein distance of {LEV_DISTANCE}")

        for i in range(LEV_DISTANCE):
            selectedStreets = [street for street in streets_in_zip_area if len(street) >= street_length - LEV_DISTANCE & len(street) <= street_length + LEV_DISTANCE]

            for street in selectedStreets:
                dist = levenshtein(user_street.lower(), street.lower())
                if dist <= i and dist >= 0:
                    result.append(street)
            if result:
                logging.info(f"[INFO] Found match using Levenshtein distance of {i}")
                break
    
    return result