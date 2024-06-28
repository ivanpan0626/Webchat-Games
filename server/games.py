from flask import render_template, request, session, redirect, jsonify, url_for, Blueprint
from flask_socketio import join_room, leave_room, send, emit
from flask_login import login_required, current_user
from . import socketio, db

games = Blueprint('games', __name__)

@games.route("/games/2048")
def game2048():
    room = session.get("room")
    return render_template("2048.html", room=room)

@games.route("/games/highscores")
@login_required
def highscores():
    hs2048 = current_user.hs2048
    return render_template("highscores.html", hs2048=hs2048, user=current_user)

@games.route("/games/2048/score", methods=["POST"])
def score2048():
    score = int(request.json.get("score"))
    room = request.json.get("room")
    if current_user.is_authenticated:
        if current_user.hs2048 < score:
            current_user.hs2048 = score
            db.session.commit()
        else:
            print("Lol loser!")
    
    name = session.get("name")
    content = {
        "score": score, 
        "name": name
        }
    
    socketio.emit('reportScore', content, to=room)
    return jsonify({"message": "recieved"})