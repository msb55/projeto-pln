# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six

# EVENT TABLE FIELDS
ACTION = 'ACTION'
AGENT = 'AGENT'
PATIENT = 'PATIENT'
BENEFICIATY = 'BENEFICIATY'
TENSE = 'TENSE'
LOC_PREP = 'LOC_PREP'
LOC_TARGET = 'LOC_TARGET'
INSTRUMENT = 'INSTRUMENT'
ADVERB = 'ADVERB'
ADJECTIVE = 'ADJECTIVE'
ADP_AGENTE = 'ADP_AGENTE'
ADP_PATIENT = 'ADP_PATIENT'
ADP_LOC = 'ADP_LOC'

INVALID = 'INVALID'
NOT_FIND = 'NOT_FIND'

encodeType = [('á', 'Ã¡'),('à', 'Ã\\xa0'),('â', 'Ã¢'),('ã', 'Ã£'),('é', 'Ã©'),('è', 'Ã¨'),('ê', 'Ãª'),('í', 'Ã\\xad'),('ó', 'Ã³'),('ô', 'Ã´'),('õ', 'Ãµ'),('ú', 'Ãº'),('ç', 'Ã§'),('Á', 'Ã\\x81'),('À', 'Ã\\x80'),('Â', 'Ã\\x82'),('Ã', 'Ã\\x83'),('É', 'Ã\\x89'),('È', 'Ã\\x88'),('Í', 'Ã\\x8d'),('Ó', 'Ã\\x93'),('Ô', 'Ã\\x94'),('Õ', 'Ã\\x95'),('Ú', 'Ã\\x9a'),('Ç', 'Ã\\x87')]

def get_syntax(text):
    """Detects syntax in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')
        print(text)
    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='pt')

    # Detects syntax in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    tokens = client.analyze_syntax(document)

    return tokens

def get_entities(text):
    """Detects syntax in the text."""
    client = language.LanguageServiceClient()

    if isinstance(text, six.binary_type):
        text = text.decode('utf-8')

    # Instantiates a plain text document.
    document = types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT,
        language='pt')

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(document).entities

    return entities

def find_entity(entities, name):
    for entitie in entities:
        if clear_str(entitie.name.lower()) == clear_str(name.lower()):
            return entitie.type
    
    return NOT_FIND

query = {}

def terceiro_excluido():
    global query
    if not AGENT in query:
        return AGENT
    if not PATIENT in query:
        return PATIENT
    if not BENEFICIATY in query:
        return BENEFICIATY
    return INVALID

def clear_str(text):
    find = list(filter(lambda x: x[1] in text, encodeType))
    if len(find) == 0:
        return text
    return find[0][0]

def witch_adp(name):
    global query
    if AGENT in query:
        if query[AGENT] == clear_str(name):
            return ADP_AGENTE
    if PATIENT in query:
        if query[PATIENT] == clear_str(name):
            return ADP_PATIENT
    if LOC_TARGET in query:
        if query[LOC_TARGET] == clear_str(name):
            return ADP_LOC
    
    return INVALID

def semantic(text):
    global query

    syntax = get_syntax(text)
    entities = get_entities(text)
    
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
               'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')
    
    query = {}

    for i, token in enumerate(syntax.tokens):
        
        if pos_tag[token.part_of_speech.tag] == "NOUN":
            
            i_parent = token.dependency_edge.head_token_index
            parent = syntax.tokens[i_parent]
            
            if pos_tag[parent.part_of_speech.tag] == "VERB" and i_parent > i:
                query[AGENT] = clear_str(token.text.content)

            elif pos_tag[parent.part_of_speech.tag] == "VERB" and i_parent < i:
                query[PATIENT] = clear_str(token.text.content)

            elif pos_tag[parent.part_of_speech.tag] == "ADP":
                i_grandparent = parent.dependency_edge.head_token_index
                grandparent = syntax.tokens[i_grandparent]

                if pos_tag[grandparent.part_of_speech.tag] == "NOUN":
                    query[witch_adp(grandparent.text.content)] = clear_str(token.text.content)

                elif parent.text.content.lower() == "com":
                    if entity_type[find_entity(entities, token.text.content)] == "PERSON":
                        pessoa = terceiro_excluido()                   
                        query[pessoa] = clear_str(token.text.content)
                    else:
                        query[INSTRUMENT] = clear_str(token.text.content)

                elif parent.text.content.lower() in ("na","no","da","do"):
                    query[LOC_TARGET] = clear_str(token.text.content)
                    query[LOC_PREP] = clear_str(parent.text.content)

                elif parent.text.content.lower() in ("de","para","ao","a","à"):                    
                    if entity_type[find_entity(entities, token.text.content)] == "PERSON":
                        pessoa = terceiro_excluido()
                        query[pessoa] = clear_str(token.text.content)
                    else:
                        query[LOC_TARGET] = clear_str(token.text.content)
                        query[LOC_PREP] = clear_str(parent.text.content)

        elif pos_tag[token.part_of_speech.tag] == "VERB":
            if token.dependency_edge.label == 54:
                query[ACTION] = clear_str(token.lemma)

        elif pos_tag[token.part_of_speech.tag] == "ADV":
            query[ADVERB] = clear_str(token.text.content)

        elif pos_tag[token.part_of_speech.tag] == "ADJ":
            query[ADJECTIVE] = clear_str(token.text.content)

    print(query)

# test = ["João come rapidamente","João come graciosamente","João beijou Maria no parque","João beijou Maria debaixo da mesa","João comeu sorvete com uma colher","João comeu galinha com um garfo","João dormiu na cama com um travesseiro","João dormiu na cama com Maria","João gosta de cachorros","Maria gosta de gatos","João dormiu debaixo de uma árvore","João infelizmente deu seus gatos para Maria","Maria comeu o sorvete","João comeu sorvete rapidamente no parque com uma colher"]
test = ["João dormiu na cama com Maria","João gosta de cachorros","Maria gosta de gatos","João infelizmente deu seus gatos para Maria"]
for i in test:
    print(i)
    semantic(i)