# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import six
import operations_database

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
ADP_AGENT = 'ADP_AGENT'
ADP_PATIENT = 'ADP_PATIENT'
ADP_LOC = 'ADP_LOC'

INVALID = 'INVALID'
NOT_FIND = 'NOT_FIND'

ANSWER = 'ANSWER'

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
            return ADP_AGENT
    if PATIENT in query:
        if query[PATIENT] == clear_str(name):
            return ADP_PATIENT
    if LOC_TARGET in query:
        if query[LOC_TARGET] == clear_str(name):
            return ADP_LOC
    
    return INVALID

def semantic(text):
    global query

    # pergunta
    if text[-1] == "?":
        print("É uma pergunta.", text)
        make_query(text, True)
        answer_type = 0
        # answer_yesOrNo = 0
        # answer_isPerson = 1
        # answer_isLocal = 2
        # answer_isModo = 3
        # answer_isInstrument = 4
        # answer_isUndefined = 5
        # answer_isParaQuem = 6

        if text.lower().startswith("quem") or text.lower().startswith("com quem") or text.lower().startswith("de quem"):
            answer_type = 1
        elif text.lower().startswith("onde") or text.lower().startswith("para onde"):
            answer_type = 2
        elif text.lower().startswith("como"):
            answer_type = 3
        elif text.lower().startswith("o que") or text.lower().startswith("do que"):
            answer_type = 5
        elif text.lower().startswith("com"):
            answer_type = 4
        elif text.lower().startswith("para quem"):
            answer_type = 6
        else:
            answer_type = 0
        
        query[ANSWER] = answer_type
        print("resposta:",operations_database.answer_processing(query))
    else:
        print("É uma afirmação.", text)
        make_query(text, False)
        operations_database.insert_event(query)   

def make_query(text, isanswer):
    global query

    syntax = get_syntax(text)
    entities = get_entities(text)
    
    pos_tag = ('UNKNOWN', 'ADJ', 'ADP', 'ADV', 'CONJ', 'DET', 'NOUN', 'NUM',
               'PRON', 'PRT', 'PUNCT', 'VERB', 'X', 'AFFIX')

    entity_type = ('UNKNOWN', 'PERSON', 'LOCATION', 'ORGANIZATION',
                   'EVENT', 'WORK_OF_ART', 'CONSUMER_GOOD', 'OTHER')

    query = {}
                   
    for i, token in enumerate(syntax.tokens):                
        # afirmacao
        if pos_tag[token.part_of_speech.tag] == "NOUN": 
            
            i_parent = token.dependency_edge.head_token_index
            parent = syntax.tokens[i_parent]
            
            if pos_tag[parent.part_of_speech.tag] == "VERB" and i_parent > i:
                if token.lemma != '':
                    query[AGENT] = clear_str(token.lemma)
                else:
                    query[AGENT] = clear_str(token.text.content)

            elif pos_tag[parent.part_of_speech.tag] == "VERB" and i_parent < i:
                query[PATIENT] = clear_str(token.text.content)

            elif pos_tag[parent.part_of_speech.tag] == "VERB":
                pessoa = terceiro_excluido()
                if token.lemma != '':
                    query[pessoa] = clear_str(token.lemma)
                else:
                    query[pessoa] = clear_str(token.text.content)
            
            elif pos_tag[parent.part_of_speech.tag] == "PRON" and isanswer:
                pessoa = terceiro_excluido()
                if token.lemma != '':
                    query[pessoa] = clear_str(token.lemma)
                else:
                    query[pessoa] = clear_str(token.text.content)

            elif pos_tag[parent.part_of_speech.tag] == "ADP":
                i_grandparent = parent.dependency_edge.head_token_index
                grandparent = syntax.tokens[i_grandparent]

                if pos_tag[grandparent.part_of_speech.tag] == "NOUN":
                    if token.lemma != '':
                        query[witch_adp(grandparent.text.content)] = clear_str(token.lemma)
                    else:
                        query[witch_adp(grandparent.text.content)] = clear_str(token.text.content)

                elif parent.text.content.lower() == "com":
                    if entity_type[find_entity(entities, token.text.content)] == "PERSON":
                        pessoa = terceiro_excluido()
                        if token.lemma != '':
                            query[pessoa] = clear_str(token.lemma)
                        else:
                            query[pessoa] = clear_str(token.text.content)
                    else:
                        if token.lemma != '':
                            query[INSTRUMENT] = clear_str(token.lemma)
                        else:
                            query[INSTRUMENT] = clear_str(token.text.content)

                elif parent.text.content.lower() in ("na","no","da","do","em"):
                    query[LOC_TARGET] = clear_str(token.text.content)
                    query[LOC_PREP] = clear_str(parent.text.content)

                elif parent.text.content.lower() in ("de","para","ao","a","à"):
                    pessoa = terceiro_excluido()
                    if token.lemma != '':
                        query[pessoa] = clear_str(token.lemma)
                    else:
                        query[pessoa] = clear_str(token.text.content)

        elif pos_tag[token.part_of_speech.tag] == "VERB":
            if token.dependency_edge.label == 54:
                query[ACTION] = clear_str(token.lemma)
            elif isanswer and not ACTION in query:
                query[ACTION] = clear_str(token.lemma)
            else:
                label = terceiro_excluido()
                if token.lemma != '':
                    query[label] = clear_str(token.lemma)
                else:
                    query[label] = clear_str(token.text.content)

        elif pos_tag[token.part_of_speech.tag] == "ADV":
            query[ADVERB] = clear_str(token.text.content)

        elif pos_tag[token.part_of_speech.tag] == "ADJ":
            query[ADJECTIVE] = clear_str(token.text.content)
    print(query)

# test = ["João come rapidamente","João come graciosamente","João beijou Maria no parque","João beijou Maria debaixo da mesa","João comeu sorvete com uma colher","João comeu galinha com um garfo","João dormiu na cama com um travesseiro","João dormiu na cama com Maria","João gosta de cachorros","Maria gosta de gatos","João dormiu debaixo de uma árvore","João infelizmente deu seus gatos para Maria","Maria comeu o sorvete","João comeu sorvete rapidamente no parque com uma colher"]
# test = ["João dormiu na cama com Maria","João gosta de cachorros","Maria gosta de gatos","João infelizmente deu seus gatos para Maria"]


# test = ["João doou para Maria","João doou para o orfanato", "João viajou para Recife","João beijou Maria no parque","João gosta de cachorros","João comeu sorvete com uma colher","João infelizmente deu seus gatos para Maria", "Maria gosta de gatos"]
# test = ["João come rapidamente","João come graciosamente", "João beijou Maria debaixo da mesa","João comeu galinha com um garfo","João dormiu na cama com um travesseiro","João dormiu na cama com Maria","João dormiu debaixo de uma árvore", "Maria comeu o sorvete", "João comeu sorvete rapidamente no parque com uma colher"]

# test = ["João come rapidamente","João come graciosamente","João beijou Maria no parque","João beijou Maria debaixo da mesa","João comeu sorvete com uma colher","João comeu galinha com um garfo","João dormiu na cama com um travesseiro","João dormiu na cama com Maria","João gosta de cachorros","Maria gosta de gatos","João dormiu debaixo de uma árvore","João infelizmente deu seus gatos para Maria","Maria comeu o sorvete","João comeu sorvete rapidamente no parque com uma colher","João foi para a casa de Maria","Roberto odeia João","Link comprou presentes para Zelda","Vitor ficou triste com a nota","Vitor ficou triste com Maria","João chorou antes de dormir ","Yone estuda na Unijorge","Maria adora cerveja ","Maria comprou pães na padaria","Ananda foi à feira","Leonardo é um estudante ","Marcos voltou para Irecê","Leonardo dormiu tarde","Lucas digita rápido","Bruno ama filmes da Marvel","Maria está com sede","João ganhou uma bola","Leonardo amou a nova série da Netlix","João viajou para Recife","Renata gosta de Alex","Pablo é um critico ","Hans é um ótimo professor","Jailson foi dormir tarde","Marcela ofereceu carona para Marcos na rodovia ","Leonardo odeia barulhos ","Jailson foi dormir tarde","Marcela ofereceu carona para Marcos na rodovia ","Leonardo odeia barulhos ","Naruto ama Sasuke","Vitor gosta de carnaval ","João comprou um celular para Maria","Leonardo odeia atrasos","Marcos dormiu tranquilamente "]
# test = ["O pai de Marcos está feliz","Marcos voltou para casa","Leonardo voltou para casa"]
# test = ["Maria gosta de gatos?","João chorou antes de dormir?","Maria está com sede?","Jailson foi dormir tarde?","Leonardo voltou para casa?","João comeu sorvete com uma colher?","João foi para a casa de Maria?","Leonardo é um estudante?","Pablo é um critico?","João comprou um celular para Maria?","Jailson gosta de sorvete?","Leonardo ama crianças?","Marcos mora em Recife?","Marcos é um estudante?","João gosta de gatos?","João dormiu na cama com uma bicicleta?","João comeu sorvete com uma colher?","Marcos comeu sorvete com uma colher?","Marcela ama João?","Vitor dorme bem?"]
test = ["Como joão come?","Com quem João dormiu na cama?","Com o que João dormiu?","o que João comeu?","o que Maria adora?","Com o que João comeu a galinha?","Quem Roberto odeia?","Onde Yone estuda?","Como Lucas digita?","O que João ganhou?","De quem Renata gosta?","Onde Marcela ofereceu carona para Marcos?","Para quem Marcela ofereceu carona?","Para quem Marcela ofereceu carona na rua?","Quem Naturo ama?","Quem voltou para casa?","O que Bruno ama?","Onde João dormiu?","Para quem Link comprou presentes?","O que Link comprou para Zelda?","Do que João gosta?","Do que Vitor gosta?","O que Leonardo odeia?","Como Maria está?","Onde Ananda foi?","O que João comprou para Roberto?","O que Marcos ganhou de presente?","O que Leonardo ama em Recife?","Com quem Vitor ficou triste?","Hans é um ótimo professor?"]
for i in test:
    # print(i)
    semantic(i)

# semantic("Com quem João dormiu?")

# while True:
#     print("Pode dizer :)")
#     sentenca = input()
#     if sentenca.lower() == "sair":
#         break
#     resposta = semantic(sentenca)
#     print(resposta)
#     print("")