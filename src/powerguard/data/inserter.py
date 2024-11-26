class Inserter:
    def __init__(self, conn, cursor):
        self._conn = conn
        self._cursor = cursor

    def insert_into_table(self, table: str, data: dict):
        """Insert data into a specific table."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, tuple(data.values()))
        self.conn.commit()
