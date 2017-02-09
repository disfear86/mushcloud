from flask import redirect, url_for, flash, session
from functools import wraps
from threading import Thread


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login_page'))
    return wrap


def start_thread(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrap
