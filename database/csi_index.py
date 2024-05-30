import sqlite3
import xlrd
import sys
import os
import pandas as pd

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Global variable for SQLite database file
DB_FILE = BASE_DIR.joinpath("csi_index.db")
TABLE_NAME = "index_data"
REQUIRED_COLUMNS = {
    "指数英文名称Index Name(Eng)": "csi_index",
    "成份券代码Constituent Code": "code",
    "成份券名称Constituent Name": "name",
    "交易所英文名称Exchange(Eng)": "exchange",
}


# 从 https://www.csindex.com.cn/#/indices/family/list 下载指数样本列表


class CSIIndex:
    def __init__(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Construct the CREATE TABLE query dynamically
        columns = ", ".join(
            [f"{col_name} TEXT" for col_name in REQUIRED_COLUMNS.values()]
        )
        create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({columns});"
        cursor.execute(create_table_query)

        conn.commit()
        conn.close()

    def get_csi(self):
        conn = sqlite3.connect(DB_FILE)
        query = f"SELECT * FROM {TABLE_NAME};"
        df = pd.read_sql_query(query, conn)
        conn.close()
        df["symbol"] = df["exchange"] + df["code"]
        return df

    def store_csi_xls(
        self,
        xls_file: str,
    ):
        exchange_mapping = {
            "Shenzhen Stock Exchange": "sz",
            "Shanghai Stock Exchange": "sh",
            "Beijing Stock Exchange": "bj",
        }

        workbook = xlrd.open_workbook(xls_file)
        sheet = workbook.sheet_by_index(0)  # Read the first sheet

        headers = [sheet.cell_value(0, col).strip() for col in range(sheet.ncols)]
        col_indices = {
            header: idx
            for idx, header in enumerate(headers)
            if header in REQUIRED_COLUMNS
        }

        if len(col_indices) != len(REQUIRED_COLUMNS):
            raise ValueError(
                f"The .xls file '{xls_file}' does not contain all the required columns."
            )

        # Extract and process data for the required columns
        data = []
        for row in range(1, sheet.nrows):
            row_data = []
            for header in REQUIRED_COLUMNS:
                value = sheet.cell_value(row, col_indices[header])
                if header == "交易所英文名称Exchange(Eng)":  # Process exchange column
                    value = exchange_mapping.get(
                        value, value
                    )  # Map to abbreviation or leave unchanged
                row_data.append(value)
            data.append(row_data)

        # Connect to SQLite database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        current_csi_name = sheet.cell_value(
            1, col_indices["指数英文名称Index Name(Eng)"]
        )
        colume_name = REQUIRED_COLUMNS["指数英文名称Index Name(Eng)"]
        cursor.execute(
            "DELETE FROM {} WHERE {} = ?".format(TABLE_NAME, colume_name),
            (current_csi_name,),
        )

        # Insert the data into the table
        placeholders = ", ".join(["?"] * len(REQUIRED_COLUMNS))
        insert_query = f"INSERT INTO {TABLE_NAME} VALUES ({placeholders});"
        cursor.executemany(insert_query, data)

        conn.commit()
        conn.close()

        print(
            f"Data from '{xls_file}' has been successfully inserted into '{TABLE_NAME}' in '{DB_FILE}'."
        )


csi = CSIIndex()

if __name__ == "__main__":
    # Ensure the command-line arguments include at least one .xls file
    if len(sys.argv) < 2:
        print("Usage: python script.py <xls_file1> <xls_file2> ...")
        sys.exit(1)
    csi = CSIIndex()
    # Process each .xls file passed as command-line arguments
    for xls_file_path in sys.argv[1:]:
        if not os.path.isfile(xls_file_path):
            print(f"File '{xls_file_path}' does not exist. Skipping...")
            continue
        try:
            csi.store_csi_xls(xls_file_path)
        except Exception as e:
            print(f"Error processing file '{xls_file_path}': {e}")
