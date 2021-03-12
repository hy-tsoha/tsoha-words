from app import app
from flask import render_template, request, redirect
import decks, users

@app.route("/")
def index():
    return render_template("index.html", decks=decks.get_list())

@app.route("/add", methods=["get", "post"])
def add():
    if request.method == "GET":
        return render_template("add.html")
    if request.method == "POST":
        name = request.form["name"]
        words = request.form["words"]
        deck_id = decks.create(name, words, users.user_id())
        return redirect("/deck/"+str(deck_id))

@app.route("/deck/<int:id>")
def deck(id):
    deck = decks.get_deck(id)
    return render_template("deck.html", name=deck[0], creator=deck[1], size=deck[2])

@app.route("/login", methods=["get", "post"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if users.login(username, password):
            return redirect("/")
        else:
            return render_template("error.html", message="Väärä tunnus tai salasana")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["get","post"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        if password1 != password2:
            return render_template("error.html", message="Salasanat eroavat")
        role = request.form["role"]
        if role != "1" and role != "2":
            return render_template("error.html", message="Tuntematon käyttäjärooli")
        if users.register(username, password1, role):
            return redirect("/")
        else:
            return render_template("error.html", message="Rekisteröinti ei onnistunut")
