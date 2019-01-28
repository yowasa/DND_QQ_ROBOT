class User:
    def __init__(self, context):
        self.user_id = context.get('user_id')
        self.current_character = context.get('current_character')
        self.jrrp = context.get('jrrp')
        self.jrrp_date = context.get('jrrp_date')
        self.user_list = context.get('user_list')
