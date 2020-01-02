from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    __tablename__="users"
    user_id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True, nullable=False) #add nullable=False
    password=db.Column(db.String,nullable=False)
    display_name=db.Column(db.String)
    verified=db.Column(db.Boolean,default=False)
    channels=db.relationship("Channel",secondary="members",backref=db.backref("users"))



class Member(db.Model):
    __tablename__="members"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey("users.user_id"),nullable=False)
    channel_id=db.Column(db.Integer,db.ForeignKey("channels.id"),nullable=False)

    #user=db.relationship("User",backref=db.backref("members",cascade="all, delete-orphan"))
    #channel=db.relationship("Channel",backref=db.backref("members",cascade="all, delete-orphan"))


class Channel(db.Model):
    __tablename__="channels"
    #username=db.Column(db.String,db.ForeignKey("users.username"),nullable=False)
    id=db.Column(db.Integer,primary_key=True)
    channel=db.Column(db.String, nullable=False)
    #users=db.relationship("User",secondary="members")

class Message(db.Model):
    __tablename__="messages"
    id=db.Column(db.Integer,primary_key=True)
    channel_id=db.Column(db.Integer,db.ForeignKey("channels.id"),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.user_id"),nullable=False)
    message=db.Column(db.String(255),nullable=False)
    dttm=db.Column(db.DateTime,server_default=db.func.current_timestamp())

class OTP(db.Model):
    __tablename__="otps"
    id=db.Column(db.Integer,primary_key=True)
    value=db.Column(db.Integer,nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("users.user_id"),nullable=False)
    dttm=db.Column(db.DateTime, nullable=False)
