import os
import warnings

import pandas as pd
import psycopg2
import requests

from config import quest
from utils import get_logger

warnings.simplefilter("ignore", UserWarning)

logger = get_logger(__name__)


class QuestBase:
    def __init__(self) -> None:
        self.dsn = quest.dsn
        self.host = quest.host
        self.rest_port = quest.rest_port
        try:
            _ = psycopg2.connect(self.dsn)
        except psycopg2.OperationalError as e:
            logger.error(f"Error connecting to questdb with dsn: {self.dsn}")
            raise e

    def sql_exec(self, sql: str):
        with psycopg2.connect(self.dsn) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql)


class Stock(QuestBase):
    def create_table(self) -> None:
        sql = """CREATE TABLE IF NOT EXISTS 'stock' (
                    symbol SYMBOL INDEX,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    amount DOUBLE,
                    volume DOUBLE,
                    date TIMESTAMP);
                """
        self.sql_exec(sql)

    def recreate_table(self):
        sql = """
        DROP TABLE 'stock';
        """
        self.sql_exec(sql)
        self.create_table()

    def bulk_insert_csv(self, file_path: str) -> None:
        if os.path.exists(file_path):
            schema = """[
                {"name": "symbol",  "type": "symbol"},
                {"name": "open",    "type": "double"},
                {"name": "high",    "type": "double"},
                {"name": "low",     "type": "double"},
                {"name": "close",   "type": "double"},
                {"name": "amount",  "type": "double"},
                {"name": "volume",  "type": "double"},
                {"name": "date",    "type": "TIMESTAMP", "pattern": "yyyy-MM-ddTHH:mm:ss"}
            ]"""
            params = {"name": "stock"}
            files = {
                "schema": schema,
                "data": open(file_path, "rb"),
            }
            requests.post(
                "http://{host}:{port}/imp".format(host=self.host, port=self.rest_port),
                params=params,
                files=files,
            )

    def latest_data(self, symbol):
        sql = """
            select * from 'stock'
            where symbol = '{symbol}'
            order by date desc
            limit 1;""".format(symbol=symbol)

        with psycopg2.connect(self.dsn) as conn:
            data = pd.read_sql(sql, conn)
        if not data.empty:
            data["date"] = pd.to_datetime(data["date"])
            data = data.set_index("date")
            return data

    def query(self, symbol):
        sql = """
            select *
            from stock where symbol = '{symbol}';
            """.format(symbol=symbol)

        with psycopg2.connect(self.dsn) as conn:
            data = pd.read_sql(sql, conn)
        if not data.empty:
            data["date"] = pd.to_datetime(data["date"])
            data = data.set_index("date")
            return data


class Gbbq(QuestBase):
    def create_table(self) -> None:
        sql = """CREATE TABLE IF NOT EXISTS 'gbbq' (
                    code SYMBOL INDEX,
                    date TIMESTAMP,
                    category INT,
                    fenhong DOUBLE,
                    peigujia DOUBLE,
                    songgu DOUBLE,
                    peigu DOUBLE
                    );
                """
        self.sql_exec(sql)

    def recreate_table(self):
        sql = """
        DROP TABLE 'gbbq';
        """
        self.sql_exec(sql)
        self.create_table()

    def bulk_insert_csv(self, file_path: str) -> None:
        if os.path.exists(file_path):
            schema = """[
                {"name": "code",  "type": "symbol"},
                {"name": "date",   "type": "TIMESTAMP", "pattern": "yyyyMMdd"},
                {"name": "category",  "type": "int"},
                {"name": "fenhong",   "type": "double"},
                {"name": "peigujia",  "type": "double"},
                {"name": "songgu",    "type": "double"},
                {"name": "peigu",     "type": "double"}
            ]"""
            params = {"name": "gbbq"}
            files = {
                "schema": schema,
                "data": open(file_path, "rb"),
            }
            requests.post(
                "http://{host}:{port}/imp".format(host=self.host, port=self.rest_port),
                params=params,
                files=files,
            )

    def query(self, code="", category=""):
        if not code and not category:
            sql = """select * from gbbq;"""
        if code:
            sql = """select * from gbbq where code = '{}';""".format(code)
        if category:
            category = str(category)
            sql = """select * from gbbq where category = '{}';""".format(category)
        if code and category:
            category = str(category)
            sql = """select * from gbbq where code = '{code}' and category = '{category}';""".format(
                code=code, category=category
            )
        with psycopg2.connect(self.dsn) as conn:
            data = pd.read_sql(sql, conn)
        if not data.empty:
            data["date"] = pd.to_datetime(data["date"])
            data = data.set_index("date")
            return data


stock = Stock()
gbbq = Gbbq()
