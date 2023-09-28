import json
import pickle
import os.path
import base64
import email
import re
import database
import time
import sys

import database
import main






with open('./rule.json') as json_file:
    data = json.load(json_file)
    

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
    msg_labels="Test"
    for msg_id in mail_ids:
        main.ModifyMessage(service, user_id,msg_id,  msg_labels)
        
    return True






for i in conditions:
    # print(i)
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
        take_action(action,mail_ids)

        print("Program has been executed!!!!")
        print("-------------------------")
    
    else:
        print("Check the rule.json script")
        break
