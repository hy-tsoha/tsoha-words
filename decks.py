from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

def get_list():
    sql = "SELECT id, name FROM decks ORDER BY name"
    return db.session.execute(sql).fetchall()

def get_deck(id):
    sql = "SELECT d.name, u.name FROM decks d, users u WHERE d.id = :id AND d.creator_id = u.id"
    info = db.session.execute(sql, {"id": id}).fetchone()

    sql = "SELECT COUNT(*) FROM cards WHERE deck_id = :id"
    size = db.session.execute(sql, {"id": id}).fetchone()

    return (info[0], info[1], size[0])

def create(name, words, creator_id):
    sql = "INSERT INTO decks (creator_id, name) VALUES (:creator_id, :name) RETURNING id"
    deck_id = db.session.execute(sql, {"creator_id":creator_id, "name":name}).fetchone()[0]

    for pair in words.split("\n"):
        parts = pair.strip().split(";")
        if len(parts) != 2:
            continue

        sql = "INSERT INTO cards (deck_id, word1, word2) VALUES (:deck_id, :word1, :word2)"
        db.session.execute(sql, {"deck_id":deck_id, "word1":parts[0], "word2":parts[1]})

    db.session.commit()
    return deck_id
