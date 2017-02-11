"""Authentication module for registration, logging in, and changing password"""
from flask import render_template, redirect, url_for, flash, \
     request, session
from flask_login import login_user, logout_user, current_user
from app import app
from .alchemy import db, User, tablename
from passlib.hash import sha256_crypt
import gc
from os import mkdir
from os.path import isdir
from app.decorators import start_thread
from .forms import RegistrationForm, ChangePwdForm, EnterEmail, ForgotPass
import time
import shutil
from app import mail
from flask_mail import Message


@start_thread
def setup_mail(msg):
    with app.app_context():
        mail.send(msg)


def send_mail(subject, sender, recipients, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    setup_mail(msg)


def registration(username, email, password, form):
    try:
        # set free account storage volume
        plan = 2000  # mbytes
        mb_left = 2000

        dat = User.query.filter_by(username=username).first()
        dat_email = User.query.filter_by(email=email).first()

        if dat is not None:
            flash('Username not available.')
            return redirect(url_for('register', form=form))
        elif dat_email is not None:
            flash('Email is already in use.')
            return redirect(url_for('register', form=form))
        else:
            db.session.add(User(None, username, email, password, plan, mb_left, False))


            user = User.query.filter_by(username=username).first()

            flash('Registration Successful.')
            login_user(user)
            next = request.args.get('next')
            main_path = app.config['USER_STORAGE_PATH']
            user_path = main_path + str(user.username)

            # check if directory exists and create main user directory
            if isdir(user_path):
                shutil.rmtree(user_path)
            mkdir(user_path)

            # create users first folder in main directory
            mkdir(user_path + '/' + 'My Folder')

            # create personal user table in db
            class User_folder(db.Model):
                __tablename__ = str(user.username)
                id = db.Column(db.Integer, primary_key=True)
                name = db.Column(db.String(150))
                code = db.Column(db.String(150))
                path = db.Column(db.String(150))
                date = db.Column(db.String(15))
                size = db.Column(db.Float)

            db.create_all()
            path = user_path + '/' + 'My Folder'
            date = time.strftime("%d/%m/%Y")

            user_table = tablename(str(user.username))
            data = user_table('My Folder', None, path, date, None)
            db.session.add(data)
            db.session.commit()

            gc.collect()
            return redirect(next or url_for('user_home'))

    except Exception as e:
        return redirect(url_for('register', error=str(e)))


def log_in(user_submit, password):
    try:
        user = User.query.filter_by(username=user_submit).first()
        if user is None:
            flash('Invalid Credentials.')
            return redirect(url_for('login'))
        else:
            pwd = user.password
            if sha256_crypt.verify(password, pwd):
                #session['logged_in'] = True
                #session['username'] = request.form['username']
                #user = str(session['username'])
                login_user(user)
                flash('Hello, ' + user.username + '!')
                next = request.args.get('next')

                #gc.collect()
                #return redirect(request.args.get("next"))
                return redirect(next or url_for('user_home'))
            else:
                flash('Invalid Credentials.')
                return redirect(url_for('login'))

    except Exception as e:
        return redirect(url_for("login_page", error=(str(e))))


def change_pass(user):
    try:
        form = ChangePwdForm(request.form)
        if request.method == "POST" and form.validate():
            old_pwd = form.old_pwd.data
            new_pwd = sha256_crypt.encrypt(form.new_pwd.data)

            data = db.session.query(User.username, User.password). \
                filter(User.username == user).first()

            usr = User.query.filter_by(username=user).first()
            pwd = data[1]

            if sha256_crypt.verify(old_pwd, pwd):
                usr.password = new_pwd
                db.session.commit()
                flash('Password Changed Successful.')
                return redirect(url_for('user_home'))
            else:
                flash('Invalid password.')
                return redirect(url_for('user_settings'))
            gc.collect()
        return render_template('user_settings.html', form=form)

    except Exception as e:
        return render_template('user_settings.html', form=form, error=(str(e)))


def forgot_password():
    # set base url for email link
    url_main = app.config['RESET_PASS_URL']
    form = EnterEmail(request.form)

    if request.method == "POST" and form.validate():
        email = form.email.data
        usr = User.query.filter_by(email=email).first()

        # check if usr query has data
        if usr and usr.email == email:
            # generate token
            token = usr.get_token()
            # set url for email link
            url_token = url_main + token
            sender = app.config['MAIL_USERNAME']
            subject = "Password Reset."
            recipients = [email]

            html_body = "<div class='container' align='middle'> \
                        <img src='http://<yourdomain>/static/images/<yourlogo>.jpg' \
                                style='width:30%; height:15%;'' alt='Brand Name'> \
                        </img> \
                        <p><b>You have requested to change your password.<br></p> \
                            Please click <a href=" + url_token + ">Here</a> \
                    </div>"

            send_mail(subject, sender, recipients, html_body)

            # set db entry to True to show token is unused
            usr.reset_pass = True
            db.session.commit()

            flash("An e-mail has been sent to your e-mail address.")
            return redirect(url_for('forgot_pwd'))
        else:
            flash("Invalid e-mail.")
            return redirect(url_for('forgot_pwd'))
    return render_template('forgot_password.html', form=form)


def reset_password(token=None):
    form = ForgotPass(request.form)
    # verify the generated token
    usr = User.verify_token(token)
    # check if token is unused
    is_token_unused = usr.reset_pass

    if token and usr and is_token_unused:
        if form.validate():
            # set db entry to false to mark token was used
            usr.reset_pass = False
            # set new password
            usr.password = sha256_crypt.encrypt(form.new_pwd.data)
            db.session.commit()
            flash('Password has been Successfully changed.')
            return redirect(url_for('login_page'))
    else:
        flash('Session expired.')
        return redirect(url_for('forgot_pwd'))

    return render_template('reset_password.html', form=form)
