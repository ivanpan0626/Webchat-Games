from flask import render_template, request, session, redirect, jsonify, url_for, Blueprint
from flask_socketio import join_room, leave_room, send, emit
from flask_login import login_required, current_user
import random
from string import ascii_uppercase
from . import socketio, db
from .models import User

chat = Blueprint('chat', __name__)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)

        if code not in rooms:
            break

    return code

@chat.route("/", methods=['POST', 'GET'])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", user=current_user, error="Please enter a Name!", code=code, name=name)
        if join != False and not code:
            return render_template("home.html", user=current_user, error="Please enter a Room Code!", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {
                "members": 0,
                "messages": []
                }
        elif code not in rooms:
            return render_template("home.html", user=current_user, error="Room does not exist!", code=code, name=name)
        
        session["room"] = room
        if current_user.is_authenticated:
            session["name"] = current_user.username
        else:
            session["name"] = name

        return redirect(url_for("chat.room", user=current_user))
        
    return render_template("home.html", user=current_user)

@chat.route("/games/2048")
def game2048():
    return render_template("2048.html", user=current_user)

@chat.route("/games/2048/score", methods=["POST"])
def score2048():
    score = request.json.get("score")
    if current_user.is_authenticated:
        current_user.hs2048 = score
    
    name = session.get("name")
    socketio.emit("reportScore", {"score": score, "name": name})
    return jsonify({"message": "recieved"})

@chat.route('/room')
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("chat.home"))
    
    return render_template("room.html", user=current_user, code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get("name")} said: {data['data']}")

@socketio.on("initGame")
def initGame(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    content = {
        "name": session.get("name"),
        "game": data["game"]
    }
    socketio.emit('initGame', content)
    rooms[room]["messages"].append({"name": session.get("name"), "message": "EXPIRED GAMELINK"})
    print(f"{session.get("name")} started: {data['game']}")

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")

    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")