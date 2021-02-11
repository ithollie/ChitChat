import MySQLdb

class MyData(object):
    
    localhost  =  ""
    user       =  ""
    password   =   ""
    database_name  =  ""
    
    connection  = None
    db = None
    
    
    def __init__(self):
        pass
    @classmethod
    def connect(self):
        if MyData.connection  is None:
            MyData.connection  =  MySQLdb.connect(self.localhost, self.user, self.password,self.database_name)
        else:
            MyData.connection = MyData.connection
            
            
    @staticmethod
    def createtable(table_name):
        pass
    @staticmethod
    def insert(name,last_name,email,password):
        sql_statement  =  "INSERT INTO students('name', 'passwor') VALES(`{name}`,`{name}`,`{name}`)"
        if sql_statement  is not  None:
            try:
                cursor  =  MyData.connection.cursor()
                cursor.execute(sql_statement)
                db.commit()
            except:
                MyData.connection.rollback()
                MyData.connection.close()
        else:
            return False


    @staticmethod
    def updates(sql):
        sql_statement  =  "UPDATE  INTO students('name', 'passwor') VALES(`{name}`,`{name}`,`{name}`)"
        if sql_statement  is not  None:
            try:
                cursor  =  MyData.connection.cursor()
                cursor.execute(sql_statement)
            except:
                MyData.connection.rollback()
        else:
            MyData.connection.close()
    

    @staticmethod
    def delete(data):
        sql_statement  =  "DELETE INTO students('name', 'passwor') VALES(`{name}`,`{name}`,`{name}`)"
        if sql_statement  is not  None:
            cursor  =  MyData.connection.cursor()
            cursor.execute(sql_statement)
            MyData.connection.close()
        else:
            return False

    @staticmethod
    def find(collection, query):
        sql_statement  =  "INSERT INTO students('name', 'passwor') VALES(`{name}`,`{name}`,`{name}`)"
        if sql_statement  is not  None:
            cursor  =  MyData.connection.cursor()
            cursor.execute(sql_statement)
            cursor.fetchone()
            MyData.connection.close()
        else:
            return False

    @staticmethod
    def find_one(collection, query):
       sql_statement  =  "INSERT INTO students('name', 'passwor') VALES(`{name}`,`{name}`,`{name}`)"
        if sql_statement  is not  None:
            cursor  =  MyData.connection.cursor()
            cursor.execute(sql_statement)
            MyData.connection.close()
        else:
            return False
