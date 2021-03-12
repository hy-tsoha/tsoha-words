from db import db

def get_my_stats(deck_id, user_id):
    sql = "SELECT COUNT(*), COALESCE(SUM(a.result),0) FROM answers a, cards c WHERE c.deck_id=:deck_id AND a.user_id=:user_id AND a.card_id=c.id"
    return db.session.execute(sql, {"deck_id":deck_id, "user_id":user_id}).fetchone()
