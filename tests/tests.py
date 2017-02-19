#!/usr/bin/python3
import os
import unittest
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.alchemy import User
from app import app, db
from config import basedir
from coverage import Coverage
from flask_login import current_user, login_user
from flask import request, session
from app.auth import registration, change_pass
from passlib.hash import sha256_crypt
import shutil
import pdb


cov = Coverage(source=['app'], branch=True, omit=['app/forms.py', 'app/decorators.py'])
cov.start()


def add_user():
    pwd = sha256_crypt.encrypt('mushpass')
    user = User(None, username='mushcloud', password=pwd,
                email='mushcloud@mushcloud.com')
    db.session.add(user)
    db.session.commit()
    return user


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app = app
        self.client = self.app.test_client()
        self._ctx = self.app.test_request_context()
        self._ctx.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_db(self):
        user = add_user()
        assert user in db.session


class TestCase(BaseTestCase):
    def test_registration(self):
        with self.client:
            self.client.post('register/', data=dict(
                username='mushcloud', email='mushcloud@mushcloud.com',
                password='mushpass', confirm='mushpass'
            ), follow_redirects=True)

            pwd = sha256_crypt.encrypt('mushpass')

            registration(username='mushcloud', email='mushcloud@mushcloud.com',
                            password=pwd, form=None)
            #pdb.set_trace()
            user = User.query.filter_by(username='mushcloud').first()

            self.assertTrue(user.username == "mushcloud")
            self.assertTrue(str(user) == '<User mushcloud>')
            self.assertTrue(current_user.is_active())

    def test_login_logout(self):
        with self.client:
            self.client.post('login_page/', data=dict(
                                    username='mushcloud',
                                    password='mushpass',
                                ), follow_redirects=True)

            user = add_user()
            login_user(user)

            self.assertTrue(current_user.username == "mushcloud")
            self.assertTrue(current_user.is_active())
            self.client.post('logout/', follow_redirects=True)
            self.assertFalse(current_user.is_active)

    def test_change_pwd(self):
        with self.client:
            self.client.post('change_pwd/', data=dict(
                                    old_pwd='mushpass',
                                    new_pwd='newpass',
                                    confirm='newpass'
                                ), follow_redirects=True)
            user = add_user()
            change_pass(user=user, old_pwd='mushpass', new_pwd='newpass')

            self.assertTrue(sha256_crypt.verify('newpass', user.password))

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
