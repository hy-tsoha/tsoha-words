from app import app
from flask import render_template, request, redirect
import decks
import stats
import users

@app.route("/")
def index():
    return render_template("index.html", decks=decks.get_all_decks())

@app.route("/add", methods=["get", "post"])
def add_deck():
    users.require_role(2)

    if request.method == "GET":
        return render_template("add.html")

    if request.method == "POST":
        users.check_csrf()

        name = request.form["name"]
        if len(name) < 1 or len(name) > 20:
            return render_template("error.html", message="Nimessä tulee olla 1-20 merkkiä")

        words = request.form["words"]
        if len(words) > 10000:
            return render_template("error.html", message="Sanalista on liian pitkä")

        deck_id = decks.add_deck(name, words, users.user_id())
        return redirect("/deck/"+str(deck_id))

@app.route("/remove", methods=["get", "post"])
def remove_deck():
    users.require_role(2)

    if request.method == "GET":
        my_decks = decks.get_my_decks(users.user_id())
        return render_template("remove.html", list=my_decks)

    if request.method == "POST":
        users.check_csrf()

        if "deck" in request.form:
            deck = request.form["deck"]
            decks.remove_deck(deck, users.user_id())

        return redirect("/")

@app.route("/deck/<int:deck_id>")
def show_deck(deck_id):
    info = decks.get_deck_info(deck_id)
    size = decks.get_deck_size(deck_id)

    total, correct = stats.get_deck_stats(deck_id, users.user_id())

    reviews = decks.get_reviews(deck_id)

    return render_template("deck.html", id=deck_id, name=info[0], creator=info[1], size=size,
                           total=total, correct=correct, reviews=reviews)

@app.route("/review", methods=["post"])
def review():
    users.require_role(1)
    users.check_csrf()

    deck_id = request.form["deck_id"]

    stars = int(request.form["stars"])
    if stars < 1 or stars > 5:
        return render_template("error.html", message="Virheellinen tähtimäärä")

    comment = request.form["comment"]
    if len(comment) > 1000:
        return render_template("error.html", message="Kommentti on liian pitkä")
    if comment == "":
        comment = "-"

    decks.add_review(deck_id, users.user_id(), stars, comment)

    return redirect("/deck/"+str(deck_id))

@app.route("/play/<int:deck_id>")
def play(deck_id):
    users.require_role(1)

    card = decks.get_random_card(deck_id)
    return render_template("play.html", deck_id=deck_id, card_id=card[0], question=card[1])

@app.route("/result", methods=["post"])
def result():
    users.require_role(1)
    users.check_csrf()

    deck_id = request.form["deck_id"]
    card_id = request.form["card_id"]
    answer = request.form["answer"].strip()

    decks.send_answer(card_id, answer, users.user_id())
    words = decks.get_card_words(card_id)

    return render_template("result.html", deck_id=deck_id, question=words[0],
                           answer=answer, correct=words[1])

@app.route("/login", methods=["get", "post"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not users.login(username, password):
            return render_template("error.html", message="Väärä tunnus tai salasana")
        return redirect("/")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["get", "post"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        if len(username) < 1 or len(username) > 20:
            return render_template("error.html", message="Tunnuksessa tulee olla 1-20 merkkiä")

        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        if password1 == "":
            return render_template("error.html", message="Salasana on tyhjä")

        role = request.form["role"]
        if role not in ("1", "2"):
            return render_template("error.html", message="Tuntematon käyttäjärooli")

        if not users.register(username, password1, role):
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
        return redirect("/")

@app.route("/stats")
def show_stats():
    users.require_role(2)

    data = stats.get_full_stats(users.user_id())
    return render_template("stats.html", data=data)
