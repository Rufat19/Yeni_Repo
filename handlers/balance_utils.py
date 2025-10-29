from handlers.db_utils import get_balance, set_balance

def add_balance(user_id, amount):
    current = get_balance(user_id)
    set_balance(user_id, current + amount)

def deduct_balance(user_id, amount):
    """Deduct specified amount from user balance. Returns True if successful, False if insufficient balance."""
    current = get_balance(user_id)
    if current >= amount:
        set_balance(user_id, current - amount)
        return True
    return False