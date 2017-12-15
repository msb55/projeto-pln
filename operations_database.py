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
    print(obj[database.NAME], "não foi encontrado nos registros. Adicionado!")
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

def get_object_by_id(id_object):
    # conectando...
    conn = sqlite3.connect(database.DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    cursor.execute("""SELECT """+database.NAME+""" FROM object WHERE id = ?""",(id_object,))

    resultado = cursor.fetchall()

    if len(resultado) == 0:
        raise "Objeto não encontrado!"

    return resultado[0][0]

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


    dependencies = get_dependencies(dependencies)


    for key, value in dependencies.items():
        query[key] = value
    where = ()
    values = ()
    query.pop(ANSWER)

    for key, value in query.items():
        where += (key+" =?",)
        values += (value,)

    # where = ' AND '.join(where)

    sql = ""
    if answer_type == 0:
        where = ' AND '.join(where)
        sql= """SELECT CASE WHEN COUNT(*) > 0 THEN 'Sim' ELSE 'Não' END FROM event WHERE """ + where
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
    elif answer_type == 4: # Com; Com o que
        aux_values = values
        count = 0
        for i in values:
            if isinstance(i, str) and i.lower() == "com":
                a = list(aux_values)
                a.remove(i)
                aux_values = tuple(a)
                b = list(where)
                b.pop(count)
                where = tuple(b)
            count += 1

        where = ' AND '.join(where)
        values = aux_values
        sql = """SELECT """+database.INSTRUMENT+""" FROM event WHERE """+where
    elif answer_type == 5: # O que; Do que
        where = ' AND '.join(where)
        if not database.AGENT in query:
            sql = """SELECT """+database.AGENT+""" FROM event WHERE """+where
        elif not database.PATIENT in query:
            sql = """SELECT """+database.PATIENT+""" FROM event WHERE """+where
        elif not database.BENEFICIATY in query:
            sql = """SELECT """+database.BENEFICIATY+""" FROM event WHERE """+where
    elif answer_type == 6:
        where = ' AND '.join(where)
        sql = """SELECT """+database.BENEFICIATY+""" FROM event WHERE """+where
    
    cursor.execute(sql, values)
    retorno = cursor.fetchall()

    resposta = []
    for tup in retorno:
        for t in tup:
            if not t is None:
                if isinstance(t, int):
                    obj = get_object_by_id(t)
                    if not obj in resposta:
                        resposta.append(get_object_by_id(t))
                elif not t in resposta:
                    resposta.append(t)

    if len(resposta) == 2:
        resposta = ' e '.join(tuple(resposta))
    else:
        resposta = ', '.join(tuple(resposta))

    return resposta
