import database
import sqlite3

def insert_object(obj):
    # conectando...
    conn = sqlite3.connect(database.DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    # inserindo dados na tabela
    cursor.execute("""
    INSERT INTO object (NAME)
    VALUES (?)
    """,(obj[database.NAME],))

    lastid = cursor.lastrowid

    # gravando no bd
    conn.commit()
    conn.close()

    return lastid

def insert_event(evento):
    # conectando...
    conn = sqlite3.connect(database.DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    dependencies = get_dependencies({database.AGENT: evento[database.AGENT],database.PATIENT: evento[database.PATIENT],database.BENEFICIATY: evento[database.BENEFICIATY],database.LOC_TARGET: evento[database.LOC_TARGET],database.INSTRUMENT: evento[database.INSTRUMENT]})

    columns = ()
    fields = ()
    values = ()
    for key, value in dependencies.items():
        if value > 0:
            columns += (key,)
            fields += ('?',)
            values += (value,)

    # inserindo dados na tabela
    cursor.execute("""
    INSERT INTO event (ACTION, TENSE, LOC_PREP, ADVERB, ADJECTIVE, ADP_AGENT, ADP_PATIENT, ADP_LOC, """+','.join(columns)+""")
    VALUES (?,?,?,?,?,?,?,?,"""+','.join(fields)+""")
    """,(evento[database.ACTION], evento[database.TENSE], evento[database.LOC_PREP], evento[database.ADVERB], evento[database.ADJECTIVE], evento[database.ADP_AGENT], evento[database.ADP_PATIENT], evento[database.ADP_LOC]) + values)

    print("OK")

    # gravando no bd
    conn.commit()
    conn.close()

def get_dependencies(dependencies):
    # conectando...
    conn = sqlite3.connect(database.DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    ids = {}
    for key, value in dependencies.items():
        if value != '':
            # busca id -> insere em ids[column]

            # buscando ID
            cursor.execute("""
            SELECT id FROM object WHERE """+database.NAME+""" = ?
            """,(value,))

            retorno =  cursor.fetchall()
            if len(retorno) == 0:
                ids[key] = insert_object({database.NAME:value})
            else:          
                ids[key] = retorno[0][0]
        else:
            ids[key] = 0
    
    print(ids)
    conn.close()

    return ids

# init_db()
# insert_object({NAME:'Ananda', TYPE:''})
# get_all("lic")
# get_dependencies({'AGENT':"Marcos", 'PATIENT': "Vitor", 'BENEFICIATY': ''})
inserir = {'ACTION': 'dormir', 'TENSE': 'passado', 'LOC_PREP':'de', 'ADVERB':'debaixo', 'ADJECTIVE':'', 'ADP_AGENT':'', 'ADP_PATIENT':'', 'ADP_LOC':'','AGENT':'João','PATIENT':'','BENEFICIATY':'','LOC_TARGET':'árvore','INSTRUMENT':''}

insert_event(inserir)