''' SPELLING RESOLVER API '''
import logging
import json
import azure.functions as func

# Import custom modules
try:
    from __app__.modules import resolve_spelling as resolve
except Exception as e:
    logging.info("[INFO] Helper: Using local imports.")
    from modules import resolve_spelling as resolve

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Receive request
    try:
        text = req.params.get("query")
    except Exception as e:
        logging.error(e)
        pass
    else:
        req_body = req.get_json()
        text = req_body.get("query")
        lang = req_body.get("locale")
        if not lang:
            lang = "de"
    # Snip off everything after first two characters (e.g. en-us -> en)
    lang = lang[:2]
                
    # Process request
    if text:
        try:
            # Create instance of class with locale
            cleaner = resolve.CleanText(lang)
            # General preprocessing
            resolved =  cleaner.clean_repeats( # Clean numbers (3*3 = 333)
                            cleaner.resolve_numbers_as_words( # Resolve numbers as words
                                cleaner.resolve_spelling_alphabet( # Resolve spelling alphabet
                                    cleaner.remove_punctuation(text) # Remove Punctuation
                                )))
            # Extract first characters
            resolved_fc = cleaner.extract_first_character(resolved)
        except AttributeError:
            return func.HttpResponse(
             "[ERROR] Received request with invalid or not supported locale.",
             status_code = 400
            )

        # Pack response json
        res = json.dumps(dict(
            original                    = text,
            resolved                    = resolved,
            resolved_nospace            = resolved.replace(" ", ""),
            first_letters               = resolved_fc,
            first_letters_nospace       = resolved_fc.replace(" ", "")
        ))
        return func.HttpResponse(res, mimetype='application/json')
    else:
        return func.HttpResponse(
             "[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'karl heinrich 33 22'\}",
             status_code = 400
        )
