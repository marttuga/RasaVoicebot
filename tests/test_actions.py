import pytest
from asyncio import AbstractEventLoop, get_event_loop, new_event_loop
from rasa_sdk import Tracker
from unittest.mock import call
from unittest.mock import Mock, patch
from unittest.mock import MagicMock, AsyncMock
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted, UserUtteranceReverted
from actions.actions import (
    ActionDefaultFallback,
    ActionRestart,
    ActionSaveSupportCases,
    ActionSaveComplaints,
    ValidateFormComplain,
    ValidateFormSupport,
)

# Função utilitária para criar um objeto Tracker mockado com os slots necessários
def create_tracker():
    return MagicMock(
        get_slot=MagicMock(side_effect=lambda slot: {
            "name": "Marta",
            "phoneNumber": "914567254",
            "issue": "Test issue"
        }[slot])
    )


# Teste da ActionDefaultFallback
@pytest.mark.asyncio
async def test_action_default_fallback():
    action = ActionDefaultFallback()
    dispatcher = CollectingDispatcher()
    tracker = create_tracker()

    response = await action.run(dispatcher, tracker, {})

    assert len(response) == 1
    assert response[0]['event'] == 'rewind'

# Teste da ActionRestart
@pytest.mark.asyncio
async def test_action_restart():
    action = ActionRestart()
    dispatcher = CollectingDispatcher()
    tracker = create_tracker()

    response = await action.run(dispatcher, tracker, {})

    assert len(response) == 1
    assert response[0]['event'] == 'restart'

# Teste da ValidateFormComplain
@pytest.mark.asyncio
async def test_validate_form_complain():
    action = ValidateFormComplain()
    dispatcher = CollectingDispatcher()
    tracker = create_tracker()

    # Teste para um nome inválido (com números)
    result = action.validate_name("John123", dispatcher, tracker, {})
    assert result == {"name": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Invalid name. Name should contain only alphabets."
    dispatcher.messages = []

    # Teste para um nome válido
    result = action.validate_name("John", dispatcher, tracker, {})
    assert result == {"name": "John"}
    assert len(dispatcher.messages) == 0  # Verifique se nenhuma mensagem de erro foi enviada
    dispatcher.messages = []


    # Teste para um número de telefone em branco
    result = action.validate_phoneNumber("", dispatcher, tracker, {})
    assert result == {"phoneNumber": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Please provide a phone number."
    dispatcher.messages = []

    # Teste para um número de telefone inválido (não tem 9 dígitos)
    result = action.validate_phoneNumber("12345678", dispatcher, tracker, {})
    assert result == {"phoneNumber": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Invalid phone number. Phone number should contain 9 digits."
    dispatcher.messages = []

    # Teste para um número de telefone válido
    result = action.validate_phoneNumber("123456789", dispatcher, tracker, {})
    assert result == {"phoneNumber": "123456789"}
    assert len(dispatcher.messages) == 0  # Verifique se nenhuma mensagem de erro foi enviada
    dispatcher.messages = []

    # Teste para uma complaint em branco
    result = action.validate_complaint("", dispatcher, tracker, {})
    assert result == {"complaint": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Please provide a complaint."
    dispatcher.messages = []

    # Teste para uma complaint que excede o limite de caracteres
    result = action.validate_complaint("a"*101, dispatcher, tracker, {})
    assert result == {"complaint": None}  # Corrija esta linha, remova as aspas em torno de None
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "The complaint should not exceed 100 characters."
    dispatcher.messages = []

    # Teste para uma reclamação com SQL Injection (não deve ser inserida)
    sql_injection_complaint = '"); DROP TABLE SupportCases; --'
    result = action.validate_complaint(sql_injection_complaint, dispatcher, tracker, {})
    assert result == {"complaint": None}  # Verifique se a reclamação foi rejeitada
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem de erro foi enviada
    assert "Invalid complaint. Please avoid using SQL keywords." in dispatcher.messages[0]["text"]  # Verifique se a mensagem de erro inclui "Invalid complaint description"
    dispatcher.messages = []

    # Teste para uma complaint válida
    valid_description = "This is a valid issue description."
    result = action.validate_complaint(valid_description, dispatcher, tracker, {})
    assert result == {"complaint": valid_description}
    assert len(dispatcher.messages) == 0  # Verifique se nenhuma mensagem de erro foi enviada
    dispatcher.messages = []




# Teste da ValidateFormSupport
@pytest.mark.asyncio
async def test_validate_form_support():
    action = ValidateFormSupport()
    dispatcher = CollectingDispatcher()
    tracker = Tracker(sender_id="default",slots={},latest_message={},events=[],
    paused=False,followup_action=None,active_loop=None,latest_action_name=None, )
    
    # Teste para um nome em branco
    result = action.validate_name("", dispatcher, tracker, {})  # chamar a função validate_name 
    assert result == {"name": None}  # verificar se está vazio 
    assert len(dispatcher.messages) == 1  # verificar se a mensagem foi enviada pelo dispatcher
    assert dispatcher.messages[0]["text"] == "Please provide a name." 
    dispatcher.messages = []  # Limpa as mensagens no dispatcher para o próximo teste

    # Teste para um nome inválido (com números)
    result = action.validate_name("John123", dispatcher, tracker, {})  # Chamando a função validate_name com um nome inválido
    assert result == {"name": None}  # Verifica se o resultado está None
    assert len(dispatcher.messages) == 1 
    assert dispatcher.messages[0]["text"] == "Invalid name. Name should contain only alphabets."  # Verifica se a mensagem enviada é a esperada
    dispatcher.messages = []  # Limpa as mensagens no dispatcher para o próximo teste

    # Teste para um nome válido
    result = action.validate_name("John", dispatcher, tracker, {})  # chamar a função validate_name com um nome válido
    assert result == {"name": "John"}  # Verificar se ficou o resultado esperado 
    assert len(dispatcher.messages) == 0  # Verifica se nenhuma mensagem de erro foi enviada 
    dispatcher.messages = []  # Limpa as mensagens no dispatcher para o próximo teste



    # Teste para um número de telefone em branco
    result = action.validate_phoneNumber("", dispatcher, tracker, {})
    assert result == {"phoneNumber": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Please provide a phone number."
    dispatcher.messages = []

    # Teste para um número de telefone inválido (não tem 9 dígitos)
    result = action.validate_phoneNumber("12345678", dispatcher, tracker, {})
    assert result == {"phoneNumber": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Invalid phone number. Phone number should contain 9 digits."
    dispatcher.messages = []

    # Teste para um número de telefone válido
    result = action.validate_phoneNumber("123456789", dispatcher, tracker, {})
    assert result == {"phoneNumber": "123456789"}
    assert len(dispatcher.messages) == 0  # Verifique se nenhuma mensagem de erro foi enviada
    dispatcher.messages = []

    # Teste para uma descrição em branco
    result = action.validate_issue("", dispatcher, tracker, {})
    assert result == {"issue": None}
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "Please provide an issue description."
    dispatcher.messages = []

    # Teste para uma descrição que excede o limite de caracteres
    result = action.validate_issue("a"*101, dispatcher, tracker, {})
    assert result == {"issue": None}  # Corrija esta linha, remova as aspas em torno de None
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem foi enviada
    assert dispatcher.messages[0]["text"] == "The issue description should not exceed 100 characters."
    dispatcher.messages = []

    # Teste para uma descrição com SQL Injection (não deve ser inserida)
    sql_injection_description = '"); DROP TABLE SupportCases; --'
    result = action.validate_issue(sql_injection_description, dispatcher, tracker, {})
    assert result == {"issue": None}  # Verifique se a descrição foi rejeitada
    assert len(dispatcher.messages) == 1  # Verifique se apenas uma mensagem de erro foi enviada
    assert "Invalid issue description" in dispatcher.messages[0]["text"]  # Verifique se a mensagem de erro inclui "Invalid issue description"
    dispatcher.messages = []

    # Teste para uma descrição válida
    valid_description = "This is a valid issue description."
    result = action.validate_issue(valid_description, dispatcher, tracker, {})
    assert result == {"issue": valid_description}
    assert len(dispatcher.messages) == 0  # Verifique se nenhuma mensagem de erro foi enviada
    dispatcher.messages = []

# Teste da ActionSaveSupportCases
@pytest.mark.asyncio
async def test_action_save_support_cases():
    action = ActionSaveSupportCases()
    dispatcher = CollectingDispatcher()
    tracker = create_tracker()

    # Mock do método mysql.connector.connect
    with patch("mysql.connector.connect") as mock_connect:
        # Mock do cursor da bse de dados
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_connect.return_value.cursor.return_value = mock_cursor

        # Mock da função DataUpdateSupportCases
        with patch("actions.database_connectivity.DataUpdateSupportCases") as mock_data_update:
            # Definir o efeito colateral para DataUpdateSupportCases
            def side_effect(name, phoneNumber, issue):
                # Realizar verificações necessárias em name, phoneNumber e issue 
                assert name == "Marta"
                assert phoneNumber == "914567254"
                assert issue == "Test issue"

            mock_data_update.side_effect = side_effect

            result = action.run(dispatcher, tracker, {})

    # Resto do teste permanece igual
    mock_connect.assert_called_with(
        host="localhost",
        user="root",
        passwd="root",
        database="db_Tugs"
    )
    mock_connect.return_value.cursor.assert_called()

# Teste da ActionSaveComplaints
@pytest.mark.asyncio
async def test_action_save_complaints():
    action = ActionSaveComplaints()
    dispatcher = CollectingDispatcher()
    tracker = create_tracker()

    # Mock do método tracker.get_slot para retornar os slots necessários
    with patch.object(tracker, 'get_slot', side_effect=lambda slot: {
        "name": "Marta",
        "phoneNumber": "914567254",
        "complaint": "Test complaint"
    }[slot]) as mock_get_slot:

        # Mock do método mysql.connector.connect
        with patch("mysql.connector.connect") as mock_connect:
            # Mock do cursor do banco de dados
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None
            mock_connect.return_value





