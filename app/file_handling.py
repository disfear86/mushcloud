from app import app
from flask import redirect, flash, request
from werkzeug import secure_filename
from .alchemy import db, User, tablename
import os
from os import listdir, mkdir
from os.path import isfile, join, isdir
import time
import uuid
import re
import shutil

main_path = app.config['USER_STORAGE_PATH']

# check if file or folder is in main or sub folders
# and set path accordingly
def check_which_folder(user, user_path, f_name):
    if user_path == (main_path + user + '/'):
        f_path = user_path + f_name
    else:
        f_path = user_path + '/' + f_name
    return f_path


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def get_extension(filename):
    return '.' in filename and \
           filename.rsplit('?.', 1)[0].lower()


def get_file_size(up_file):
    # save pointer position at beggining of file
    old_file_position = up_file.tell()
    # count file bytes
    up_file.seek(0, os.SEEK_END)
    # get the file size in MB
    get_size = up_file.tell() / 1000000
    # reset pointer at beggining of file
    up_file.seek(old_file_position, os.SEEK_SET)
    return get_size


# create uuid for each file
def uuid_generator(string_length=20):
    """Returns a random string of length string_length."""
    rand_id = str(uuid.uuid4())
    rand_id = rand_id.replace("-", "")
    return rand_id[0:string_length]


class WriteUserDb(object):
    """Writes file or directory info to database."""
    def __init__(self, user, user_path):
        self.usr = User.query.filter_by(username=user).first()
        self.user_table = tablename(user)
    
    # Initialize get_size and get_uuid to None in case we want to write dir data to db
    def write_obj(self, file_name, file_path, get_date, get_size=None, get_uuid=None):
        self.file_name = file_name
        self.get_uuid = get_uuid
        self.file_path = file_path
        self.get_date = get_date
        self.get_size = get_size

        data = self.user_table(str(self.file_name), self.get_uuid,
                               str(self.file_path), self.get_date,
                               self.get_size)
        db.session.add(data)
        db.session.commit()


class FileHandle(object):
    """File or directory object parent class."""
    def __init__(self, user, user_path):
        self.user = user
        self.user_table = tablename(user)
        self.user_path = user_path


class ListAll(FileHandle):
    """List all files and directories."""
    def __init__(self, user, user_path):
        super(ListAll, self).__init__(user, user_path)

    # list files and folders
    def list_files(self):

        allfiles = []
        for f in listdir(self.user_path):
            if isfile(join(self.user_path, f)):
                extension = (os.path.splitext(f)[1][1:]).lower()
                date_data = db.session.query(self.user_table.name, self.user_table.date).filter(self.user_table.path == (join(self.user_path, f)))

                if date_data is not None:
                    file_date = date_data[0][1]
                    file_name = date_data[0][0]
                    f_data = [f, extension, file_date, file_name]
                    allfiles.append(f_data)

        alldirs = []
        for d in listdir(self.user_path):
            if isdir(join(self.user_path, d)):
                date_data = db.session.query(self.user_table.date).filter(self.user_table.path == (join(self.user_path, d))).first()

                if date_data is not None:
                    file_date = date_data[0]
                    alldirs.append([d, file_date])

        allfiles.sort()
        alldirs.sort()
        return allfiles, alldirs


class Upload(FileHandle):
    """Upload file."""
    def __init__(self, user, user_path, up_file):
        super(Upload, self).__init__(user, user_path)
        self.up_file = up_file

    def file_upload(self):
        if self.up_file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if not allowed_file(self.up_file.filename):
            flash('File type not allowed.')

        if self.up_file and allowed_file(self.up_file.filename):
            # generate uuid for file
            uuid_code = uuid_generator()

            # check if file has secure filename
            filename = secure_filename(self.up_file.filename)

            # get the file extension
            ext = (os.path.splitext(filename)[1]).lower()

            # set file name to uuid + extension
            filename = uuid_code + ext
            file_path = check_which_folder(self.user, self.user_path, filename)

            if isfile(str(file_path)):
                flash('A file with that name already exists.')
            # set uploaded file name to store on db
            else:
                name_for_db = secure_filename(self.up_file.filename)
                get_date = time.strftime("%d/%m/%Y")
                get_size = get_file_size(self.up_file)

                # retreive user remaining storage
                mbytes = db.session.query(User.mb_left).filter(User.username == self.user)
                # calculate remaining storage after file upload
                Mbytes_left = float(mbytes[0][0]) - float(get_size)

                # check if file to upload is larger then remaining storage
                if Mbytes_left < 0:
                    flash('Not enough space.')
                else:
                    # save file to user folder, update storage on db
                    # and store file info on user personal table
                    self.up_file.save(os.path.join(self.user_path, filename))
                    usr = User.query.filter_by(username=self.user).first()
                    usr.mb_left = Mbytes_left

                    # insert file data into user table
                    write_f = WriteUserDb(self.user, self.user_path)
                    write_f.write_obj(name_for_db, file_path,
                                      get_date, get_size, uuid_code)

                    flash("File '" + filename + "' was uploaded successfully.")


class CreateDir(FileHandle):
    """Create new directory."""
    def __init__(self, user, user_path):
        super(CreateDir, self).__init__(user, user_path)

    def create(self):
        folder_name = request.form['newfolder']
        if folder_name == '':
            flash('No folder name given.')
            return redirect(request.url)
        folder_path = check_which_folder(self.user, self.user_path, folder_name)

        if isdir(str(folder_path)):
            flash('Folder already exists')
        else:
            # create directory on user current path
            mkdir(folder_path)
            self.user_path = folder_path
            get_date = time.strftime("%d/%m/%Y")
            # flash(user_path)
            # insert folder data into user table
            write_f = WriteUserDb(self.user, self.user_path)
            write_f.write_obj(folder_name, folder_path, get_date)

            flash("Folder '" + folder_name + "' was created successfully.")


class Rename(FileHandle):
    """Rename file or directory."""
    def __init__(self, user, user_path, ren_data, new_name, new_path):
        super(Rename, self).__init__(user, user_path)
        self.ren_data = ren_data
        self.new_name = new_name
        self.new_path = new_path

    def rename_f(self):
        usr = self.user_table.query.filter_by(name=self.ren_data).first()

        del_path = db.session.query(self.user_table.path).filter(self.user_table.name == self.ren_data).first()[0]

        if isdir(del_path):
            os.rename(del_path, self.new_path)
            usr.path = self.new_path

        usr.name = self.new_name
        db.session.commit()


class Delete(FileHandle):
    """Delete file or directory."""
    def __init__(self, user, user_path, del_data, folder):
        super(Delete, self).__init__(user, user_path)
        self.del_data = del_data
        self.folder = folder

    def delete_file(self, f):
        self.f = f

        # get file code by removing file extension
        file_code = (os.path.splitext(self.f[0])[0])

        del_path = db.session.query(self.user_table.path).filter(self.user_table.code == file_code).first()[0]
        get_size = db.session.query(self.user_table.size).filter(self.user_table.path == del_path).first()[0]

        # retreive users remaining storage
        mbytes = db.session.query(User.mb_left).filter(User.username == self.user).first()[0]

        # set new remaining storage after file is deleted
        # and update database entry
        mbytes_left = float(mbytes) + float(get_size)

        usr = User.query.filter_by(username=self.user).first()
        usr.mb_left = mbytes_left

        # remove file from storage
        os.remove(del_path)
        # delete database entry
        self.user_table.query.filter(self.user_table.path == del_path).delete()
        db.session.commit()

    def delete_folder(self, d):
        self.d = d

        del_path = check_which_folder(self.user, self.user_path, self.d[0])
        if not self.folder:
            del_path = self.user_path + self.d[0]
        else:
            del_path = self.user_path + '/' + self.d[0]

        query = self.user_table.query.all()

        quotes = re.compile("'[^']*'")
        data = [val[1:-1] for val in quotes.findall(str(query))[1::2]]

        # search and delete any db entries that belong to folder
        # to be deleted
        for entry in data:
            if self.d[0] in entry:
                self.user_table.query.filter(self.user_table.path == entry).delete()
        db.session.commit()

        # remove directory and contents
        shutil.rmtree(del_path)
