"""DAO to access hbase"""

class GenericDAO:
    """
    A class used to access HBase table
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def put(self, model_name, key, values):
        """
        Put a row into hbase

        Args:
            key (bytes): row key
            values (bytes): a dict containing cols and values
        """
        with self.db_manager.pool().connection() as conn:
            conn.table(model_name).put(key, values)

    def scan(self, model_name, row_start=None, row_stop=None, limit=100):
        """scan a batch of rows from hbase, a sample"""
        sample_rows = []
        with self.db_manager.pool().connection() as conn:
            table = conn.table(model_name)
            for row in table.scan(row_start=row_start, row_stop=row_stop, limit=limit):
                sample_rows.append(row)
        return sample_rows

    def get(self, model_name, key):
        """
        Get a row from hbase

        Args:
            key (bytes): row key to get values
        Returns:
            Row: row. The row as dict
        """
        with self.db_manager.pool().connection() as conn:
            table = conn.table(model_name)
            return table.row(key)

    def delete(self, model_name, key):
        """
        Delete a row in hbase

        Args:
            key (bytes): a key to delete row
        """
        with self.db_manager.pool().connection() as conn:
            table = conn.table(model_name)
            table.delete(key)
