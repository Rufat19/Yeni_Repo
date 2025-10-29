from handlers.db_utils import get_balance, set_balance

def add_balance(user_id, amount):
    current = get_balance(user_id)
    set_balance(user_id, current + amount)