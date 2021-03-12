from db import db
from random import randint

def get_decks():
    sql = "SELECT id, name FROM decks WHERE visible=1 ORDER BY name"
    return db.session.execute(sql).fetchall()

def get_deck_info(id):
    sql = "SELECT d.name, u.name FROM decks d, users u WHERE d.id = :id AND d.creator_id = u.id"
    return db.session.execute(sql, {"id": id}).fetchone()

def get_deck_size(id):
    sql = "SELECT COUNT(*) FROM cards WHERE deck_id = :id"
    return db.session.execute(sql, {"id": id}).fetchone()[0]

def get_my_decks(user_id):
    sql = "SELECT id, name FROM decks WHERE creator_id=:user_id AND visible=1 ORDER BY name"
    return db.session.execute(sql, {"user_id":user_id}).fetchall()

def remove_deck(deck_id, user_id):
    sql = "UPDATE decks SET visible=0 WHERE id=:id AND creator_id=:user_id"
    db.session.execute(sql, {"id":deck_id, "user_id":user_id})
    db.session.commit()

def get_random_card(deck_id):
    size = get_deck_size(deck_id)
    pos = randint(0, size-1)
    sql = "SELECT id, word1 FROM cards WHERE deck_id=:deck_id LIMIT 1 OFFSET :pos"
    return db.session.execute(sql, {"deck_id":deck_id, "pos":pos}).fetchone()

def get_card_words(id):
    sql = "SELECT word1, word2 FROM cards WHERE id=:id"
    return db.session.execute(sql, {"id":id}).fetchone()

def add_deck(name, words, creator_id):
    sql = "INSERT INTO decks (creator_id, name, visible) VALUES (:creator_id, :name, 1) RETURNING id"
    deck_id = db.session.execute(sql, {"creator_id":creator_id, "name":name}).fetchone()[0]

    for pair in words.split("\n"):
        parts = pair.strip().split(";")
        if len(parts) != 2:
            continue

        sql = "INSERT INTO cards (deck_id, word1, word2) VALUES (:deck_id, :word1, :word2)"
        db.session.execute(sql, {"deck_id":deck_id, "word1":parts[0], "word2":parts[1]})

    db.session.commit()
    return deck_id

def send_answer(card_id, answer, user_id):
    sql = "SELECT word2 FROM cards WHERE id=:id"
    correct = db.session.execute(sql, {"id":card_id}).fetchone()[0]
    result = 1 if answer == correct else 0
    sql = "INSERT INTO answers (user_id, card_id, sent_at, result) VALUES (:user_id, :card_id, NOW(), :result)"
    db.session.execute(sql, {"user_id":user_id, "card_id":card_id, "result":result})
    db.session.commit()

def get_reviews(deck_id):
    sql = "SELECT u.name, r.stars, r.comment FROM reviews r, users u WHERE r.user_id=u.id AND r.deck_id=:deck_id ORDER BY r.id"
    return db.session.execute(sql, {"deck_id": deck_id}).fetchall()

def add_review(deck_id, user_id, stars, comment):
    sql = "INSERT INTO reviews (deck_id, user_id, stars, comment) VALUES (:deck_id, :user_id, :stars, :comment)"
    db.session.execute(sql, {"deck_id":deck_id, "user_id":user_id, "stars":stars, "comment":comment})
    db.session.commit()
