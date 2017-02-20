# mushcloud
A cloud storage web app created with Flask and Bootstrap.

This is a flask web app I created to implement what I've learnt so far in Python and Flask.

I'm fairly new to web development so any input or advice is greatly appreciated.

The application is compatible with both Python 2 and Python 3.

Requirements:

`pip install -r requirements.txt`

You will also need a Mysql connector (I used mysqlclient and it works great with Python 3.5) and bootstrap 3 installed.

`pip install mysqlclient`

For more info and docs visit [mysqlclient github repo](https://github.com/PyMySQL/mysqlclient-python)

To get the application working, you have to modify the config.py file to inlude your database URI, mail server, reset password url and set up the main user storage directory. Finally run `python3 db_create.py` command from the terminal to create the database.
