from app import login
from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(64))
    email = db.Column(db.String(120), index=True, unique=True)
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    image_uploads = db.relationship('ImageUpload', backref='upload_user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ImageUpload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<ImageUpload {}>'.format(self.image)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
