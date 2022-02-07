import logging
import json
import spacy
import logging
import spacy
from spacy.matcher import Matcher
import azure.functions as func

# Load phrase matcher
nlp = spacy.load('en_core_web_sm')
matcher = Matcher(nlp.vocab)

# Add match ID "HelloWorld" with no callback and one pattern
pattern = [{"TEXT": {"REGEX": "[0-9A-Za-z]{3}[,.]{1}[0-9A-Za-z]{3}[,.]{1}[0-9A-Za-z]{3}$"}}]
matcher.add("SACHNR", [pattern])

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        documents = req_body.get('values')

    # Load phrase matcher
    nlp = spacy.load('en_core_web_sm')
    matcher = Matcher(nlp.vocab)

    # Add match ID "HelloWorld" with no callback and one pattern
    pattern = [{"TEXT": {"REGEX": "[0-9A-Za-z]{3}[,.]{1}[0-9A-Za-z]{3}[,.]{1}[0-9A-Za-z]{3}$"}}]
    matcher.add("SACHNR", [pattern])

    if len(documents) > 0:
        res = []
        for _, entry in enumerate(documents):
            doc = nlp(entry["data"]["text"])
            matches = matcher(doc)
            if len(matches) > 0:
                for match_id, start, end in matches:
                    string_id = nlp.vocab.strings[match_id] # Get string representation
                    span = doc[start:end]  # The matched span
                    logging.warning(f'{match_id}, {string_id}, {start}, {end}, {span.text}')
                    res.append(dict(recordId=entry["recordId"], data=dict(match_id=match_id, string_id=string_id, start=start, end=end, text=span.text), warnings=list()))
        return func.HttpResponse(json.dumps(dict(values=res)), mimetype="application/json")
    else:
        return func.HttpResponse(json.dumps(dict(values=[])), mimetype="application/json")