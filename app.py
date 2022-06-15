# visitorLogger - A simple visitor logger for the website
# https://github.com/lwd-temp/visitorLogger
# Flask Backend
import sqlite3
import time

import flask

# Default Secret Key
SECRET_KEY = 'developmentkey'
# Default Database Name
DATABASE = 'visitor.db'
# Default Port
PORT = 80
# Default Host
HOST = '0.0.0.0'
# Debug Mode
DEBUG = False


# Create the application object
app = flask.Flask(__name__)
# Create a DB connection
db = sqlite3.connect(DATABASE, check_same_thread=False)
# Create a cursor
c = db.cursor()
# Create a table
c.execute("""CREATE TABLE IF NOT EXISTS visitors (
            uuid TEXT,
            ip TEXT,
            time TEXT,
            ua TEXT,
            referrer TEXT,
            ext TEXT,
            header TEXT)""")
# Commit the changes
db.commit()
# Close the DB connection
db.close()


@app.route('/clean')
# DB Cleanup
# Arguments: secret, secret is the secret key
#            keep, number of days to keep
def clean():
    # Use default SECRET
    SECRET = SECRET_KEY
    # Get the secret
    secret = flask.request.args.get('secret', None)
    # Check if the secret is correct
    if secret != SECRET:
        return 'Invalid secret'
    # Get the number of days to keep
    keep = flask.request.args.get('keep', None)
    # Check if the number of days to keep is valid
    if keep is None or not keep.isdigit():
        return 'Invalid keep'
    # Convert the number of days to keep to an integer
    keep = int(keep)
    # Get the current time
    now = time.time()
    # Get the time of the day
    today = time.strftime('%Y-%m-%d', time.localtime(now))
    # Get the time of the day minus the number of days to keep
    yesterday = time.strftime('%Y-%m-%d', time.localtime(now - (86400 * keep)))
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Delete all entries older than the number of days to keep
    c.execute("DELETE FROM visitors WHERE time < ?", (yesterday,))
    # Commit the changes
    db.commit()
    # Close the DB connection
    db.close()
    # Return a success message
    return 'Cleaned'


@app.route("/append")
# Append a new visitor to the DB, any method can be used
def append():
    # Get the data from the request
    try:
        uuid = str(flask.request.values.get('uuid'))
    except:
        uuid = 'None'
    try:
        ext = str(flask.request.values.get('ext'))
    except:
        ext = 'None'
    try:
        # Overide if Cf-Connecting-Ip is present
        if flask.request.headers.get('Cf-Connecting-Ip'):
            ip = str(flask.request.headers.get('Cf-Connecting-Ip'))
        elif flask.request.headers.get('X-Forwarded-For'):
            ip = str(flask.request.headers["X-Forwarded-For"])
        else:
            ip = str(flask.request.remote_addr)
    except:
        ip = 'None'
    try:
        ua = str(flask.request.headers["User-Agent"])
    except:
        ua = 'None'
    try:
        referrer = str(flask.request.headers["Referer"])
    except:
        referrer = 'None'
    try:
        header = str(flask.request.headers)
    except:
        header = 'None'
    currtime = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Insert the data
    c.execute("""INSERT INTO visitors VALUES (?,?,?,?,?,?,?)""",
              (uuid, ip, currtime, ua, referrer, ext, header))
    # Commit the changes
    db.commit()
    # Close the DB connection
    db.close()
    # Make a response
    resp = flask.make_response(flask.jsonify(
        {"uuid": uuid, "ip": ip, "time": currtime, "ua": ua, "referrer": referrer, "ext": ext, "header": header}), 200)
    # Allow Cross Origin Resource Sharing
    resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/post", methods=['POST'])
# Append a new visitor to the DB, using POST
def post():
    # Get the data from the request
    try:
        uuid = str(flask.request.form['uuid'])
    except:
        uuid = 'None'
    try:
        ext = str(flask.request.form['ext'])
    except:
        ext = 'None'
    try:
        # Overide if Cf-Connecting-Ip is present
        if flask.request.headers.get('Cf-Connecting-Ip'):
            ip = str(flask.request.headers.get('Cf-Connecting-Ip'))
        elif flask.request.headers.get('X-Forwarded-For'):
            ip = str(flask.request.headers["X-Forwarded-For"])
        else:
            ip = str(flask.request.remote_addr)
    except:
        ip = 'None'
    try:
        ua = str(flask.request.headers["User-Agent"])
    except:
        ua = 'None'
    try:
        referrer = str(flask.request.headers["Referer"])
    except:
        referrer = 'None'
    try:
        header = str(flask.request.headers)
    except:
        header = 'None'
    currtime = time.strftime("%Y-%m-%d %H:%M:%S")
    # Create a DB connection
    db = sqlite3.connect(DATABASE, check_same_thread=False)
    # Create a cursor
    c = db.cursor()
    # Insert the data
    c.execute("""INSERT INTO visitors VALUES (?,?,?,?,?,?,?)""",
              (uuid, ip, currtime, ua, referrer, ext, header))
    # Commit the changes
    db.commit()
    # Close the DB connection
    db.close()
    # Make a response
    resp = flask.make_response(flask.jsonify(
        {"uuid": uuid, "ip": ip, "time": currtime, "ua": ua, "referrer": referrer, "ext": ext, "header": header}), 200)
    # Allow Cross Origin Resource Sharing
    resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


@app.route("/")
# Return the index page
def index():
    # Make a response
    # If in debug mode, return this
    if app.debug:
        resp = flask.make_response("""<html>
        <head>
        <title>Visitor Logger</title>
        </head>
        <body>
        <h1>Visitor Logger</h1>
        <p>This is a simple visitor logger for the website.</p>
        <p>You can use the following endpoints:</p>
        <ul>
        <li>/append - Append a new visitor to the DB</li>
        <li>/post - Append a new visitor to the DB using POST</li>
        <li>/clean - Clean the DB</li>
        </ul>
        </body>
        </html>""")
    else:
        resp = flask.make_response("""<html>
        <head>
        <title>Hello, world!</title>
        </head>
        <body>
        <h1>Production</h1>
        </body>
        </html>""")
    # Allow Cross Origin Resource Sharing
    resp.headers['Access-Control-Allow-Origin'] = "*"
    # Return the data
    return resp


# Run the application
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)
# End of file
