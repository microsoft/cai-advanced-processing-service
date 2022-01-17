from Levenshtein import distance as levenshtein_distance

try:
    from __app__.shared import Logging as log
except Exception as e:
    from shared import Logging as log

def get_matching_streets(user_street: str, streetsInZipArea):

    result = []

    if user_street in streetsInZipArea:
        log.logger.info(f"[INFO] Found direct match")
        result.append(user_street)     
    else:
        log.logger.info(f"[INFO] No direct match found")
        street_length = len(user_street)

        # Set Levenshtein distance: For every 6 characters in street name increase distance by 1
        LEV_DISTANCE_INIT = 2
        LEV_DISTANCE = LEV_DISTANCE_INIT + len(user_street)//6
        log.logger.info("[INFO] Using max. Levenshtein Distance of {}".format(LEV_DISTANCE))

        for i in range(LEV_DISTANCE):
            selectedStreets = [street for street in streetsInZipArea if len(street) >= street_length - LEV_DISTANCE & len(street) <= street_length + LEV_DISTANCE]

            for street in selectedStreets:
                dist = levenshtein_distance(user_street.lower(), street.lower())
                if dist <= i and dist >= 0:
                    result.append(street)
            if result:
                log.logger.info("[INFO] Found match using Levenshtein Distance of {}".format(i))
                break
    
    return result