import sqlite3
import pandas as pd
import re

from scripts.payments_classifier import PaymentCategoryRBM


class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.tables = {}  # Store references to Table objects

    def __del__(self):
        self.conn.close()

    # Dictionary-like access
    def __getitem__(self, table_name):
        if table_name in self.tables:
            return self.tables[table_name]
        else:
            return self.get_table(table_name)

    def __setitem__(self, table_name, table_obj):
        self.tables[table_name] = table_obj

    def __delitem__(self, table_name):
        if table_name in self.tables:
            del self.tables[table_name]

    def get_table(self, table_name):
        if table_name not in self.tables:
            table = Table(self.conn, self.cursor, table_name)
            self.tables[table_name] = table
        return self.tables[table_name]

    def add_table(self, table_name):
        table = Table(self.conn, self.cursor, table_name)
        self.tables[table_name] = table
        return table


class Table:
    def __init__(self, conn, cursor, table_name):
        self.conn = conn
        self.cursor = cursor
        self.table_name = table_name

        if not self.check_table_exists(self.table_name):
            self.create_table()

        self.size = self.get_table_size()
        self.columns = self.get_columns()

    def get_columns(self):
        query = f"""
        PRAGMA table_info({self.table_name})
        """
        self.cursor.execute(query)
        columns = self.cursor.fetchall()
        return [column[1] for column in columns]

    def update_table_from_xsl(self, xsl_file):
        new_data = pd.read_excel(xsl_file)
        parsed_details = new_data["Omschrijving"].apply(self._parse_transaction)
        parsed_df = pd.DataFrame(parsed_details.tolist())
        new_data = pd.concat([new_data, parsed_df], axis=1)
        new_data = new_data.drop(
            columns=[
                "Omschrijving",
                "BIC",
                "EREF",
                "ORDP",
                "Rekeningnummer",
                "Muntsoort",
                "Rentedatum",
                "IBAN",
                "TRTP",
            ]
        )
        new_data = new_data.fillna("NOTPROVIDED")
        new_data["Transactiedatum"] = (
            new_data["Transactiedatum"]
            .astype(str)
            .apply(lambda x: x[:4] + "-" + x[4:6] + "-" + x[6:])
        )
        new_data = new_data.apply(self._update_name, axis=1)
        new_data = new_data.rename(
            columns={
                "Transactiedatum": "date",
                "Transactiebedrag": "amount",
                "NAME": "name",
                "REMI": "description",
                "location": "location",
                "Beginsaldo": "start_balance",
                "Eindsaldo": "end_balance",
            }
        )
        new_data["incoming"] = new_data["amount"] > 0
        new_data["amount"] = new_data["amount"].abs()
        new_data = self._assign_category(new_data)
        new_data.to_sql(self.table_name, self.conn, if_exists="append", index=False)
        self.remove_duplicates()

    def _assign_category(self, new_data):
        rbm = PaymentCategoryRBM(new_data)
        new_data = rbm.categorize()
        return new_data

    def remove_duplicates(self):
        query = f"""
        DELETE FROM {self.table_name}
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM {self.table_name}
            GROUP BY date, start_balance, end_balance, amount, name, description, location);
            VACUUM;
        """
        self.cursor.executescript(query)
        self.conn.commit()

    def _update_name(self, row):
        # Check if 'tikkie' is in the NAME column (case insensitive)
        if "tikkie" in row["NAME"].lower():
            if "via" in row["NAME"].lower():
                # Remove 'via Tikkie' (case insensitive)
                row["NAME"] = re.sub(
                    r"via\s+tikkie", "", row["NAME"], flags=re.IGNORECASE
                ).strip()

                remi_row = row["REMI"]

                pattern = r"\b\d+\b\s+\b\d+\b\s+(.*?)\s+([A-Z]{2}[A-Z0-9]+)"
                match = re.search(pattern, remi_row)
                if match:
                    # The substring is captured in the first group
                    substring = match.group(1)
                    remi_row = substring.strip()
                else:
                    remi_row = None

                row["REMI"] = remi_row
            else:
                # Split the REMI column by comma and take the second to last element
                remi_parts = [part.strip() for part in row["REMI"].split(",")]
                if len(remi_parts) > 1:
                    row["NAME"] = remi_parts[-2]
                    row["REMI"] = remi_parts[1]
        return row

    def _clean_list(self, lst):
        """Remove empty strings and strings with only spaces."""
        return [item for item in lst if item.strip()]

    def _parse_transaction(self, details):
        if details.startswith("/"):
            # Handle structured data
            parts = details.split("/")
            cleaned_parts = self._clean_list(parts)
            return dict(zip(cleaned_parts[::2], cleaned_parts[1::2]))
        else:
            # Handle unstructured data
            parts = details.split("  ")
            cleaned_parts = self._clean_list(parts)
            if cleaned_parts[0].startswith("BEA"):
                return {
                    "TRTP": cleaned_parts[0],
                    "NAME": cleaned_parts[1].split(",")[0].strip(),
                    "IBAN": cleaned_parts[1].split(",")[1].strip(),
                    "location": cleaned_parts[-1],
                }
        return {}

    def get_data_from_table(self):
        query = f"""
        SELECT * FROM {self.table_name}
        """
        data = pd.read_sql(query, self.conn)
        return data

    def check_table_exists(self, table_name):
        query = f"""
        SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'
        """
        self.cursor.execute(query)
        return self.cursor.fetchone() is not None

    def create_table(self):
        query = f"""
        CREATE TABLE {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            start_balance REAL,
            end_balance REAL,
            amount REAL,
            name TEXT,
            description TEXT,
            location TEXT,
            incoming BOOLEAN DEFAULT 0,
            category TEXT DEFAULT 'unknown'
        )
        """
        self.cursor.execute(query)
        self.conn.commit()

    def get_table_size(self):
        query = f"""
        SELECT COUNT(*) FROM {self.table_name}
        """
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
