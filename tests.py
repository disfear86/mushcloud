#!/usr/bin/python3
import os
import unittest
from app.alchemy import User
from app import app, db
from config import basedir
from coverage import Coverage
from flask_login import current_user
from flask import request, session
from app.auth import registration, log_in
import shutil
import pdb


cov = Coverage(source=['app'], branch=True)
cov.start()


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        app.config.update(TESTING=True)
        self.app = app
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()\


    def test_db(self):
        user = User(None, 'randomname', 'randemail@host.com', 'randompassword')
        db.session.add(user)
        db.session.commit()
        assert user in db.session


class TestCase(BaseTestCase):
    def test_registration(self):
        with self.client:
            self.client.post('register/', data=dict(
                username='mushcloud', email='mushcloud@mushcloud.com',
                password='mushpass', confirm='mushpass'
            ), follow_redirects=True)

            registration(username='mushcloud', email='mushcloud@mushcloud.com',
                            password='mushpass', form=None)
            # self.assertIn(b'Registration Successful.', response.data)
            user = User.query.filter_by(username='mushcloud').first()
            #pdb.set_trace()
            self.assertTrue(user.username == "mushcloud")
            self.assertTrue(str(user) == '<User mushcloud>')
            self.assertTrue(current_user.is_active())

    def test_login(self):
        with self.client:
            self.client.post('login_page/', data=dict(
                                    username='mushcloud',
                                    password='mushcloud',
                                ), follow_redirects=True)

            log_in('mushcloud', 'mushpass')
            user = User.query.filter_by(username='mushcloud').first()
            #pdb.set_trace()
            self.assertTrue(current_user.username == "mushcloud")
            self.assertTrue(current_user.is_active())


'''
    def test_create_dir(self):
        pass

    def test_upload(self):
        pass

    def test_rename(self):
        pass

    def test_del_file(self):
        pass

    def test_change_plan(self):
        pass
'''

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
    cov.stop()
    cov.save()
    print("\n\nCoverage Report:\n")
    cov.report()
    print("HTML version: " + os.path.join(basedir, "htmlcov/coverage/index.html"))
    cov.html_report(directory='htmlcov/coverage')
    cov.erase()
