
from flask import Flask, render_template, request
import db_functions
import time
from tcpModem import types

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    timezone = settings['timezone']
    if request.method == 'POST':  # A search was used
        call = request.form.get('callsign').upper()
        if call == "":
            blog = db_functions.get_all_blog()
            return render_template("index.html", blog=blog, title="Main Feed", call=owncall, timezone=timezone)
        blog = db_functions.get_callsign_blog(call, 0)
        title = f"{call}'s Feed"
        if call == owncall:
            return render_template("qth.html", blog=blog, title=title, call=owncall, timezone=timezone)
        else:
            return render_template("index.html", blog=blog, title=title, call=owncall, timezone=timezone)
    else:  # Default Main Page
        blog = db_functions.get_all_blog()
        return render_template("index.html", blog=blog, title="Main Feed", call=owncall, timezone=timezone)


@app.route("/monitoring")
def monitoring():
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    timezone = settings['timezone']
    blog = db_functions.get_monitoring_blog()
    return render_template("index.html", blog=blog, title="Monitoring Feed", call=owncall, timezone=timezone)


@app.route("/qth", methods=['GET', 'POST'])
def qth():
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    timezone = settings['timezone']
    if request.method == 'POST':
        msg = request.form.get('newmsg').upper()
        t = int(time.time())
        db_functions.add_blog(t, owncall, msg)
        db_functions.add_outgoing_post(types.ADD_BLOG, t, owncall, msg)
    blog = db_functions.get_callsign_blog(owncall, 0)
    title = f"{owncall} Feed"
    return render_template("qth.html", blog=blog, title=title, call=owncall, timezone=timezone)


@app.route("/callsign/<call>")
def callsign(call):
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    timezone = settings['timezone']
    blog = db_functions.get_callsign_blog(call, 0)
    title = f"{call}'s Feed"
    return render_template("index.html", blog=blog, title=title, call=owncall, timezone=timezone)


###########################################
# Background processes without refreshing #
###########################################
@app.route('/addmon', methods=['POST'])
def addmon():
    db_functions.add_monitoring(request.form.get('addmon'))
    return "nothing"


@app.route('/delmon', methods=['POST'])
def delmon():
    db_functions.remove_monitoring(request.form.get('delmon'))
    return "nothing"


@app.route('/getblog', methods=['POST'])
def getblog():
    db_functions.add_outgoing_post(types.GET_ALL_MSGS, 0, '@BLOG', request.form.get('getblog'))

    return "nothing"


if __name__ == "__main__":
    app.run()
