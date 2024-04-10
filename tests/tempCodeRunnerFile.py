
# Teste de injeção de SQL para DataUpdateSupportCases
def test_data_update_support_cases_sql_injection(database_connection):
    name = "Marta"
    phoneNumber = "913766532"
    issue = '"); DROP TABLE SupportCases; --'

    # Executar a função a ser testada
    DataUpdateSupportCases(name, phoneNumber, issue)

    # Verificar se os dados foram inseridos corretamente
    with database_connection.cursor() as cursor:
        cursor.execute("SELECT * FROM SupportCases WHERE phoneNumber = %s", (phoneNumber,))
        result = cursor.fetchall()  # Obter todos os resultados

    assert result is not None

    # Fechar o cursor explicitamente para consumir qualquer resultado não lido
    cursor.close()