import os, queue

from flask import Flask, session, request,render_template, redirect,jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

app=Flask(__name__)

app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
Session(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


users={}        #{"username":"password", ...}
display={}      #{"username":"display_name", ...}
channels={}     #{"username":[ch1,ch2,...], ...}
messages={}     #{"channel":[{message,username}, .. , ...]}


@socketio.on('join')
def on_join(data):
    username=session['user']
    room=data['room']
    join_room(room)
    if username in channels.keys():
        if room not in channels[username]:
            channels[username].append(room)
            data={'message':display[username] + " joined.", "room":room}
        else:
            data={'message':display[username] + "already in "+room+".", "room":room}
    else:
        channels[username]=[room]
        data={'message':display[username] + " joined.", "room":room}
    emit('join status', data, room=room)


@socketio.on('leave')
def on_leave(data):
    username=session['user']
    room=data['room']
    leave_room(room)
    channels[username].remove(room)
    data={'message':display[username] + " left.", "room":room}
    emit('leave status', data, room=room)


@socketio.on("send message")
def on_send_message(data):
    message=data["message"]
    username=session['user']
    room=data['room']
    now = datetime.now().strftime("%I:%M %p")

    chat={"message":message,"user":display[username], "room":room, "time":now}
    if room in messages.keys():
        messages[room].append(chat)
    else:
        messages[room]=[chat]
    emit('receive mesage', chat,room=room)


@app.route('/', methods=["POST","GET"])
def index():

    if request.method=="POST":
        dn=request.form.get('display_name')
        display[session['user']]=dn

    if 'user' in session:
        if session['user'] not in display.keys():
            return render_template('display.html')
        return render_template('index.html')
    return render_template('homepage.html')


@app.route('/signup', methods=["POST","GET"])
def signup():
    if 'user' in session:
        return "Already logged in as "+session['user']
    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")


        global users

        if username.lower()!='admin' and username not in users.keys():
            users[username]=password
        else:
            return render_template("signup.html", message="*Username already exists.")
        return render_template('regstatus.html')
    return render_template("signup.html")



@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/login', methods=['POST','GET'])
def login():
    if 'user' in session:
        return "Already logged in as "+session['user']+"<br><a href='/'>Home</a>"

    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        try:
            if users[username]==password:
                session['user']=username
                return "Successfully Logged in as "+session['user']+"<br><a href='/'>Home</a>"
            else:
                return render_template('login.html',message="Username or Password doesn't match.", username=username)
        except:
            return render_template('login.html',message="Username or Password doesn't match.", username=username)

    return render_template('login.html')


@app.route('/chat/<string:room>')
def chat_room(room):
    if 'user' in session:
        room=room.replace("%20"," ")
        return render_template("chat.html",room=room, user=display[session['user']])
    return "Please Sign In first.<br><a href='/login'>Click here to Sign In</a>"


@app.route('/display_name', methods=["POST","GET"])   #check here!!!
def display_name():
    try:
        dis_name=display[session['user']]
        if dis_name is None:
            return jsonify({"success":False})
            # changes to make display_name
        return jsonify({"success":True,"display_name":dis_name})
    except:

        return jsonify({"success":False})

@app.route('/channel_list',methods=["GET","POST"])
def channel_list():
    try:
        channel_list=channels[session['user']]
        if channel_list is None:
            return jsonify({"success":False})
        return jsonify({"success":True, "channels": channel_list})
    except:
        return jsonify({"success":False})

@app.route('/chats', methods=['POST',"GET"])
def chat():
    room=request.form.get("roomname")
    if room in messages.keys():
        return jsonify({"success":True, "message": messages[room]})
    return jsonify({"success":False})


if __name__ == '__main__':
    socketio.run(app)
