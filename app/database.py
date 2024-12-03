import psycopg2
from os.path import join, dirname, abspath
from os import environ

class Database:

    APP_PATH = dirname(abspath(__file__))
    DATA_PATH = join(dirname(APP_PATH), '..', 'data')
    QPATH = join(APP_PATH, 'queries')

    def __init__(self):
        database_url = f"postgresql://{environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@db:{environ.get('POSTGRES_PORT', '5432')}/{environ.get('POSTGRES_DB')}"
        
        self.conn = psycopg2.connect(database_url)
        self.cur = self.conn.cursor()

    def refreshDatabaseConnection(self):
        self.cur.close()
        self.conn.close()
        self.conn = psycopg2.connect(
                    user = environ.get('POSTGRES_USER'),
                    host = environ.get('POSTGRES_HOST'),
                    password = environ.get('POSTGRES_PASSWORD'),
                    dbname = environ.get('POSTGRES_DB')
        )
        self.cur = self.conn.cursor()

    def getData(self, queryFile, params):
        with open(join(self.QPATH, queryFile), 'r') as f:
            query = f.read()
            data = self.executeQuery(query, params)
        return data

    def executeQuery(self, query, params=None, getData=0, commit=0):
        self.cur = self.conn.cursor()
        data = None

        try:
            self.cur.execute(query, params)
            if commit == 1:
                self.conn.commit()
                return
            else:
                if getData == 1:
                    data = self.cur.fetchone()
                    if data is not None:
                        data = data[0]
                else:
                    data = self.cur.fetchall()
        except psycopg2.Error as Error:
            self.conn.rollback()
            raise ValueError(f"""An error has been occured --> {Error}\nThis is the query:\n\t{query}""")
        finally:
            self.cur.close()
            return data

while(True):
    try:
        db = Database()
        break
    except:
        continue