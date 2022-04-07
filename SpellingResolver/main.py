''' SPELLING RESOLVER API '''
import logging
import json
import azure.functions as func

# Import custom modules
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
        convertnumbers = req_body.get("convertnumbers", True)
        convertmultiplications = req_body.get("convertmultiplications", True)
        convertsymbols = req_body.get("convertsymbols", True)
        additional_symbols = req_body.get("additional_symbols", {})
        allowed_symbols= req_body.get("allowed_symbols", [])
        allowed_symbols += ["*"]
        extra_specials = req_body.get("extra_specials", [])
        extra_spelling_alphabet =  req_body.get("extra_spelling_alphabet", None)
    # Snip off everything after first two characters (e.g. en-us -> en)
    lang = lang[:2]
                
    # Process request
    if text:
        try:
            # Create instance of class with locale
            cleaner = resolve.CleanText(locale=lang, 
                                        allowed_symbols=allowed_symbols, 
                                        additional_symbols=additional_symbols, 
                                        extra_specials=extra_specials, 
                                        extra_spelling_alphabet=extra_spelling_alphabet
                                        )
            resolved_text = cleaner.clean(text, convertsymbols=convertsymbols,
                                          convertnumbers=convertnumbers, 
                                          convertmultiplications=convertmultiplications
                                          )
            
            # Extract first characters
            resolved_fc = cleaner.extract_first_character(resolved_text)
        except AttributeError:
            return func.HttpResponse(
             "[ERROR] Received request with invalid or not supported locale.",
             status_code = 400
            )

        # Pack response json
        res = json.dumps(dict(
            original                    = text,
            resolved                    = resolved_text,
            resolved_nospace            = resolved_text.replace(" ", ""),
            first_letters               = resolved_fc,
            first_letters_nospace       = resolved_fc.replace(" ", "")
        ))
        return func.HttpResponse(res, mimetype='application/json')
    else:
        return func.HttpResponse(
             "[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'karl heinrich 33 22'\}",
             status_code = 400
        )
