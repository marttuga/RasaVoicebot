from email.mime.multipart import MIMEMultipart
import re
import smtplib
import mysql.connector
from typing import Any, Text, Dict, List, Union
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import Restarted, UserUtteranceReverted
from email.mime.text import MIMEText
from rasa_sdk.forms import FormValidationAction
from actions.database_connectivity import DataUpdateSupportCases

class ActionDefaultFallback(Action):

    def name(self) -> Text:
        return "action_default_fallback"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_please_rephrase")

        return [UserUtteranceReverted()]


class ActionRestart(Action):
    def name(self) -> Text:
        return "action_restart"

    async def run(
        self, dispatcher, tracker: Tracker, domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        return [Restarted()]


class ActionSaveSupportCases(Action):
    def name(self) -> Text:
        return "action_save_support_cases"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        phoneNumber = tracker.get_slot("phoneNumber")
        issue = tracker.get_slot("issue")

        try:
            mydb = mysql.connector.connect(
                host="localhost",
                user="root",
                passwd="root",
                database="db_Tugs"
            )

            with mydb.cursor() as mycursor:
                sql = "SELECT * FROM SupportCases WHERE phoneNumber = %s AND issue = %s"
                val = (phoneNumber, issue)
                mycursor.execute(sql, val)
                result = mycursor.fetchone()

                if result:
                    dispatcher.utter_message("This support case already exists, you will be contacted soon, thank you for the patience.")
                else:
                    DataUpdateSupportCases(name, phoneNumber, issue)
                    dispatcher.utter_message("Support case saved and will be reviewed. You will be contacted shortly, thank you.")
        except mysql.connector.Error as e:
            print(f"Error while querying database: {e}")
        finally:
            mydb.close()

        return []




class ActionSaveComplaints(Action):
    def name(self) -> Text:
        return "action_save_complaints"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = tracker.get_slot("name")
        phoneNumber = tracker.get_slot("phoneNumber")
        complaint = tracker.get_slot("complaint")

        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="root",
            database="db_Tugs"
        )

        mycursor = mydb.cursor()

        sql = "SELECT * FROM Complaints WHERE phoneNumber = %s AND complaint = %s"
        val = (phoneNumber, complaint)

        mycursor.execute(sql, val)

        result = mycursor.fetchone()

        if result:
            dispatcher.utter_message("This complaint case already exists. You will be contacted soon. Thank you for your patience.")
        else:
            sql = "INSERT INTO Complaints (name, phoneNumber, complaint) VALUES (%s, %s, %s)"
            val = (name, phoneNumber, complaint)
            mycursor.execute(sql, val)
            mydb.commit()

            toaddr = "marta.ferreira@devscope.net"
            subject = f"Client {name} Complaint"
            message = f"The client {name} has expressed the cause of dissatisfaction as follows: {complaint}. Therefore, they should be contacted shortly via phone number {phoneNumber}."

            self.send_email(toaddr, subject, message)

            dispatcher.utter_message("Complaint saved and will be reviewed. You will be contacted shortly. Thank you.")

        mydb.close()

        return []

    def send_email(self, toaddr: Text, subject: Text, message: Text) -> None:
        fromaddr = "Tugs@devscope.net"

        msg = MIMEMultipart()
        msg["From"] = fromaddr
        msg["To"] = toaddr
        msg["Subject"] = subject

        body = message if message is not None else ""
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP("smtp_anonimo.devscope.net", 25)
            server.starttls()
            text = msg.as_string()
            server.sendmail(fromaddr, toaddr, text)
            server.quit()
        except Exception as e:
            print("An error occurred while sending email:", str(e))




class ValidateFormComplain(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_complain"

    def validate_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(text="Please provide a name.")
            return {"name": None}
        else:
            # Remove spaces and check if the value contains only alphabetic characters
            cleaned_value = "".join(value.split())  # Remove all spaces
            if not cleaned_value.isalpha():
                dispatcher.utter_message(text="Invalid name. Name should contain only alphabets.")
                return {"name": None}
            else:
                return {"name": cleaned_value}

    def validate_phoneNumber(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(text="Please provide a phone number.")
            return {"phoneNumber": None}
        else:
            if not re.match(r"^\d{9}$", value):
                dispatcher.utter_message(text="Invalid phone number. Phone number should contain 9 digits.")
                return {"phoneNumber": None}
            else:
                return {"phoneNumber": value}

    # Dentro das funções de validação, adicione uma verificação anti-SQL Injection
    def validate_complaint(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        max_char_count = 100  # Maximum character count for the complaint

        if not value:
            dispatcher.utter_message(text="Please provide a complaint.")
            return {"complaint": None}
        else:
            # Verifique se a entrada não contém palavras-chave SQL perigosas
            if any(keyword in value.lower() for keyword in ["drop", "delete", "update", "insert", "alter"]):
                dispatcher.utter_message(text="Invalid complaint. Please avoid using SQL keywords.")
                return {"complaint": None}

            char_count = len(value)
            if char_count > max_char_count:
                dispatcher.utter_message(text=f"The complaint should not exceed {max_char_count} characters.")
                return {"complaint": None}
            else:
                return {"complaint": value}


    def validate_my_form(
        self,
        slot_values: Dict[Text, Any],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # Perform the actual validation for each slot
        validated_slots = {}
        for slot, value in slot_values.items():
            validation_result = self.validate_slot(slot, value, dispatcher, tracker, domain)
            validated_slots.update(validation_result)

        return validated_slots


class ValidateFormSupport(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_support"

    def validate_name(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(text="Please provide a name.")
            return {"name": None}
        else:
            cleaned_value = "".join(value.split())
            if not cleaned_value.isalpha():
                dispatcher.utter_message(text="Invalid name. Name should contain only alphabets.")
                return {"name": None}
            else:
                return {"name": cleaned_value}

    def validate_phoneNumber(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        if not value:
            dispatcher.utter_message(text="Please provide a phone number.")
            return {"phoneNumber": None}
        else:
            if not re.match(r"^\d{9}$", value):
                dispatcher.utter_message(text="Invalid phone number. Phone number should contain 9 digits.")
                return {"phoneNumber": None}
            else:
                return {"phoneNumber": value}

    def validate_issue(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        max_char_count = 100  # Maximum character count for the issue

        if not value:
            dispatcher.utter_message(text="Please provide an issue description.")
            return {"issue": None}
        else:
            # Verifique se a entrada não contém palavras-chave SQL perigosas
            if any(keyword in value.lower() for keyword in ["drop", "delete", "update", "insert", "alter"]):
                dispatcher.utter_message(text="Invalid issue description. Please avoid using SQL keywords.")
                return {"issue": None}

            char_count = len(value)
            if char_count > max_char_count:
                dispatcher.utter_message(text=f"The issue description should not exceed {max_char_count} characters.")
                return {"issue": None}
            else:
                return {"issue": value}

    def validate_my_form(
        self,
        slot_values: Dict[Text, Any],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        # Perform the actual validation for each slot
        validated_slots = {}
        for slot, value in slot_values.items():
            validation_result = self.validate_slot(slot, value, dispatcher, tracker, domain)
            validated_slots.update(validation_result)

        return validated_slots
    
 



