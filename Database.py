# https://stackoverflow.com/questions/66303760/mariadb-connection-pool-gets-exhausted-after-a-while
import mariadb

import configparser
import sys
import os

# from classes.logger import AppLogger

# logger = AppLogger(__name__)

connections = 0
MARIADBPASS = os.environ.get('MARIADB_PROD_PASS')
MARIADBHOST = os.environ.get('MARIADB_PRODDB_HOST')
MARIADBDBNAME = os.environ.get('MARIADB_PROD_DB_NAME')
MARIADBUSERNAME = os.environ.get('MARIADB_PROD_USER')


class Db:
    """
    Main database for the application
    """

    config = configparser.ConfigParser()
    config.read('/app/config/conf.ini')
    db_config = config['db']
    try:
        conn_pool = mariadb.ConnectionPool(
            user=f"{MARIADBUSERNAME}",
            password=f"{MARIADBPASS}",
            host=f"{MARIADBHOST}",
            database=f"{MARIADBDBNAME}",
            # port=int(db_config['port']),
            # pool_name=db_config['pool_name'],
            pool_size=5,  # int(db_config['pool_size']),
        )
    except mariadb.PoolError as e:
        print(f'Error creating connection pool: {e}')
        # logger.error(f'Error creating connection pool: {e}')
        sys.exit(1)

    def get_pool(self):
        return self.conn_pool if self.conn_pool is not None else self.create_pool()

    def __get_connection__(self):
        """
        Returns a db connection
        """

        global connections
        try:
            pconn = self.conn_pool.get_connection()
            pconn.autocommit = True
            print(f"Receiving connection. Auto commit: {pconn.autocommit}")
            connections += 1
            print(f"New Connection. Open Connections: {connections}")
            # logger.debug(f"New Connection. Open Connections: {connections}")
        except mariadb.PoolError as e:
            print(f"Error getting pool connection: {e}")
            # logger.error(f'Error getting pool connection: {e}')
            # exit(1)
            pconn = self.ــcreate_connectionــ()
            pconn.autocommit = True
            connections += 1
            # logger.debug(f'Created normal connection following failed pool access. Connections: {connections}')
        return pconn

    def ــcreate_connectionــ(self):
        """
        Creates a new connection. Use this when getting a
         pool connection fails
        """
        db_config = self.db_config
        return mariadb.connect(
            user=f"{MARIADBUSERNAME}",
            password=f"{MARIADBPASS}",
            host=f"{MARIADBHOST}",
            database=f"{MARIADBDBNAME}",
            # port=int(db_config['port']),
        )

    def exec_sql(self, sql, values=None):
        global connections
        pconn = self.__get_connection__()
        try:
            cur = pconn.cursor()
            print(f'Sql: {sql}')
            print(f'values: {values}')
            cur.execute(sql, values)
            # pconn.commit()
            # Is this a select operation?
            if sql.startswith('SELECT') or sql.startswith('Select') or sql.startswith('select'):
                result = cur.fetchall()  # Return a result set for select operations
            else:
                result = True

            pconn.close()
            connections -= 1
            print(f'connection closed: connections: {connections}')
            # logger.debug(f'connection closed: connections: {connections}')
            # return True #Return true for insert, update, and delete operations
            return result
        except mariadb.Error as e:
            print(f"Error performing database operations: {e}")
            # pconn.rollback()
            pconn.close()
            connections -= 1
            print(f'connection closed: connections: {connections}')
            return False
