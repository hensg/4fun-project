"""DAO to access hbase"""

class GenericDAO:
    """
    A class used to access HBase table
    """
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.table_name = 'models'

    def __full_key(self, model_name, key):
        return '{}|{}'.format(model_name, key)

    def put(self, model_name, key, values):
        """
        Put a row into hbase

        Args:
            key (bytes): row key
            values (bytes): a dict containing cols and values
        """
        with self.db_manager.pool().connection() as conn:
            full_key = self.__full_key(model_name, key)
            conn.table(self.table_name).put(full_key, values)

    def scan(self, model_name, row_start=None, row_stop=None, limit=100):
        """scan a batch of rows from hbase, a sample"""
        sample_rows = []
        with self.db_manager.pool().connection() as conn:
            table = conn.table(self.table_name)
            full_key_start = self.__full_key(model_name, row_start)
            full_key_stop = self.__full_key(model_name, row_stop)
            for row in table.scan(row_start=full_key_start, row_stop=full_key_stop, limit=limit):
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
            table = conn.table(self.table_name)
            full_key = self.__full_key(model_name, key)
            return table.row(full_key)

    def delete(self, model_name, key):
        """
        Delete a row in hbase

        Args:
            key (bytes): a key to delete row
        """
        with self.db_manager.pool().connection() as conn:
            table = conn.table(self.table_name)
            full_key = self.__full_key(model_name, key)
            table.delete(full_key)
