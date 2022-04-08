![Data Science Toolkit](assets/img/data-science-toolkit-banner.JPG)

# Conversational AI (CAI) Advanced Processing Service - a smart authentication assistent
CAI Advanced Processing Service is a collection of modules, wrapped in multiple APIs that help you to enrich your conversational AI applications in these three fields:
- Validation
- Identification
- Authentication

|                              | Validation                                                                  | Identification                                                                              | Authentication                                                                                                                               |   |
|------------------------------|-----------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|---|
| Definition                   | Entity extraction + data preparation for backend processing                 | Identify a user or asset                                                                    | Identify a user or asset                                                                                                                     |   |
| Example                      | - License plate format is valid<br>- Customer number format is valid        | - License plate is known in backend system<br>- Customer number exists in customer database | - Combination of validated entities from user input which are verified with authentication database                                          |   |
| Technological <br>approaches | - Via pre/post processing functions based on entities (speech + text input) | - Via pre/post processing functions based on entities (speech + text input)                 | - Via Authentication processing functions based on entities (speech input)<br>- Via Oauth/Identity Provider validated login (e.g. AAD, etc.) |   |

### General approach and goals
The main field of use are intelligent applications with text-and speech input, such as chat bots or voice bots.

- Provide a modular and extendable pre/post processing service
- Support more flexible user input options in conversational scenarios
- Enable extended, context-based understanding of user input
- Take a channel-based approach where appropriate
- Process/UX Flow Best Practices for common scenarios

## High Level Architecture
The image and description below define the general architecture of the VIA system with the respective layers, which are separated in _API Layer_, _Module Layer_, _Import Layer_.

![Architecture](assets/img/high_level_architecture.PNG)

__API Layer__
- Contains function-specific Logic (e.g. Business rules like IBAN structure) and the html request and response handling when using an http-triggered function.

__Module Layer__
- Contains re-usable Processing Logic (e.g. Spelling Resolver). A module can be based on phython classes or functions.

__Import Layer__
- Stores data assets required for the processing (e.g. spelling dictionaries, spelling rules, address table). These can also be split by languages, if support for multiple languages is required.

## Tech Stack
The section below describes the teck stacks on which the API collection is built upon.

![Tech Stack](assets/img/tech_stack.PNG)

### Azure Functions
The basis of the API collection is an [Azure Functions](https://docs.microsoft.com/en-us/azure/azure-functions/functions-overview) component, which is a serverless infrastructure type offered on Microsoft Azure. It acts as webservice and can be triggered as REST-API. Basically, it is available in multiple setups such as C#, JavaScript and Python - in this case we use Python and recommend to use the Python 3.8 runtime. The minimum scale level should be either App Service or ideally Premium Plan (instead of Consumtion/serverless, due to low scaleability level, for testing purposes it is sufficient tho). The description to the respective plans can be found [here](https://docs.microsoft.com/en-us/azure/azure-functions/functions-scale). Depending on your scale, a Function, a storage account and an App Service Plan is deployed in your subscription when creating the resource intially. Further, we prefer the __Code__-based version over a custom __Docker__-container (see differences in the Azure Functions documentation).

Our recommended setup can be deployed to your subscription using the following template:


### Python
We recommend using Python >= 3.7. On top of the Python base installation, some further packages are required to serve the purpose of the API collection. These are listed in the `requirements.txt` with the respective version numbers. When deploying the service, it will automatically be used for transferring and installing it.

Other than that, we leverage [spaCy](https://spacy.io) and [Azure Table Storage](https://azure.microsoft.com/de-de/services/storage/tables/) as additional frameworks and components.

## Module Definition
The single modules that are used across multiple APIs are all stored in the subfolder `modules` and will be described below. They may also use another module itself when being accessed by an API.

### `license_plate_recognizer.py`

__Functionality:__
- Extracts, resolves and validates car license plates 
- Easily extendible to support more languages by adding word dictionaries in pre-defined structures

__Dependencies:__
- External services or libraries:
    - [Language Understanding Service (LUIS)](https://luis.ai) for extracting license plates from a string
- Modules
    - `resolve_spelling.py`

### `pattern_matcher.py`

__Functionality:__
- Matching of known string patterns to an input string

__Dependencies:__
- External services or libraries:
    - [spaCy](https://spacy.io), required named entity recognition files/models are stored in the `assets/` folder

### `request_table.py`

__Functionality:__
- Request or push data records from/to an [Azure Table Storage](https://azure.microsoft.com/de-de/services/storage/tables/)

__Dependencies:__
- External services or libraries:
    - [Azure Table Storage](https://azure.microsoft.com/de-de/services/storage/tables/) account on Azure

### `resolve_spelling.py`

__Functionality:__
- Advanced text cleaning
- Resolves spelling alphabets in a string as well as letter/number multiplications

__Dependencies:__
- External services or libraries:
    - for Email validator service it needs [Language Understanding Service (LUIS)](https://luis.ai) for extracting license plates from a string

### `similarity_score.py`

__Functionality:__
- Calculate similarity of an input string compared to a ground truth string
- Provides different levels of similarity, ranging from exact match to [Levenshtein distance](https://blog.paperspace.com/implementing-levenshtein-distance-word-autocomplete-autocorrect/) and [phonetic matching](https://github.com/jamesturk/jellyfish)

__Dependencies:__
- None

## API Documentation
The following section describes the implementation of the services provided as APIs. They can be seen as wrappers around the individual modules described above and each include a component for accepting a request, supplementary business logic around the modules, and returning the results as structured JSON.

<br>

### **Health Check API**

Check Health Status of Azure Function, e.g. used by Application Insights or your monitoring system.

**URL** : `/HealthCheck/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : None

**Data constraints** 
None, no request parameter or bodies are required

**Header constraints**
API key may be passed via header

#### **Success Response**
HTTP-response as text: `Healthcheck executed successfully.`

#### **Error Response**
No response

<br>

### **License Plate Recognizer API**
**URL** : `/LicensePlateRecognizer/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : LUIS app information and keys, see [Get Your Keys](GET_YOUR_KEYS.md) for instructions

**Data constraints** 
```json
{
    "query": "[0-500 chars]",
    "locale": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
}
```

Note that `locale` stands for language, `region` for country. Optional values - if not passed, `de` is set respectively by default.

Example: `de` for German license plate recognizer business logic, `en` if input language is English.

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, correct app information set and LUIS information is valid.

**Code** : `200 OK`

**Content example** : Response will reflect back the input sentence, the extracted entity from LUIS and the resolved license plate.

```json
# Successfully extracted license plate
{
    "id": 1,
    "query": "das ist stuttgart a wie anton dora 22",
    "cplQuery": "das ist S-AD22",
    "cplEntities": [
        {
            "entity": "S-AD22",
            "type": "licensePlate",
            "entitySplit": {
                "fullAdminDistrict": "stuttgart",
                "adminDistrict": "s",
                "letterCombination": "a d",
                "numberCombination": "22",
                "extra": "",
                "ambiguous": false
            }
        }
    ],
    "entities": [
        {
            "type": "platenumber",
            "text": "stuttgart a wie anton dora 22",
            "startIndex": 8,
            "length": 29,
            "score": 0.99148196,
            "modelTypeId": 1,
            "modelType": "Entity Extractor",
            "recognitionSources": [
                "model"
            ]
        }
    ],
    "topScoringIntent": "LicensePlate",
    "logs": [
        "[INFO] - Set params -> region: de, language: de."
    ]
}
```

```json
# If no entity could be extracted 
{
    "id": 1,
    "query": "puh das hab ich gerade nicht zur hand",
    "cplQuery": "puh das hab ich gerade nicht zur hand",
    "cplEntities": [],
    "entities": {},
    "topScoringIntent": "None",
    "logs": [
        "[INFO] - Set params -> region: de, language: de.",
        "[WARNING] - No entity could be extracted"
    ]
}
```

#### **Error Responses**

**Condition** : If provided data is invalid, e.g. locale/region not supported.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Locale not supported
```

<br>

**Condition** : If no query string (utterance from conversation, which may include a license plate) has been passed.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'AB C 1234'\}
```

<br>

### **Spelling Resolver API**
**URL** : `/SpellingResolver/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : None

**Data constraints** 
```json
{
    "query": "[0-500 chars]",
    "locale": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "convertnumbers": "[true/false, default is true]",
    "convertsymbols": "[true/false, default is true]",
    "convertmultiplications": "[true/false, default is true]",
    "additional_symbols": "[a dictionary, example: {"at":"@", "dash": "-"}, default: {}]",
    "allowed_symbols": "[a list, example: ["_", "-", "@", "." ], default: []]",
    "extra_specials": "[a list, example: {'werden':'verden'}, default: {}",
    "extra_spelling_alphabet": "[a dictionary, example: {'daimler':'d'}, default: null]",
    "locale": "de"
}
```

Note that `locale` stands for language. Optional value - if not passed, `de` is set by default.

Example: `de` for German license plate recognizer business logic, `en` if input language is English.

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, correct app information set and LUIS information is valid.

**Code** : `200 OK`

**Content example** : Response will reflect back the input sentence, as well as the resolved content.

```json
{
    "original": "karl heinrich 33 22",
    "resolved": "k h 33 22",
    "resolved_nospace": "kh3322",
    "first_letters": "k h 33 22",
    "first_letters_nospace": "kh3322"
}
```

#### **Error Responses**

**Condition** : If provided data is invalid, e.g. locale/region not supported.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Received request with invalid or not supported locale.
```

<br>

**Condition** : If no query string (utterance from conversation, which may include a license plate) has been passed.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'karl heinrich 33 22'\}
```

<br>

### **VIN Resolver API**
**URL** : `/VINResolver/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : LUIS app information and keys, see [Get Your Keys](GET_YOUR_KEYS.md) for instructions

**Data constraints** 
```json
{
    "query": "[0-500 chars]",
    "expectedwmi": ["WMI","2WM"],
    "locale": "[2-character language code, e.g. de, en, es (cut off after two characters)]"
}
```

Note that `locale` stands for language. Optional values - if not passed, `de` is set respectively by default.

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, correct app information set and LUIS information is valid.

**Code** : `200 OK`

**Content example** : Response will reflect back the input sentence, the extracted entity from LUIS, the information on whether the `WMI` is matched with the `expectedwmi` list, wether the VIN is valid based on validation rules and details on the `VIN`.

```json
# Successfull exvaluation
{
    "query": "das ist 2WMCGH3B2CES5C8T2",
    "vinQuery": "2wmcgh3b2ces5c8t2",
    "validvin": false,
    "expectedwmi": true,
    "vindetails": {
        "region": "north_america",
        "country": "Canada",
        "validvin": false,
        "year": 1982,
        "make": "Western Star",
        "manufacturer": "Western Star",
        "is_pre_2010": true,
        "wmi": "2WM",
        "vds": "CGH3B2",
        "vis": "CES5C8T2",
        "vsn": "S5C8T2",
        "less_than_500_built_per_year": false
    },
    "entities": {
        "vin": [
            "2WMCGH3B2CES5C8T2"
        ],
        "$instance": {
            "vin": [
                {
                    "type": "vin",
                    "text": "2WMCGH3B2CES5C8T2",
                    "startIndex": 8,
                    "length": 17,
                    "score": 0.99916714,
                    "modelTypeId": 1,
                    "modelType": "Entity Extractor",
                    "recognitionSources": [
                        "model"
                    ]
                }
            ]
        }
    },
    "topScoringIntent": "VINResolver"
}
```
"entities" returns LUIS response.

```json
# If no entity could be extracted 
{
    "query": "das ist ",
    "validvin": false,
    "vindetails": {},
    "entities": {},
    "message": [
        "[WARNING] - No entity could be extracted"
    ]
}
```

#### **Error Responses**

**Condition** : If provided data is invalid, e.g. locale not supported.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Locale not supported
```

**Condition** : If no query string (utterance from conversation, which may include a license plate) has been passed.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] Received a blank request. Please pass a value using the defined format. Example: {'query':'das ist 2A4GM684X6R632476', 'expectedwmi': ['WDC'],'locale': 'de'}
```

<br>

### **AtributeValidator API**
**URL** : `/AttributeValidator/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : for email validator, LUIS app information and keys, see [Get Your Keys](GET_YOUR_KEYS.md) for instructions

**Data constraints** 
AtributeValidator API suppurt the following attributes:
- `address`
- `street_in_city`
- `zip`
- `iban`
- `email`
the request body for AtributeValidator is different depending on the attribute.

- For address attribute, the request body is:
```json
{
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "module": "address",
    "values": {
        "zip": "99999",
        "city": "berlin",
        "street": "jordanstrasse",
        "number": 10
    }
}
```
-  For street_in_city attribute, the request body is (Prüft Straße in ZIP):
```json
{
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "module": "street_in_city",
    "values": {
        "zip": "99999",
        "city": "berlin",
        "street": "jordanstrasse",
        "number": 10
    }
}
```
- For zip attribute, the request body is:
```json
{
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "module": "zip",
    "values": {
        "zip": "99999",
        "city": "duesseldorf "
    }
}
```

- For iban attribute, the request body is (Prüft IBAN):
```json
{
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "module": "iban",
    "values": {
        "iban": "DE12345678901234567890"
    }
}
```
- For email attribute, the request body is (Prüft E-Mail):
```json
{
    "region": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "locale": "[2-character language code, e.g. de, en, es (cut off after two characters)]",
    "module": "email",
    "values": {
        "email": "max.mustermann@example.com"
    }
}
```

Note that `locale` stands for language. Optional values - if not passed, `de` is set respectively by default.

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, correct app information set and LUIS information is valid.

**Code** : `200 OK`

**Content example** : 

- For address validation, the response will be:
```json
{
    "error": false,
    "city_is_valid": true,
    "zip": "10115",
    "city": "Berlin",
    "street_is_valid": true,
    "street_has_options": false,
    "street": "Bergstr.",
    "number": 10
}
```

- For street_in_city validation, the response will be:
```json
{
    "error": false,
    "is_valid": true,
    "has_options": false,
    "street": "Bergstr.",
    "number": "10"
}
```

- For zip validation, the response will be:
```json
{
    "error": false,
    "is_valid": true,
    "zip": "10115",
    "city": "Berlin"
}
```

- For iban validation, the response will be:
```json
{
    "error": false,
    "is_valid": true,
    "iban": "DE02120300000000202051"
}
```

- For email validation, the response will be:
```json
{
    "query": "Normen.meyer@daimler.com",
    "e-mail recognized": true,
    "e-mail": "normen.meyer@daimler.com",
    "entities": {
        "company_name": [
            "Normen.meyer@daimler.com"
        ],
        "email_spelled": [
            "Normen.meyer@daimler.com"
        ],
        "email": [
            "normen.meyer@daimler.com"
        ],
        "domain": [
            "daimler.com"
        ],
        "$instance": {
            "company_name": [
                {
                    "type": "company_name",
                    "text": "Normen.meyer@daimler.com",
                    "startIndex": 0,
                    "length": 24,
                    "score": 0.46415412,
                    "modelTypeId": 1,
                    "modelType": "Entity Extractor",
                    "recognitionSources": [
                        "model"
                    ]
                }
            ],
            "email_spelled": [
                {
                    "type": "email_spelled",
                    "text": "Normen.meyer@daimler.com",
                    "startIndex": 0,
                    "length": 24,
                    "score": 0.76997584,
                    "modelTypeId": 1,
                    "modelType": "Entity Extractor",
                    "recognitionSources": [
                        "model"
                    ]
                }
            ],
            "email": [
                {
                    "type": "builtin.email",
                    "text": "Normen.meyer@daimler.com",
                    "startIndex": 0,
                    "length": 24,
                    "modelTypeId": 2,
                    "modelType": "Prebuilt Entity Extractor",
                    "recognitionSources": [
                        "model"
                    ]
                }
            ],
            "domain": [
                {
                    "type": "domain",
                    "text": "daimler.com",
                    "startIndex": 13,
                    "length": 11,
                    "score": 0.9899364,
                    "modelTypeId": 1,
                    "modelType": "Entity Extractor",
                    "recognitionSources": [
                        "model"
                    ]
                }
            ]
        }
    },
    "topScoringIntent": "GetEntities"
}

"entities" returns LUIS response.

```json
# If no entity could be extracted 
{
    "query": "mein email",
    "e-mail recognized": false,
    "e-mail": "",
    "entities": {},
    "topScoringIntent": "GetEntities"
}
```

#### **Error Responses**

**Condition** : If provided data is invalid, e.g. region not supported.

**Code** : `200 OK`

**Content example** :

```
[ERROR] Locale not supported
{
    "error": true,
    "is_valid": false,
    "error_message": "Locale US not supported."
}
```

**Condition** : If no query string (utterance from conversation, which may include a license plate) has been passed.

**Code** : `200 BAD REQUEST`

**Content example** :

```
{
    "error": false,
    "error_message": "Submitted IBAN is not a valid IBAN for DE with length of 22",
    "is_valid": false
}
```

<br>

### Table Requestor API
**URL** : `/TableRequestor/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : Table storage connection string, see [Get Your Keys](GET_YOUR_KEYS.md) for instructions

**Data constraints** 
The request structure in the `params` section depends on the structure of your data in the table storage. The entire, unfiltered data set can be requested by only passing the `PartitionKey` in the request's `params` section.

```json
{
    "table": {
        "name": "[0-100 chars]"
    },
    "params": {
        "PartitionKey": "[name of partition-key]",
        "Lastname": "[example, depends on the column names in your table storage]"
    }
}
```

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, successful table storage authentication and valid table name.

**Code** : `200 OK`

**Content example** : Response will reflect back an array of results that match to the filter parameters.

```json
{
    "table": {
        "name": "CustomerData"
    },
    "params": {
        "PartitionKey": "CustomerData",
        "LastName": "Nadella"
    }
}
```

#### **Error Responses**

**Condition** : If connection data is not valid or table does not exist.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] - Connection to table storage could not be established, please verify the connection string and table name.
```

<br>

**Condition** : If empty or invalid request body has been passed.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] - Pass a table and set of variables you want to look up in the customer data base, for example:
 {'table': {'name': 'UserData'}, 'params': {'PartitionKey': 'UserData'}}.
```

<br>

### Authentication API
**URL** : `/Authentication/`

**Method** : `GET` / `POST`

**Auth required** : Only deployed version, if authentication is activated (strongly recommended) 

**Permissions required** : Table storage connection string, see [Get Your Keys](GET_YOUR_KEYS.md) for instructions

**Data constraints** 
The request structure in the `attributes` section depends on the structure of your data in the table storage and the manifest definition for the authentication. The `method` field controls whether we use levenstein and/or phonethic matching. The `verbose` setting allows for a more detailed debugging output but should be set to `false` in productive implementation.

```json
{
    "attributes":
        {
            "Firstname": "Satya",
            "Lastname": "Nadella",
            "Birthdate": "1900-02-03",
            "Id": "1234"
        },
    "method": 4,
    "verbose": true,
    "region": "de",
    "locale": "de"
}
```

**Header constraints**
API key may be passed via header

#### **Success Responses**

**Condition** : Data provided, successful table storage authentication and valid table name.

**Code** : `200 OK`

**Content example** : Response will reflect back an array of results that match to the filter parameters.

```json
{
    "result": {
        "authenticated": false
    },
    "verbose": {
        "attributes": {
            "Birthdate": false,
            "Firstname": true,
            "Lastname": true
        },
        "method": 4
    }
}
```

#### **Error Responses**

**Condition** : If connection data is not valid or table does not exist.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] - Connection to table storage could not be established, please verify the connection string and table name.
```

<br>

**Condition** : If empty or invalid request body has been passed.

**Code** : `400 BAD REQUEST`

**Content example** :

```
[ERROR] - Pass a table and set of variables you want to look up in the customer data base, for example:
 {'table': {'name': 'UserData'}, 'params': {'PartitionKey': 'UserData'}}.
```

## Operations
The section below describes the frameworks to be installed locally before you can get started testing, debugging and deploying the service.

### Local Installation
First, you have to install/set up following components:
1. PowerShell
    - [Azure Command Line Interface (CLI)](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli), command line tools for Azure using PowerShell
    - [Azure Functions Core Tools](https://docs.microsoft.com/de-de/azure/azure-functions/functions-run-local?tabs=windows%2Ccsharp%2Cbash#v2), download for your local runtime environment, e.g. as `.exe` -> _v3.x: Windows 64-Bit_
    - A restart is highly recommended or even required after installing these components, otherwise you might face some hiccups.
2. Python >= 3.7
    - We recommend you to use the official version from the [Python website](https://www.python.org/downloads/release/python-379/), make sure you install `pip` and set Python as `path` variable during the installation process.
    
3. Postman
    - Framework for API testing, download it [here](https://www.postman.com/downloads/) and install it.

### Testing and Debugging
1. Get your code from GitHub: `git clone https://github.com/microsoft/looky` and `cd` into the environment
1. Create a virtual environment: `python –m venv .venv`
1. Activate the virtual environment: `source .venv/bin/activate` (Linux) or `.venv\Scripts\activate` (Windows), type `deactivate` to disable it again if needed
1. Install the requirements: `pip install -r requirements.txt`
1. Set your keys (only for local development and debugging) in the `config.ini` (they are needed for the LUIS request)
1. For debugging and local testing, open a separate PowerShell window and execute `func start --verbose` in the root folder of the function. This enables you to do code changes during runtime without shutting down the function completely when there is an issue
1. Use [Postman](https://www.postman.com/downloads/) for testing the endpoints using the localhost request of this [collection](assets/postman_collection/looky_localhost.postman_collection.json)

### Deployment to Azure
1. Open your PowerShell
1. Activate your environment, if you haven't before: <br>
`source .venv/bin/activate` (Linux) or `.venv/Scripts/activate` (Windows)
1. Login to your Azure Account: `az login` (a browser window will open, where you may have to log on Azure)
1. Execute the command below:<br> 
`func azure functionapp publish [insert your function name] --remote build`
1. Wait until the deployment is finished
1. (optional, only has to be done for initial deployment OR when settings are updated) Execute following command:<br>
`az webapp config appsettings set -g [insert name of resource group] -n [insert your function name] --settings @appsettings.json`
1. Use [Postman](https://www.postman.com/downloads/) for testing the endpoints with the [collections](assets/postman-collection/cai-advanced-processing-service.postman_collection.json)

## Contributing
This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks
This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft 
trademarks or logos is subject to and must follow 
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
