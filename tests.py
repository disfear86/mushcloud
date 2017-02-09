#!/usr/bin/python3
import os
import unittest
from app.alchemy import User
from app import app, db
from config import basedir
from coverage import Coverage

cov = Coverage()
cov.start()


class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:D@kis886848@localhost/mush_test_testing'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_db(self):
        user = User(None, 'randomname', 'randemail@host.com', 'randompassword')
        db.session.add(user)
        db.session.commit()
        assert user in db.session
'''
    def test_reg(self):
        pass

    def test_login(self):
        pass

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
    print("HTML version: " + os.path.join(basedir, "tmp/coverage/index.html"))
    cov.html_report(directory='tmp/coverage')
    cov.erase()
