"""DAO to access hbase"""

class Model1DAO:
    """
    A class used to access HBase table model1
    """
    TABLE_NAME = 'datamodel1'

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def put(self, key, values):
        """
        Put a row into hbase

        Args:
            key (bytes): row key
            values (bytes): a dict containing cols and values
        """
        with self.db_manager.pool().connection() as conn:
            conn.table(self.TABLE_NAME).put(key, values)

    def scan(self, row_start=None, row_stop=None, limit=100):
        """scan a batch of rows from hbase, a sample"""
        sample_rows = []
        with self.db_manager.pool().connection() as conn:
            table = conn.table(self.TABLE_NAME)
            for row in table.scan(row_start=row_start, row_stop=row_stop, limit=limit):
                sample_rows.append(row)
        return sample_rows

    def get(self, key):
        """
        Get a row from hbase

        Args:
            key (bytes): row key to get values
        Returns:
            Row: row. The row as dict
        """
        with self.db_manager.pool().connection() as conn:
            table = conn.table(self.TABLE_NAME)
            return table.row(key)

    def delete(self, key):
        """
        Delete a row in hbase

        Args:
            key (bytes): a key to delete row
        """
        with self.db_manager.pool().connection() as conn:
            table = conn.table(self.TABLE_NAME)
            table.delete(key)
