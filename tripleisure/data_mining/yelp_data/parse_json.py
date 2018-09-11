import json
import pandas as pd
import psycopg2


def create_table():
    conn = psycopg2.connect("dbname=tracy user=tracy")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""DROP TABLE IF EXISTS YELP_SIGHTSEEING""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS YELP_SIGHTSEEING (
        location_id integer NOT NULL,
        placename character varying(100),
        latitude double precision,
        longitude double precision,
        importance double precision,
        duration double precision
    );
    """)
    print(u'Create table successfully...')


def insert_data_into_table():
    with open('yelp_sightseeing.json', 'r') as input_file:
        businesses = json.load(input_file)
    placename = []
    price = []
    lat = []
    lon = []
    importance = []
    for biz in businesses:
        placename.append(biz.get('alias'))
        lat.append(biz.get('coordinates', {}).get('latitude'))
        lon.append(biz.get('coordinates', {}).get('longitude'))
        importance.append(biz.get('rating'))
    df = pd.DataFrame({'location_id': range(len(businesses)),
                       'placename': placename,
                       'latitude': lat,
                       'longitude': lon,
                       'importance': importance,
                       'duration': 3.0})
    df.to_csv('yelp_sightseeing.csv', index=False,
              columns=['location_id','placename', 'latitude', 'longitude', 'importance', 'duration'])
    conn = psycopg2.connect("dbname=tracy user=tracy")
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("""
        copy yelp_sightseeing
        from '/Users/tracy/code/tripleisure/tripleisure/yelp_data/yelp_sightseeing.csv'
        (FORMAT csv, HEADER, DELIMITER ',');
    """)
    print(u'Copy data into table...')


if __name__ == '__main__':
    create_table()
    insert_data_into_table()

