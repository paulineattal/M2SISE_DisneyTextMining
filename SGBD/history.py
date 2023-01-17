# -*- coding: utf-8 -*-
"""
Created on Tue Jan 17 18:01:35 2023

@author: pauli
"""

import psycopg2
import psycopg2.extras as extras

conn = psycopg2.connect(
          user = "m140",
          password = "m140",
          host = "db-etu.univ-lyon2.fr",
          port = "5432",
          database = "m140"
    )

def execute_req(conn, req):
    try: 
        cursor = conn.cursor()
        cursor.execute(req)
        conn.commit()
        cursor.close()
    except (Exception, psycopg2.Error) as error :
        print ("Erreur lors de la création du table PostgreSQL", error)
        
        
sql_create_history = '''CREATE TABLE IF NOT EXISTS history(
Names TEXT
Country TEXT,
room_type TEXT,
nuitee INT,
reservation_date TEXT,
traveler_infos TEXT,
date_review TEXT,
review_title TEXT,
grade_review TEXT,
positive_review TEXT,
negative_review TEXT,
usefulness_review INT,
UniqueID TEXT,
hotel TEXT
  ); '''

execute_req(conn, sql_create_history)


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
        print("Error: %s" % error)
        conn.rollback()
        cursor.close()
        return 1
    print("the dataframe is inserted")
    cursor.close()
    
    
insert_values(conn, base, 'history')



