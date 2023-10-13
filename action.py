import json
import database
from database import DatabaseService
import main
from main import GmailService

string_predicate = {

    "contains":"LIKE",
    "not contains":"NOT LIKE",
    "equal":"=",
    "not equal":"!=",
    "Less than":"<=",
    "Greater than":">="
}

class MailActionService:


    def __init__(self) -> None:
        pass

    def import_rules_and_predicates_values(self) -> None:

        with open('./rule.json') as json_file:
            data = json.load(json_file)
            
        self.rule_level_predicate = data["All_or_Any"]
        self.conditions=data["Conditions"]


    def take_action_on_mail(self, action: str, mail_ids: int) -> bool:
        service,user_id,label_ids,status=GmailService().initialize_gmail_credentials()
        msg_labels= [action]   # choose any between STARRED, IMPORTANT ,UNREAD, SPAM, TRASH
        for msg_id in mail_ids:
            GmailService().modify_email(service=service, user_id=user_id, msg_id=msg_id,  msg_labels=msg_labels)
            
        return True

    def execute(self) -> None:

        self.import_rules_and_predicates_values()

        action_mail_ids_map = {condition["Action"]: [] for condition in self.conditions}
        condition_met_count = 0

        for condition in self.conditions:

            field_name = condition["Field_name"]
            predicate = condition["Predicate"]
            value = condition["Value"]
            action = condition["Action"]

            if all([field_name,predicate,value,action]):
                if field_name != "Date":
                    value="'%"+value+"%'"
                    operator = string_predicate[predicate]
                    mail_data=DatabaseService().build_and_execute_query(field_name=field_name, operator=operator, value=value)
                else:
                    value="-"+value
                    operator = string_predicate[predicate]
                    mail_data=DatabaseService().build_and_execute_date_query(operator=operator,value=value)

                mail_ids=[i[-1] for i in mail_data]
                print(len(mail_ids))

                if mail_ids:
                    condition_met_count += 1
                    action_mail_ids_map[action].extend(mail_ids)
            else:
                print("Check the rule.json script")
                break

        if self.rule_level_predicate == "any":
            for action, mail_ids in action_mail_ids_map.items():
                self.take_action_on_mail(action=action, mail_ids=mail_ids)
        elif self.rule_level_predicate == "all" and condition_met_count == len(self.conditions):
            for action, mail_ids in action_mail_ids_map.items():
                self.take_action_on_mail(action=action, mail_ids=mail_ids)
        else:
            print("-------------------------")
            print("All self.conditions are not met, actions will not be taken.")
            print("-------------------------")

        print("\nProgram has been executed!!!!\n")
        print("-------------------------")


MailActionService().execute()