import copy

import psycopg2.extras


COLS_RELATION ={
    "last_update": "lastupdate",
    "mag_type": "magtype",
    "ev_type": "evtype",
    "longitude": "lon",
    "latitude": "lat",
    "id": "unid",
    "magnitude": "mag",
    "region": "flynn_region"
}


def _translate_columns_from_db(d):
    updated = copy.deepcopy(d)
    for rows in updated:
        for k, v in COLS_RELATION.items():
            rows[v] = rows.pop(k)
    return updated


def _translate_columns_to_db(d):
    updated = copy.deepcopy(d)
    for rows in updated:
        for k, v in COLS_RELATION.items():
            rows[k] = rows.pop(v)
    return updated


def _get_data_from_db(conn, q, q_data=tuple()):

    with conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as curs:
            sql_query = curs.execute(q, q_data)
            data = curs.fetchall()

    return _translate_columns_from_db(data)


def get_all_from_db(conn):

    sql_q = "SELECT * FROM quake_data;"

    results = _get_data_from_db(conn, sql_q)

    return results


def get_new_data_from_db(conn, date):
    sql_q = "select * from quake_data WHERE last_update > %s;"
    q_data = (date, )

    results = _get_data_from_db(conn, sql_q, q_data)

    return results



