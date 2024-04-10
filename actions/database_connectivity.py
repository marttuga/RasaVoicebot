# import mysql.connector
# def DataUpdateSupportCases(name, phoneNumber, issue):
#     try:
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             passwd="root",
#             database="db_Tugs"
#         )        
#         with mydb.cursor() as mycursor:
#             sql = "CREATE TABLE IF NOT EXISTS SupportCases (name VARCHAR(255), phoneNumber VARCHAR(255), issue VARCHAR(255));"
#             mycursor.execute(sql)

#             sql = "INSERT INTO SupportCases (name, phoneNumber, issue) VALUES (%s, %s, %s)"
#             val = (name, phoneNumber, issue)
#             mycursor.execute(sql, val)

#         mydb.commit()
#     except mysql.connector.Error as e:
#         print(f"Error while updating support cases: {e}")
#     finally:
#         mydb.close()

# def DataUpdateComplaints(name, phoneNumber, complaint):
#     try:
#         mydb = mysql.connector.connect(
#             host="localhost",
#             user="root",
#             passwd="root",
#             database="db_Tugs"
#         )        

#         with mydb.cursor() as mycursor:
#             sql = "CREATE TABLE IF NOT EXISTS Complaints (name VARCHAR(255), phoneNumber VARCHAR(255), complaint VARCHAR(255));"
#             mycursor.execute(sql)

#             sql = "INSERT INTO Complaints (name, phoneNumber, complaint) VALUES (%s, %s, %s)"
#             val = (name, phoneNumber, complaint)
#             mycursor.execute(sql, val)

#         mydb.commit()
#     except mysql.connector.Error as e:
#         print(f"Error while updating complaints: {e}")
#     finally:
#         mydb.close()


import mysql.connector
def is_safe_input(data):
    # Implemente sua lógica de verificação aqui
    # Retorne True se os dados forem seguros, False caso contrário
    return not any(word in data.lower() for word in ["drop", "delete", "update", "insert"])

def DataUpdateSupportCases(name, phoneNumber, issue):
    mydb = None  # Inicializa a variável mydb fora do bloco try
    try:
        if not is_safe_input(name) or not is_safe_input(phoneNumber) or not is_safe_input(issue):
            print("Input contains potential SQL injection. Aborting operation.")
            return

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="db_Tugs"
        )
        with mydb.cursor() as mycursor:
            mycursor.execute("CREATE TABLE IF NOT EXISTS SupportCases (name VARCHAR(255), phoneNumber VARCHAR(255), issue VARCHAR(255));")

            sql = "INSERT INTO SupportCases (name, phoneNumber, issue) VALUES (%s, %s, %s)"
            val = (name, phoneNumber, issue)
            mycursor.execute(sql, val)

        mydb.commit()
    except mysql.connector.Error as e:
        print(f"Error while updating support cases: {e}")
    finally:
        if mydb:  # Verifica se mydb foi inicializado
            mydb.close()  # Fecha a conexão apenas se estiver aberta

def DataUpdateComplaints(name, phoneNumber, complaint):
    mydb = None  # Inicializa a variável mydb fora do bloco try
    try:
        if not is_safe_input(name) or not is_safe_input(phoneNumber) or not is_safe_input(complaint):
            print("Input contains potential SQL injection. Aborting operation.")
            return

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="db_Tugs"
        )

        with mydb.cursor() as mycursor:
            mycursor.execute("CREATE TABLE IF NOT EXISTS Complaints (name VARCHAR(255), phoneNumber VARCHAR(255), complaint VARCHAR(255));")

            sql = "INSERT INTO Complaints (name, phoneNumber, complaint) VALUES (%s, %s, %s)"
            val = (name, phoneNumber, complaint)
            mycursor.execute(sql, val)

        mydb.commit()
    except mysql.connector.Error as e:
        print(f"Error while updating complaints: {e}")
    finally:
        if mydb:  # Verifica se mydb foi inicializado
            mydb.close()  # Fecha a conexão apenas se estiver aberta
