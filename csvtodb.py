import sys
import psycopg2
import psycopg2.extras
import argparse
import csv
from decouple import config

import argparse

if sys.version_info[0] < 3:
    raise Exception("This program requires at least python3.2")
if sys.version_info[0] == 3 and sys.version_info[1] < 2:
    raise Exception("This program requires at least python3.2")

parser = argparse.ArgumentParser(description='CSV to Redshift')

parser.add_argument('file', metavar='file path', type=str,
                   help='path to csv file')

parser.add_argument('table', metavar='table name', type=str,
                   help='db table name')

parser.add_argument("--chunk", help="split csv into chunks")

args = parser.parse_args()

file = args.file
table = args.table
chunks = args.chunk

dbconnection = {
	"dbname": config('DBNAME'),
	"host": config('HOST'),
	"user": config('USER'),
	"password": config('PASSWORD'),
	"port": config('PORT') 
}


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    arr = []
    for i in range(0, len(l), n):
        arr.append(l[i:i + n])
    return arr

def get_conn(config=dbconnection):
    try:
        conn = psycopg2.connect(dbname=config['dbname'], host=config['host'],
                                port=config['port'], user=config['user'], password=config['password'])
    except Exception as err:
        print(err.code, err)
    return conn

conn = get_conn()
cur = conn.cursor()

headers = None
vals = []

with open(file, newline='') as csvfile:
    rowReader = csv.reader(csvfile, delimiter=',')
    for row in rowReader:
        if headers is None:
            headers = row
        else:
            vals.append(tuple(row))

headerstr = ", ".join(headers)
valplaceholders = ", ".join(["%s" for v in headers])


if chunks:

    valuechunks = chunks(vals, 10000)
    datalen = len(valuechunks)
    percent = 100 / datalen

    for i,chunk in enumerate(valuechunks):
        print(str(round(percent * i, 4)) + "%")
        query = "INSERT INTO {} ({}) VALUES ({})".format(table, headerstr, valplaceholders)
        res = psycopg2.extras.execute_batch(cur,query,chunk)
        conn.commit()

else:
    query = "INSERT INTO {} ({}) VALUES ({})".format(table, headerstr, valplaceholders)

    res = psycopg2.extras.execute_batch(cur,query,vals)

    conn.commit()


cur.close()
conn.close()