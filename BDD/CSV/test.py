import os
import pandas as pd
from functions import insert_values

path = 'C:/Users/pattal/Documents/Disney/prépa/Disney-Text-Mining/ETL/dags/'
os.chdir('C:/Users/pattal/Documents/Disney/prépa/Disney-Text-Mining/ETL/dags/')

df = pd.read_csv('update.csv', sep = ";")
print(df)

import datetime
date = datetime.date.today()
df = df.assign(execution_date= str(date))

import psycopg2
import psycopg2.extras as extras


def insert_values(conn, df, table):
    tuples = [tuple(x) for x in df.to_numpy()]
    cols = ','.join(list(df.columns))
    # SQL query to execute
    query = "INSERT INTO %s(%s) VALUES %%s" % (table, cols)
    cursor = conn.cursor()
    try:
        extras.execute_values(cursor, query, tuples)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Erreur: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("Le dataframe à été inseré")
    cursor.close()

conn = psycopg2.connect(
            user = "m140",
            password = "m140",
            host = "db-etu.univ-lyon2.fr",
            port = "5432",
            database = "m140"
        )

insert_values(conn, df, 'history')