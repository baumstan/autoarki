from datetime import datetime
from app import db, app, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from time import time
import jwt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    firstname = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True)
    creation_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(128))
    image_uploads = db.relationship('ImageUpload', backref='uploader_id', lazy='dynamic')
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def previous_uploads(self):
        images = ImageUpload.query.filter_by(uploader_id==self.id)
        return images.order_by(ImageUpload.timestamp.desc())

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class ImageUpload(db.Model):
    id = db.Column(db.Integer, index=True, primary_key=True)
    image = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<ImageUpload {}>'.format(self.image)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))
