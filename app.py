import os, queue
import json
from flask import Flask, session, request,render_template, redirect,jsonify, abort
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
from  flask_mail import Mail, Message

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

mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = '***REMOVED***'
app.config['MAIL_PASSWORD'] = '***REMOVED***'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True



mail=Mail(app)

#engine=create_engine(os.getenv("DATABASE_URL"))
#db=scoped_session(sessionmaker(bind=engine))
app.config["SQLALCHEMY_DATABASE_URI"]= os.getenv("DATABASE_URL") #"***REMOVED***
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False

db.init_app(app)


@socketio.on('join')
def on_join(data):
    username=session['user']
    room = data['room']
    if User.query.filter_by(username=session['user']).first().verified and len(room)>0 and room!="undefined":

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
            data={'display_name':User.query.filter_by(username=username).first().display_name, "room":room}
            emit('join status', data, room=room)
        #else:
        #    data={'message':User.query.filter_by(username=username).first().display_name + "  already in "+room+".", "room":room}




@socketio.on('leave')
def on_leave(data):
    username=session['user']
    room=data['room']
    if User.query.filter_by(username=username).first().verified and room in [c.channel for c in User.query.filter_by(username=session['user']).first().channels]:
        member=Member.query.filter(and_(Member.user_id==(User.query.filter_by(username=username).first().user_id),
        Member.channel_id==(Channel.query.filter_by(channel=room).first().id ) )).first()
        db.session.delete(member)
        db.session.commit()
        data = {'display_name':User.query.filter_by(username=session['user']).first().display_name, "room": room}
        print("You left")
        emit('leave status', data, room=room)
        leave_room(room)
        print("status has been sent")


@socketio.on("send message")
def on_send_message(data):
    message=data["message"]
    username=session['user']
    room=data['room']
    print("Mesage received")
    if User.query.filter_by(username=session['user']).first().verified and room in [c.channel for c in User.query.filter_by(username=session['user']).first().channels]:

        now = datetime.now().strftime("%I:%M %p")
        chat={}

        channel_id=Channel.query.filter_by(channel=data['room']).first().id
        user_id=User.query.filter_by(username=username).first().user_id
        newMessage=Message(channel_id=channel_id,user_id=user_id,message=message)
        db.session.add(newMessage)
        db.session.commit()
        chat={"message":newMessage.message,"user":User.query.get(newMessage.user_id).display_name, "room":Channel.query.get(newMessage.channel_id).channel,"time":newMessage.dttm.strftime("%I:%M %p") }
        print("Debug: mesage will be sent")
        join_room(room)
        emit('receive message', chat,room=room)



@app.route('/')
def index():

    '''if request.method=="POST":
        dn=request.form.get('display_name')
        User.query.filter_by(username=session['user']).first().display_name=dn
        db.session.commit()
        #done
    '''

    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()
        if not user.verified:
            return redirect('/verify')
        return redirect('/chat')
        #return render_template('profile.html',display_name=user.display_name, username=user.username)
    return render_template('homepage.html')


@app.route('/signup', methods=["POST","GET"])
def signup():
    if 'user' in session:
        return render_template('loginstatus.html',message="Already logged in as "+session['user']+".")
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
            return render_template('loginstatus.html',message="Already verified.")

        #Generate OTP here
        try:
            otp=OTP(user_id=User.query.filter_by(username=session['user']).first().user_id, value=random.randrange(100001,999998),dttm=datetime.now())
            db.session.add(otp)
            db.session.commit()
            #Send otp
            port=465
            password="***REMOVED***"
            msg=Message(f"Hello {otp.value}",sender="***REMOVED***",recipients=[f"{User.query.filter_by(username=session['user']).first().username}"])
            mail.send(msg)


            '''context=ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com",port,context=context) as server:
                server.login("***REMOVED***",password)
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
            '''
            return render_template("verify.html")
        except:
            abort(503)

    return redirect('/login')
@app.errorhandler(503)
def internal_error(error):
    if 'user' in session:
        User.query.filter_by(username=session['user']).first().verified=True
        db.session.commit()
        return redirect('/')
    return "Iternal server Error",503


@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

@app.route('/login', methods=['POST','GET'])
def login():
    if 'user' in session:
        if User.query.filter_by(username=session['user']).first().verified:
            return render_template('loginstatus.html',message="Already logged in as "+session['user']+".")
        else:
            return redirect('/verify')

    if request.method=="POST":
        username=request.form.get("username")
        password=request.form.get("password")
        if User.query.filter(and_(User.username==username,User.password==password)).first() :
            session['user']=username
            if User.query.filter_by(username=session['user']).first().verified:
                return render_template('loginstatus.html',message="Successfully Logged in as "+session['user']+".")
                return
            else:
                return redirect('/verify')

        else:
            return render_template('login.html',message="Username oorr Password doesn't match.", username=username)

    return render_template('login.html')


@app.route('/chat')
def chat_room():
    if 'user' in session:
        if not User.query.filter_by(username=session['user']).first().verified:
            return redirect('/verify')
        #room=room.replace("%20"," ")
        #if (Channel.query.filter_by(channel=room).first() is None):
        #    abort(404)
        #if (room not in ([c.channel for c in User.query.filter_by(username=session['user']).first().channels])):
        #    abort(403)
        user=User.query.filter_by(username=session['user']).first()
        return render_template("chat.html", user=user.display_name, username=user.username)
    return "Please Sign In first.<br><a href='/login'>Click here to Sign In</a>"


@app.route('/display_name', methods=["POST"])   #check here!!!
def display_name():
    try:
        dis_name=User.query.filter_by(display_name=request.form.get('display_name')).first()
        if dis_name is None:
            return jsonify({"success":True})
            # changes to make display_name
        return jsonify({"success":False})
    except:

        return jsonify({"success":False})


@app.route('/channel_list',methods=["POST"])
def channel_list():
    #user_id= User.query.filter_by(username=session['user']).first().user_id
    #channel_ids=Member.query.filter_by(user_id=user_id).with_entities(Member.channel_id)
    #channels=Channel.query.filter(Channel.id.in_(channel_ids)).all()
    if 'user' in session:
        channels = User.query.filter_by(username=session['user']).first().channels
        channel_names = []
        for c in channels:
            channel_names.append(c.channel)
        if len(channel_names)==0:
            return jsonify({"success":False})

        return jsonify({"success":True, "channels": channel_names })
    else:
        return jsonify({"success": False})


@app.route('/groupname',methods=["POST"])
def groupname():
    if 'user' in session:
        room=request.form.get('room')
        for c in Channel.query.all():
            if room==c.channel:
                return jsonify({"success":True})
        return jsonify({"success": False})
    return jsonify({"success": False})

@app.route('/chats', methods=['POST'])
def chat():
    if 'user' in session:
        if not User.query.filter_by(username=session['user']).first().verified:
            return jsonify({"success":False})
        room=request.form.get("roomname")
        if (Channel.query.filter_by(channel=room).first() is None):
            abort(404)
        if (room not in ([c.channel for c in User.query.filter_by(username=session['user']).first().channels])):
            abort(403)
        channel_id=Channel.query.filter_by(channel=room).first().id
        messages=Message.query.filter_by(channel_id=channel_id).all()
        message=[]
        for m in messages:
            message.append({"message":m.message,"user":User.query.get(m.user_id).display_name,
            "room":Channel.query.get(m.channel_id).channel,"time":m.dttm.strftime("%I:%M %p")})
        if message is not None:
            return jsonify({"success":True, "message": message })
        return jsonify({"success":False})
    else:
        return jsonify({"success":False})




def main():
    db.create_all()

if __name__ == '__main__':
    with app.app_context():
        main()
    socketio.run(app)
