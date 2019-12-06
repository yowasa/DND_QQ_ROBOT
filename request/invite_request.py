from filter import *

def handle_invite_request(content):
    user_id= content["user_id"]
    user=get_user(user_id)
    if user.level>=10:
        return True
    else:
        return False