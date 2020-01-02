import os, queue
import json
from flask import Flask, session, request,render_template, redirect,jsonify
from flask_session import Session
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import scoped_session , sessionmaker
from models import *
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from datetime import datetime,timedelta
import re

app=Flask(__name__)

# Check for environment variable
'''if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
'''
app.config["SESSION_PERMANENT"]=False
app.config["SESSION_TYPE"]='filesystem'
Session(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


#engine=create_engine(os.getenv("DATABASE_URL"))
#db=scoped_session(sessionmaker(bind=engine))
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql://postgres:ranjana99@localhost:5432/postgres" #os.getenv(DATABASE_URL)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db.init_app(app)
'''
users={}        #{"username":"password", ...}
display={}      #{"username":"display_name", ...}
channels={}     #{"username":[ch1,ch2,...], ...}
messages={}     #{"channel":[{message,username}, .. , ...]}
'''

@socketio.on('join')
def on_join(data):
    username=session['user']
    room=data['room']
    join_room(room)
    user_id=User.query.filter_by(username=username).first().user_id
    channel=Channel.query.filter_by(channel=room).first()
    if channel is None:
        channel=Channel(channel=room)
        db.session.add(channel)
        db.session.commit()
    channel_id=channel.id
    if Member.query.filter(and_(Member.user_id==user_id,Member.channel_id==channel_id)).first() is None:
        member=Member(user_id=user_id,channel_id=channel_id)
        db.session.add(member)
        db.session.commit()
        data={'message':User.query.filter_by(username=username).first().display_name + " joined.", "room":room}
    else:
        data={'message':User.query.filter_by(username=username).first().display_name + "  already in "+room+".", "room":room}

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
    chat={}

    channel_id=Channel.query.filter_by(channel=data['room']).first().id
    user_id=User.query.filter_by(username=username).first().user_id
    newMessage=Message(channel_id=channel_id,user_id=user_id,message=message)
    db.session.add(newMessage)
    db.session.commit()
    chat={"message":newMessage.message,"user":User.query.get(newMessage.user_id).display_name,"room":Channel.query.get(newMessage.channel_id).channel,"time":now }
    emit('receive mesage', chat,room=room)
    '''except:
        emit('receive mesage', chat,room=room)
    '''


@app.route('/', methods=["POST","GET"])
def index():

    if request.method=="POST":
        dn=request.form.get('display_name')
        User.query.filter_by(username=session['user']).first().display_name=dn
        db.session.commit()
        #done

    if 'user' in session:
        if User.query.filter_by(username=session['user']).first().display_name is None:
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
        display_name=request.form.get("display_name")
        emailPattern=re.compile("^[a-zA-Z][a-zA-Z0-9_]*(\.[a-zA-Z0-9_]+)*@([a-zA-Z][a-zA-Z0-9_]*)(\.[a-zA-Z0-9_]+)+$")
        try:
            if bool(emailPattern.match(username)):
                if username.lower()!='admin' and User.query.filter_by(username=username).first() is None:
                    user=User(username=username,password=password,display_name=display_name)
                    db.session.add(user)
                    db.session.commit()
                    session['user']=username
                    return redirect('/verify')
                    return render_template('verify.html')
                else:
                    return render_template("signup.html", message="*Username already exists.")
            else:
                return render_template("signup.html", message="*Username is invalid.")
        except:
            render_template("signUp.html", message="Something went wrong.")
    return render_template("signup.html")

@app.route('/verify', methods=['POST','GET'])
def verification():
    if request.method=="POST":
        try:
            otp=int(request.form.get("otp"))
            user_id=User.query.filter_by(username=session['user']).first().user_id
            fetchedOtp=OTP.query.filter(and_(OTP.user_id==user_id,OTP.value==otp)).first()
            if fetchedOtp is None:
                return jsonify({'success':False, 'message': "OTP didn't match."})
            dttm=fetchedOtp.dttm
            if (dttm+timedelta(minutes=5))>datetime.now():
                User.query.filter_by(username=session['user']).first().verified=True
                db.session.commit()
                return jsonify({'success':True})
            else:
                return jsonify({'success':False, 'message': "OTP expired"})
        except:
            return jsonify({'succes':False,'message':"Invalid OTP"})
    if 'user' in session:
        if User.query.filter_by(username=session['user']).first().verified:
            return "Already verified.<br><a href='/'>Home</a>"

        #Generate OTP here
        otp=OTP(user_id=User.query.filter_by(username=session['user']).first().user_id,value=random.randrange(100001,999998),dttm=datetime.now())
        db.session.add(otp)
        db.session.commit()
        #Send otp
        port=465
        password="ranjana99"

        context=ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
            server.login("biltu1610@gmail.com",password)
            sender_email="you@gmail.com"
            receiver_email=User.query.filter_by(username=session['user']).first().username
            message=MIMEMultipart("alternative")
            message["subject"]="Verification OTP"
            message['from']=sender_email
            message['to']=receiver_email
            otp=otp.value
            text="""
            FLACK OTP for verfication is {otp} and will be expired in 5 minutes.
            """
            html = f"""\
            <html>
            <body>
                <p>
                FLACK OTP for verification is: {otp} <br>and will be expired in 5 minutes.
                </p>
            </body>
            </html>
            """
            part1=MIMEText(text,"plain")
            part2=MIMEText(html,"html")
            message.attach(part1)
            message.attach(part2)

            server.sendmail(sender_email,receiver_email,message.as_string())



        return render_template("verify.html")
    return redirect('/login')



@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/login', methods=['POST','GET'])
def login():
    if 'user' in session:
        if User.query.filter_by(username=session['user']).first().verified:
            return "Already logged in as "+session['user']+"<br><a href='/'>Home</a>"
        else:
            return redirect('/verify')

    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if User.query.filter(and_(User.username==username,User.password==password)).first() :
            session['user']=username
            if User.query.filter_by(username=session['user']).first().verified:
                return "Successfully Logged in as "+session['user']+"<br><a href='/'>Home</a>"
            else:
                return redirect('/verify')

        else:
            return render_template('login.html',message="Username oorr Password doesn't match.", username=username)

    return render_template('login.html')


@app.route('/chat/<string:room>')
def chat_room(room):
    if 'user' in session:
        room=room.replace("%20"," ")
        return render_template("chat.html",room=room, user=User.query.filter_by(username=session['user']).first().display_name)
    return "Please Sign In first.<br><a href='/login'>Click here to Sign In</a>"


@app.route('/display_name', methods=["POST","GET"])   #check here!!!
def display_name():
    try:
        dis_name=User.query.filter_by(username=session['user']).first().display_name
        if dis_name is None:
            return jsonify({"success":False})
            # changes to make display_name
        return jsonify({"success":True,"display_name":dis_name})
    except:

        return jsonify({"success":False})

@app.route('/channel_list',methods=["GET","POST"])
def channel_list():
    #user_id= User.query.filter_by(username=session['user']).first().user_id
    #channel_ids=Member.query.filter_by(user_id=user_id).with_entities(Member.channel_id)
    #channels=Channel.query.filter(Channel.id.in_(channel_ids)).all()
    channels=User.query.filter_by(username=session['user']).first().channels
    channel_names=[]
    for c in channels:
        channel_names.append(c.channel)
    '''channels=[]
    #return jsonify({"success":False})
    for id in channel_ids:
        if Channel.query.get(id) is not None:
            channels.append(Channel.query.get(id).channel)
    '''

    if len(channel_names)==0:
        return jsonify({"success":False})

    return jsonify({"success":True, "channels": channel_names })


@app.route('/chats', methods=['POST',"GET"])
def chat():
    room=request.form.get("roomname")
    channel_id=Channel.query.filter_by(channel=room).first().id
    messages=Message.query.filter_by(channel_id=channel_id).all()
    message=[]
    for m in messages:
        message.append({"message":m.message,"user":User.query.get(m.user_id).display_name,"room":Channel.query.get(m.channel_id).channel,"time":datetime.now().strftime("%I:%M %p")})
    if message is not None:
        return jsonify({"success":True, "message": message })
    return jsonify({"success":False})
def main():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        main()
    socketio.run(app)
