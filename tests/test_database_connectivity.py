import pytest
import mysql.connector
from actions.database_connectivity import DataUpdateSupportCases, DataUpdateComplaints



# Função de teste para DataUpdateComplaints
def test_data_update_complaints(database_connection):
    name = "Marta"
    phoneNumber = "913766532"
    complaint = "Rude behaviour"

    # Executar a função a ser testada
    DataUpdateComplaints(name, phoneNumber, complaint)

    # Verificar se os dados foram inseridos corretamente
    with database_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Complaints WHERE phoneNumber = %s", (phoneNumber,))
        result = cursor.fetchall()  # Obter todos os resultados

    assert result is not None

    # Fechar o cursor explicitamente para consumir qualquer resultado não lido
    cursor.close()

# Teste de injeção de SQL para DataUpdateSupportCases
def test_data_update_support_cases_sql_injection(database_connection):
    name = "Rui"
    phoneNumber = "913768592"
    issue = '"); DROP TABLE SupportCases; --'

    # Executar a função a ser testada
    DataUpdateSupportCases(name, phoneNumber, issue)

    # Verificar se os dados foram inseridos corretamente
    with database_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM SupportCases WHERE phoneNumber = %s", (phoneNumber,) )
        result = cursor.fetchall()  # Obter o resultado

    assert result == []  # Verificar se a lista está vazia

    # Fechar o cursor explicitamente para consumir qualquer resultado não lido
    cursor.close()

# Teste de injeção de SQL para DataUpdateComplaints
def test_data_update_complaints_sql_injection(database_connection):
    name = "Ricardo"
    phoneNumber = "923766592"
    complaint = '"); DROP TABLE Complaints; --'

    # Executar a função a ser testada
    DataUpdateComplaints(name, phoneNumber, complaint)

    # Verificar se os dados foram inseridos corretamente
    with database_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Complaints WHERE phoneNumber = %s", (phoneNumber,))
        result = cursor.fetchall()  # Obter todos os resultados

    assert result == []  # Verificar se a lista está vazia

    # Fechar o cursor explicitamente para consumir qualquer resultado não lido
    cursor.close()

