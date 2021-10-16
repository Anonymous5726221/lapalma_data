from urllib.parse import urlparse
import os
from datetime import timedelta
from datetime import datetime as dt

import psycopg2
from psycopg2 import sql

from db_helper.tools import _translate_columns_to_db, _translate_columns_from_db, get_all_from_db
from SeismicPortal.dl_quakes import CANARY_BOX, SeismicPortal


DB_URL = urlparse(os.environ.get("DATABASE_URL"))

DB_HOST = DB_URL.hostname
DB_PORT = DB_URL.port
DB_NAME = DB_URL.path[1:]
DB_USER = DB_URL.username
DB_PASS = DB_URL.password


def convert_sp_to_db(q_list):
    to_update = _translate_columns_to_db(q_list)

    for i in to_update:
        i.pop("auth")

    return to_update


def upsert_row(r, conn):

    col_names = tuple(r.keys())
    vals = ", ".join(f"'{v}'" for v in r.values())
    conflict_resolution = ", ".join(f"{c} = EXCLUDED.{c}" for c in r.keys())

    sql_q = sql.SQL('INSERT INTO quake_data({col}) VALUES({val}) ON CONFLICT (id) DO UPDATE SET {conf};').format(
        col=sql.SQL(',').join(map(sql.Identifier, col_names)),
        val=sql.SQL(vals),
        conf=sql.SQL(conflict_resolution)
    )

    with conn:
        with conn.cursor() as curs:
            print(sql_q.as_string(curs))
            sql_query = curs.execute(sql_q, (col_names, vals, conflict_resolution))

        conn.commit()


if __name__ == '__main__':

    sp = SeismicPortal()
    conn = psycopg2.connect(f"host={DB_HOST} port={DB_PORT} dbname={DB_NAME} user={DB_USER} password={DB_PASS}")

    results = sp.download_earthquakes(start_time=dt(2021, 8, 4), **CANARY_BOX)
    to_update = convert_sp_to_db([r.get("properties") for r in results])

    db_snap = {r.get("unid"): r for r in get_all_from_db(conn)}

    for ix, r in enumerate(to_update):
        print(f"Updating {ix+1} of {len(to_update)} rows. ID: {r.get('id')}")
        upsert_row(r, conn)

    db_diff = {r.get("unid"): r for r in get_all_from_db(conn)}

    for k, v in db_diff.items():

        if db_snap.get(k) != v:

            print(f"Event {v.get('unid')} updated:")
            print(f"Before: {db_snap.get(k)}")
            print(f"After: {v}")
