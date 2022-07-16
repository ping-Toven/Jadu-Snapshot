import sqlite3
from sqlite3 import Error
class DB_HELPER:
    # Function to create the tables
    def create_table(self, conn:sqlite3.Connection, create_table_sql):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(create_table_sql)
            print("Table created if it didn't already exist")
        except Error as e:
            print(e)

    def color_check(self, conn: sqlite3.Connection, token_id:str, color:str):
        """ Check for token's existing color. 
        :param conn: db connection obj
        :param token_id: token_id unique search key for WHERE
        :param color: colo value to check DB against
        :return bool: True = Update the color. False = Color exists / not needed for this token
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT color FROM {} WHERE token_id = (?)".format(table_name), [token_id])
        db_color, = cursor.fetchone()
        if db_color == color:
            return False
        return True

    def mod_check(self, conn: sqlite3.Connection, token_id:str, mod:str):
        """ Check for token's existing modification. 
        :param conn: db connection obj
        :param token_id: token_id unique search key for WHERE
        :param mod: mod value to check DB against
        :return bool: True = Update the mod. False = mod exists
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT modification FROM {} WHERE token_id = (?)".format(table_name), [token_id])
        db_mod, = cursor.fetchone()
        if db_mod == mod:
            return False
        return True
    
    def type_check(self, conn: sqlite3.Connection, token_id:str, type:str):
        """ Check for token's existing type value. 
        :param conn: db connection obj
        :param token_id: token_id unique search key for WHERE
        :param type: type value to check DB against
        :return bool: True = Update the type. False = type exists
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT type FROM {} WHERE token_id = (?)".format(table_name), [token_id])
        db_type, = cursor.fetchone()
        if db_type == type:
            return False
        return True
    
    def wallet_check(self, conn: sqlite3.Connection, token_id:str, wallet:str):
        """ Check for token's existing wallet address. 
        :param conn: db connection obj
        :param token_id: token_id unique search key for WHERE
        :param wallet: wallet address value to check DB against
        :return bool: True = Update the wallet. False = wallet exists
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT wallet FROM {} WHERE token_id = (?)".format(table_name), [token_id])
        db_wallet, = cursor.fetchone()
        if db_wallet == wallet:
            return False
        return True

    def update_token(self, conn:sqlite3.Connection, token_id:str, wallet:str, type:str='', modification:str='', color:str=''):
        """ update a token based on as-needed logic
        :param conn: sqlite3 connection object
        :param token_id: tokenID to update
        :param wallet: tokenID's current owner wallet address
        :param type: tokenID's TYPE attribute
        :param modification: tokenID's MODIFICATION attribute
        :param color: tokenID's COLOR attribute
        :return str: succesful msg
        """
        successful = "token updated successfully"
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        mod_bool, type_bool, color_bool, wallet_bool = self.mod_check(self, conn, token_id, modification), self.type_check(self, conn, token_id, type), self.color_check(self, conn, token_id, color), self.wallet_check(self, conn, token_id, wallet)
        if mod_bool and type_bool and color_bool and wallet_bool:
            cursor.execute("UPDATE {} SET (wallet = ?, type = ?, modification = ?, color = ?) WHERE token_id = ?".format(table_name), (wallet, type, modification, color, token_id))
            conn.commit()
        elif mod_bool and type_bool and wallet_bool:
            cursor.execute("UPDATE {} SET (wallet = ?, type = ?, modification = ?) WHERE token_id = ?".format(table_name), (wallet, type, modification, token_id))
            conn.commit()
        elif wallet_bool:
            cursor.execute("UPDATE {} SET (wallet = ?) WHERE token_id = ?".format(table_name), (wallet, token_id))
            conn.commit()
        return successful