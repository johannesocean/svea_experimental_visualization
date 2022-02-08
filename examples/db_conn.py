#!/usr/bin/env python3
"""
Created on 2022-01-11 14:39

@author: johannes
"""
import sqlite3
import pandas as pd
from svea_expvis.config import Config


def get_db_conn(db_path):
    """Doc."""
    return sqlite3.connect(db_path)


class DbHandler:
    """Doc."""
    def __init__(self, table=None, parameter=None):
        self.table = table
        self.parameter = parameter
        cfig = Config(data_file_name='data_chl.db')
        self.db_path = cfig.get_data_path()

    def update_attributes(self, **kwargs):
        """Doc."""
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def post(self, data, table=None):
        """Doc."""
        conn = get_db_conn(self.db_path)
        table = table or self.table
        data.to_sql(table, conn, if_exists='append', index=False)

    def update_db(self, update_query):
        """Doc."""
        conn = None
        try:
            conn = get_db_conn(self.db_path)
            cursor = conn.cursor()
            cursor.execute(update_query)
            conn.commit()
        except sqlite3.Error as error:
            print("Failed to update sqlite table", error)
        finally:
            if conn:
                conn.close()
                print("The SQLite connection is closed")

    def get(self, table=None):
        """Doc."""
        conn = get_db_conn(self.db_path)
        table = table or self.table
        return pd.read_sql(f'select * from {table}', conn)

    def get_parameter_data(self, table=None, parameter=None):
        """Doc."""
        conn = get_db_conn(self.db_path)
        table = table or self.table
        parameter = parameter or self.parameter
        query = f"""select {parameter} from {table}"""
        return pd.read_sql(query, conn)

    def get_unique_parameter_data(self, table=None, parameter=None):
        """Doc."""
        conn = get_db_conn(self.db_path)
        table = table or self.table
        parameter = parameter or self.parameter
        query = f"""select distinct {parameter} from {table}"""
        return pd.read_sql(query, conn)

    def get_data_for_time_period(self, start_time=None, end_time=None,
                                 table=None):
        """Doc."""
        if start_time and end_time:
            conn = get_db_conn(self.db_path)
            table = table or self.table
            return pd.read_sql(
                f"""select * from {table} where timestamp between 
                '"""+start_time+"""%' and '"""+end_time+"""%'""",
                conn
            )

    def get_data_for_key(self, key, table=None):
        """Doc."""
        conn = get_db_conn(self.db_path)
        table = table or self.table
        return pd.read_sql(
            f"""select * from {table} where KEY like '"""+key+"""'""",
            conn
        )


if __name__ == "__main__":
    dbh = DbHandler(table='btl', parameter='KEY')
