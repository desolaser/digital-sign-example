import pyodbc
from decouple import config


class DatabaseHelper:
    driver = config('DB_DRIVER')
    server = config('DB_SERVER') # 'SERVPV\SERVSQL'
    database = config('DB_DATABASE_NAME')
    user = config('DB_USER')
    password = config('DB_PASS')

    def get_connection_cursor(self):
        try:
            connection = pyodbc.connect(
                f"""
                    DRIVER={self.driver};
                    SERVER={self.server};
                    DATABASE={self.database};
                    UID={self.user};
                    PWD={self.password};
                """
            )
            return connection, connection.cursor()
        except Exception as e:
            print(e)
            raise e
    
    def get_token(self, serial_number):
        try: 
            _, cursor = self.get_connection_cursor()
            cursor.execute(f"""
                SELECT Nombre, Contraseña, Dispositivo, Firma, Contacto FROM [BdConservador].[dbo].[BdTokenFirma]
                WHERE SerialNumber = '{serial_number}'
            """)
            for row in cursor:
                token = {
                    "name": row[0].strip(),
                    "password": row[1].strip(),
                    "device": row[2].strip(),
                    "signature": row[3].strip(),
                    "contact": row[4].strip()
                }
                return token

            return None
        except Exception as e:
            print(e)
            raise Exception(e)