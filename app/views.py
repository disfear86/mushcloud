from flask import render_template, redirect, url_for, jsonify, \
                    flash, request, session, send_file, g
from werkzeug.exceptions import abort, BadRequestKeyError
import gc

from app import app, login_manager
from app.auth import registration, log_in, change_pass, forgot_password, \
                    reset_password
from flask_login import login_required, current_user
from app.alchemy import db, User, tablename

from app.file_handling import check_which_folder, ListAll, CreateDir, \
                                    Rename, Upload, Delete
import os
from os.path import isdir
from .forms import RegistrationForm, LoginForm, ChangePwdForm
from passlib.hash import sha256_crypt


main_path = app.config['USER_STORAGE_PATH']


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


# currently unused
def file_size(files):
    """Returns file size in KB or MB depending on size."""
    size = os.path.getsize(files)
    if size > 1000000:
        size /= 1000000
        return "{0:.2f}".format(size) + ' MB'
    else:
        size /= 1000
        return "{0:.2f}".format(size) + ' KB'


###################################
# create class variables to pass  #
# delete and rename data          #
# between functions               #
class DelData(object):
    del_data = ''


class RenData(object):
    ren_data = ''
#                                 #
###################################


@app.route('/')
def homepage():
    return render_template('main.html')


@app.route('/user_settings/', methods=['GET', 'POST'])
@login_required
def user_settings():
    return render_template('user_settings.html')


@app.route('/change_password/', methods=['GET', 'POST'])
def change_pwd():
    user = g.user
    form = ChangePwdForm(request.form)
    if request.method == "POST" and form.validate():
        old_pwd = form.old_pwd.data
        new_pwd = form.new_pwd.data
        try:
            change_pass(user, old_pwd, new_pwd)
            gc.collect()
            return redirect(url_for('user_home'))
        except:
            flash('Invalid password.')
            return redirect(url_for('change_pwd', form=form))

    return render_template('change_pwd.html', form=form)


@app.route('/forgot_password/', methods=['GET', 'POST'])
def forgot_pwd():
    return forgot_password()


@app.route('/reset_password/<key>', methods=['GET', 'POST'])
def reset_pwd(key=""):
    return reset_password(key)


@app.route('/change_plan/', methods=['GET', 'POST'])
@login_required
def change_plan():
    user = str(g.user.username)
    if request.method == "POST" and 'options' in request.form:
        new_plan = request.form['options']
        old_plan = db.session.query(User.plan_mb).filter(User.username == user)
        plan_left = db.session.query(User.mb_left).filter(User.username == user)
        usr = User.query.filter_by(username=user).first()
        usr.mb_left = (float(new_plan) - float(old_plan[0][0])) + float(plan_left[0][0])
        usr.plan_mb = new_plan
        db.session.commit()
        flash("Congratulations You've Upgraded Your Plan")
        gc.collect()
    return render_template('change_plan.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        return redirect(url_for('user_home'))
    form = RegistrationForm(request.form)
    if request.method == "POST" and form.validate():
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.encrypt(form.password.data)
        return registration(username, email, password, form)
    return render_template('register.html', form=form)


@app.before_request
def before_request():
    g.user = current_user


@app.route('/login/', methods=['GET', 'POST'])
def login_page():
    if 'logged_in' in session:
        return redirect(url_for('user_home'))
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        user_submit = request.form['username']
        password = request.form['password']
        return log_in(user_submit, password)
    return render_template("login.html", form=form)


@app.route('/_delete/', methods=['GET', 'POST'])
def delete():
    if request.method == "POST":
        DelData.del_data = request.json['data']
        return jsonify(result=DelData.del_data)


@app.route('/_rename/', methods=['GET', 'POST'])
def rename():
    if request.method == "POST":
        RenData.ren_data = request.json['data']
        return jsonify(result=RenData.ren_data)


@app.route('/search/', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == "POST":
        user = str(current_user.username)

        search_data = request.form['search']
        if not search_data:
            data = 'No data entered.'
            return render_template('search.html', data=data)

        user_table = tablename(user)

        # select all file entries in db that start with data entered by user.
        search_q = user_table.query.filter(user_table.name.startswith(search_data)).all()

        # create lists to make passing the data to our template easier
        name_lst = [search_q[i].name for i in range(len(search_q))]
        path_lst = [search_q[i].path for i in range(len(search_q))]
        path_to_open = [search_q[i].path.replace(main_path + user + '/', '')
                        for i in range(len(search_q))]
        # zip the lists into one list
        name_path_pairs = [[i, j, k] for i, j, k in zip(name_lst, path_lst, path_to_open)]

        if not search_q:
            data = 'No results found.'
            return render_template('search.html', data=data)
        else:
            return render_template('search.html', data=name_path_pairs, user=user)


@app.route('/home/', methods=['GET', 'POST'])
@app.route('/home/<path:folder>/', methods=['GET', 'POST'])
@login_required
def user_home(folder=""):
    # aquire session username and path to file
    user = str(g.user.username)
    home_path = main_path + user
    user_path = home_path + '/' + folder

    try:
        # if path is a file, open/download it
        if not isdir(user_path):
            return send_file(user_path)

        # bar data, user storage left
        user_plan = db.session.query(User.plan_mb).filter(User.username == user)
        user_plan_left = db.session.query(User.mb_left).filter(User.username == user)
        user_bar_data = str(user_plan_left[0][0]) + ' MB ' + '/ ' + str(float(user_plan[0][0])) + ' MB'

        percent = (float(user_plan_left[0][0]) / float(user_plan[0][0])) * 100
        percent = str("{0:.2f}".format(round(percent, 2))) + '%'

        file_obj = ListAll(user, user_path)
        # list files and folders
        allfiles, alldirs = file_obj.list_files()

        # upload new file
        if request.method == 'POST' and 'newfile' in request.files:
            if 'newfile' not in request.files:
                flash('No file part')
                return redirect(request.url)
            up_file = request.files['newfile']

            newfile_obj = Upload(user, user_path, up_file)
            newfile_obj.file_upload()

            gc.collect()
            if not folder:
                return redirect(url_for('user_home'))
            else:
                return redirect(url_for('user_home', folder=folder))

        # create new folder
        if request.method == 'POST' and 'newfolder' in request.form:
            folder_obj = CreateDir(user, user_path)
            folder_obj.create()

            gc.collect()
            if not folder:
                return redirect(url_for('user_home'))
            else:
                return redirect(url_for('user_home', folder=folder))

        # delete file or folder
        if DelData.del_data:
            del_obj = Delete(user, user_path, DelData.del_data, folder)
            for f in allfiles:
                if f[3] == DelData.del_data:
                    del_obj.delete_file(f)

                    flash("File " + DelData.del_data + " has been deleted.")
                    gc.collect()
                    if not folder:
                        return redirect(url_for('user_home'))
                    else:
                        return redirect(url_for('user_home', folder=folder))

            for d in alldirs:
                if d[0] == DelData.del_data:
                    del_obj.delete_folder(d)

                    flash("Folder '{}' has been deleted.".format(d[0]))
                    gc.collect()
                    if not folder:
                        return redirect(url_for('user_home'))
                    else:
                        return redirect(url_for('user_home', folder=folder))

        # rename file or folder
        if request.method == 'POST' and 'new_data' in request.form:
            new_name = request.form['new_data']
            new_path = check_which_folder(user, user_path, new_name)

            ren_obj = Rename(user, user_path, RenData.ren_data, new_name, new_path)
            ren_obj.rename_f()

            if not folder:
                return redirect(url_for('user_home'))
            else:
                return redirect(url_for('user_home', folder=folder))

        gc.collect()
        return render_template('user_home.html',
                               user_path=user_path, folder=folder,
                               user_bar_data=user_bar_data, alldirs=alldirs,
                               allfiles=allfiles, percent=percent,
                               user_plan_left=user_plan_left[0][0])
    except Exception as e:
        error = e
        return redirect(url_for('user_home', error=error))


@app.route('/logout/')
@login_required
def logout():
    session.clear()
    gc.collect()
    flash('You have been logged out!')
    return redirect(url_for('login_page'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html")


@app.errorhandler(BadRequestKeyError)
def handle_key_error(e):
    app.logger.exception('Missing key {}'.format(e.args[0]))
    try:
        abort(500)
    except Exception as new_e:
        app.handle_user_exception(new_e)
