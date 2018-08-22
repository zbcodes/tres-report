import os.path
import sqlite3
from collections import OrderedDict
from dbfread import DBF

from period import Period


class Tres:
    """
    Statystyki z systemu Trawers
    """

    def __init__(self, tres_path):
        self.__kb_path = tres_path['kb']
        self.__kg_path = tres_path['kg']
        self.__mg_path = tres_path['mg']
        self.__na_path = tres_path['na']
        self.__zo_path = tres_path['zo']
        self.__period = Period()
        self.__conn = sqlite3.connect(':memory:',
                                      detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__cur = self.__conn.cursor()
        self.__is_sale = False
        self.__dbf_files = {}
        self.__create_dbfs_dict()
        self.__import_dbf()

    def __create_dbfs_dict(self):
        """Utworzenie słownika składającego się z nazw zbiorów i pol niezbędnych danych"""
        # kartoteka magazynowa
        self.__dbf_files['mg00immx.dbf'] = \
            {'indeks', 'category'}
        # dokumenty sprzedaży
        sales_docs = 'na' + self.__period.year_month() + 'mx.dbf'
        if os.path.isfile(self.__na_path + sales_docs):
            self.__is_sale = True
            self.__dbf_files[sales_docs] = \
                {'data', 'rodzajd', 'mag', 'indeks', 'oilosc', 'owartosc', 'bwartosc'}

    def __import_dbf(self):
        """Import pliku DBF i eksport danych do bazy SQLite"""
        for key, value in self.__dbf_files.items():
            dbf_file = ''
            if key[0:2] == 'mg':
                dbf_file = self.__mg_path + key
            elif key[0:2] == 'na':
                dbf_file = self.__na_path + key
            elif key[0:2] == 'zo':
                dbf_file = self.__zo_path + key
            elif key[0:2] == 'kg':
                dbf_file = self.__kg_path + key
            elif key[0:2] == 'kb':
                dbf_file = self.__kb_path + key
            with DBF(dbf_file, encoding='cp852', lowernames=True,
                     ignore_missing_memofile=True, load=True) as dbf_table:
                self.__remove_unnecessary_columns(dbf_table, value)
                sql_fields = self.__sqlite_fields_data(dbf_table, value)
                self.__crete_sqlite_table(key[:-4], sql_fields)
                self.__populate_sqlite_table(dbf_table, key[:-4], sql_fields)

    def __remove_unnecessary_columns(self, dbf_table, fields):
        """Usunięcie zbędnych kolumn z odczytanej tabeli DBF"""
        fields_to_remove = set(dbf_table.field_names).difference(fields)
        for row in dbf_table:
            for field in fields_to_remove:
                del row[field]

    def __sqlite_fields_data(self, dbf_table, fields):
        """Dane pól do utworzenia tabeli w bazie SQLite"""
        sql_fields = OrderedDict()
        for field in dbf_table.fields:
            if field.name in fields:
                sql_fields[field.name] = field.type
        return sql_fields

    def __crete_sqlite_table(self, table, fields):
        """Utworzenie pustej tabeli w bazie SQLite"""
        sql_query = 'CREATE TABLE {0} ('.format(table)

        for k, v in fields.items():
            sql_query += str(k)
            sql_query += ' '

            if v == 'C':
                sql_query += 'text'
            elif v == 'N':
                sql_query += 'real'
            elif v == 'D':
                sql_query += 'date'
            elif v == 'L':
                sql_query += 'integer'

            if str(k) != next(reversed(fields)):
                sql_query += ', '
            else:
                sql_query += ')'

        self.__cur.execute(sql_query)
        self.__conn.commit()

    def __populate_sqlite_table(self, dbf_table, table, sql_fields):
        """Wypełnienie danymi tabeli w bazie SQLite"""
        sql_query = 'INSERT INTO ' + table + ' VALUES (' + (len(sql_fields) - 1) * '?,' + '?)'
        for row in dbf_table:
            self.__cur.execute(sql_query, tuple(row.values()))
        self.__conn.commit()

    def sale(self):
        """Dane sprzedaży dla bieżącego miesiąca"""
        if self.__is_sale:
            # sprzedaż z podziałem na dni
            sql_query = """
                SELECT d.data,
                       sum(CASE WHEN i.category = '2' THEN d.oilosc ELSE 0 END) AS wine_quantity,
                       sum(CASE WHEN i.category = '2' THEN d.owartosc ELSE 0 END) AS wine_value,
                       sum(CASE WHEN i.category = '3' THEN d.oilosc ELSE 0 END) AS cider_quantity,
                       sum(CASE WHEN i.category = '3' THEN d.owartosc ELSE 0 END) AS cider_value,
                       sum(CASE WHEN i.category = '4' THEN d.oilosc ELSE 0 END) AS vodka_quantity,
                       sum(CASE WHEN i.category = '4' THEN d.owartosc ELSE 0 END) AS vodka_value,
                       sum(CASE WHEN i.category = '1' THEN d.oilosc ELSE 0 END) AS soki_quantity,
                       sum(CASE WHEN i.category = '1' THEN d.owartosc ELSE 0 END) AS soki_value,
                       sum(CASE WHEN i.category = '1' OR i.category = '2' OR i.category = '3' OR
                                     i.category = '4' THEN d.owartosc ELSE 0 END) AS net_value,
                       sum(CASE WHEN i.category = '1' OR i.category = '2' OR i.category = '3' OR
                                     i.category = '4' THEN d.bwartosc ELSE 0 END) AS gross_value
                FROM na{0}mx AS d, mg00immx AS i
                WHERE d.mag = '01' AND
                      d.rodzajd = 'FA' AND
                      d.indeks = i.indeks
                GROUP BY d.data
                ORDER BY d.data""".format(self.__period.year_month())
            self.__cur.execute(sql_query)
            daily_sales = self.__cur.fetchall()

            # miesięczne podsumowanie sprzedaży
            if daily_sales:
                sql_query = """
                    SELECT sum(CASE WHEN i.category = '2' THEN d.oilosc ELSE 0 END) AS wine_quantity,
                           sum(CASE WHEN i.category = '2' THEN d.owartosc ELSE 0 END) AS wine_value,
                           sum(CASE WHEN i.category = '3' THEN d.oilosc ELSE 0 END) AS cider_quantity,
                           sum(CASE WHEN i.category = '3' THEN d.owartosc ELSE 0 END) AS cider_value,
                           sum(CASE WHEN i.category = '4' THEN d.oilosc ELSE 0 END) AS vodka_quantity,
                           sum(CASE WHEN i.category = '4' THEN d.owartosc ELSE 0 END) AS vodka_value,
                           sum(CASE WHEN i.category = '1' THEN d.oilosc ELSE 0 END) AS soki_quantity,
                           sum(CASE WHEN i.category = '1' THEN d.owartosc ELSE 0 END) AS soki_value,
                           sum(CASE WHEN i.category = '1' OR i.category = '2' OR i.category = '3' OR
                                         i.category = '4' THEN d.owartosc ELSE 0 END) AS net_value,
                           sum(CASE WHEN i.category = '1' OR i.category = '2' OR i.category = '3' OR
                                         i.category = '4' THEN d.bwartosc ELSE 0 END) AS gross_value
                    FROM na{0}mx AS d, mg00immx AS i
                    WHERE d.mag = '01' AND
                          d.rodzajd = 'FA' AND
                          d.indeks = i.indeks""".format(self.__period.year_month())
                self.__cur.execute(sql_query)
                monthly_sales = self.__cur.fetchone()

                return daily_sales, monthly_sales
            else:
                self.__is_sale = False
                return 'Brak danych sprzedaży w bieżącym miesiącu...'

        else:
            return 'Brak danych sprzedaży w bieżącym miesiącu...'

    def is_sale(self):
        """Zwraca informację, czy istnieją dane sprzedaży"""
        return self.__is_sale
