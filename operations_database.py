import database
import sqlite3

ANSWER = 'ANSWER'

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

    dependencies = {}
    for key, value in evento.items():
        if key in [database.AGENT, database.PATIENT, database.BENEFICIATY, database.LOC_TARGET, database.INSTRUMENT]:
            dependencies[key] = value

    dependencies = get_dependencies(dependencies)

    for key, value in dependencies.items():
        evento[key] = value

    columns = ()
    fields = ()
    values = ()
    for key, value in evento.items():
        columns += (key,)
        fields += ('?',)
        values += (value,)

    # inserindo dados na tabela
    cursor.execute("""INSERT INTO event ("""+','.join(columns)+""") VALUES ("""+','.join(fields)+""")""",values)

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
    
    conn.close()

    return ids

def answer_processing(query):
    # conectando...
    conn = sqlite3.connect(database.DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    answer_type = query[ANSWER]

    dependencies = {}
    for key, value in query.items():
        if key in [database.AGENT, database.PATIENT, database.BENEFICIATY, database.LOC_TARGET, database.INSTRUMENT]:
            dependencies[key] = value

    print(dependencies)
    dependencies = get_dependencies(dependencies)
    print(dependencies)

    for key, value in dependencies.items():
        query[key] = value
    where = ()
    values = ()
    query.pop(ANSWER)
    print(query)
    for key, value in query.items():
        where += (key+" =?",)
        values += (value,)

    # where = ' AND '.join(where)

    sql = ""
    if answer_type == 0:
        pass
    elif answer_type == 1: # Quem
        where = ' AND '.join(where)
        if not database.AGENT in query:
            sql = """SELECT """+database.AGENT+""" FROM event WHERE """+where
        elif not database.PATIENT in query:
            sql = """SELECT """+database.PATIENT+""" FROM event WHERE """+where
        elif not database.BENEFICIATY in query:
            sql = """SELECT """+database.BENEFICIATY+""" FROM event WHERE """+where
    elif answer_type == 2: # Onde
        aux_values = values
        count = 0
        for i in values:
            print(i)
            if isinstance(i, str) and i.lower() == "onde":
                a = list(aux_values)
                a.remove(i)
                aux_values = tuple(a)
                b = list(where)
                b.pop(count)
                where = tuple(b)
            count += 1

        where = ' AND '.join(where)
        values = aux_values
        sql = """SELECT """+database.LOC_TARGET+""" FROM event WHERE """+where
    elif answer_type == 3: # Como
        aux_values = values
        count = 0
        for i in values:
            print(i)
            if isinstance(i, str) and i.lower() == "como":
                a = list(aux_values)
                a.remove(i)
                aux_values = tuple(a)
                b = list(where)
                b.pop(count)
                where = tuple(b)
            count += 1

        where = ' AND '.join(where)
        values = aux_values
        sql = """SELECT """+database.ADJECTIVE+""", """+database.ADVERB+""" FROM event WHERE """+where
    elif answer_type == 4:
        pass
    elif answer_type == 5:
        pass
    elif answer_type == 6:
        pass
    
    print(sql)
    print(values)
    cursor.execute(sql, values)
    retorno = cursor.fetchall()
    print(retorno)

# inserir = {'ACTION': 'dormir', 'TENSE': 'passado', 'LOC_PREP':'de', 'ADVERB':'debaixo', 'ADJECTIVE':'', 'ADP_AGENT':'', 'ADP_PATIENT':'', 'ADP_LOC':'','AGENT':'João','PATIENT':'','BENEFICIATY':'','LOC_TARGET':'árvore','INSTRUMENT':''}
# insert_event(inserir)

