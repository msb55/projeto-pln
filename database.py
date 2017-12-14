import sqlite3

# OBJECT TABLE FIELDS
NAME = 'NAME'

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

# DATABASE_NAME
DATABASE_NAME = 'semantic.db'

def init_db():
    # conectando...
    conn = sqlite3.connect(DATABASE_NAME)
    # definindo um cursor
    cursor = conn.cursor()

    # criando a tabela (schema)
    cursor.execute("""
    CREATE TABLE object (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            """+NAME+""" TEXT
    );
    """)

    # criando a tabela (schema)
    cursor.execute("""
    CREATE TABLE event (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            """+ACTION+""" TEXT NOT NULL,
            """+AGENT+""" INTEGER,
            """+PATIENT+""" INTEGER,
            """+BENEFICIATY+""" INTEGER,
            """+TENSE+""" TEXT,
            """+LOC_PREP+""" TEXT,
            """+LOC_TARGET+""" INTEGER,
            """+INSTRUMENT+""" INTEGER,
            """+ADVERB+""" TEXT,
            """+ADJECTIVE+""" TEXT,
            """+ADP_AGENT+""" TEXT,
            """+ADP_PATIENT+""" TEXT,
            """+ADP_LOC+""" TEXT,
            FOREIGN KEY("""+AGENT+""") REFERENCES object(id),
            FOREIGN KEY("""+PATIENT+""") REFERENCES object(id),
            FOREIGN KEY("""+BENEFICIATY+""") REFERENCES object(id),
            FOREIGN KEY("""+LOC_TARGET+""") REFERENCES object(id),
            FOREIGN KEY("""+INSTRUMENT+""") REFERENCES object(id)
    );
    """)

    print('Tabela criada com sucesso.')

    conn.close()

# init_db()