import json
import database
import database
import main


with open('./rule.json') as json_file:
    data = json.load(json_file)
    
rule_level_predicate = data["All_or_Any"]
conditions=data["Conditions"]

string_predicate={
        "contains":"LIKE",
        "not contains":"NOT LIKE",
        "equal":"=",
        "not equal":"!=",
        "Less than":"<=",
        "Greater than":">="
    }


def take_action(action,mail_ids):
    service,user_id,label_ids,status=main.GmailCredential()
    msg_labels= [action]   # choose any between STARRED, IMPORTANT ,UNREAD, SPAM, TRASH
    for msg_id in mail_ids:
        main.ModifyMessage(service=service, user_id=user_id, msg_id=msg_id,  msg_labels=msg_labels)
        
    return True


action_mail_ids_map = {condition["Action"]: [] for condition in conditions}
condition_met_count = 0

for i in conditions:

    field_name = i["Field_name"]
    predicate = i["Predicate"]
    value = i["Value"]
    action = i["Action"]

    if all([field_name,predicate,value,action]):
        if field_name != "Date":
            value="'%"+value+"%'"
            operator = string_predicate[predicate]
            mail_data=database.select_data(field_name,operator,value)
        else:
            value="-"+value
            operator = string_predicate[predicate]
            mail_data=database.date_query(operator,value)

        mail_ids=[i[-1] for i in mail_data]
        print(len(mail_ids))

        if mail_ids:
            condition_met_count += 1
            action_mail_ids_map[action].extend(mail_ids)
    else:
        print("Check the rule.json script")
        break

if rule_level_predicate == "any":
    for action, mail_ids in action_mail_ids_map.items():
        take_action(action,mail_ids)
elif rule_level_predicate == "all" and condition_met_count == len(conditions):
    for action, mail_ids in action_mail_ids_map.items():
        take_action(action,mail_ids)
else:
    print("-------------------------")
    print("All conditions are not met, actions will not be taken.")
    print("-------------------------")

print("\nProgram has been executed!!!!\n")
print("-------------------------")