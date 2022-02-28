from datetime import datetime, timedelta
import unittest
from app import app, db
from app.models import User, ImageUpload

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        u = User(email='susan@test.com')
        u.set_password('cat')
        self.assertFalse(u.check_password('dog'))
        self.assertTrue(u.check_password('cat'))

    # def test_upload_plan_pdf(self):
    #     # create four users
    #     u1 = User(id=2524, email='john@example.com')
    #     u2 = User(id=5978, email='susan@example.com')
    #     db.session.add_all([u1, u2])
    #
    #     # create four pdf images
    #     now = datetime.utcnow()
    #     i1 = ImageUpload(id=123, image='image1',
    #               timestamp=now + timedelta(seconds=1), user_id=u1.id)
    #     i2 = ImageUpload(id=234, image='image2',
    #               timestamp=now + timedelta(seconds=1), user_id=u2.id)
    #     i3 = ImageUpload(id=345, image='image3',
    #               timestamp=now + timedelta(seconds=1), user_id=u2.id)
    #     db.session.add_all([i1, i2, i3])
    #     db.session.commit()
    #
    #     f1 = u1.previous_uploads().all()
    #     f2 = u2.previous_uploads().all()
    #     self.assertEqual(f1, ['image1'])
    #     self.assertEqual(f2, ['image2', 'image3'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
