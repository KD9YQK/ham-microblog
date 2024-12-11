import pickle
from quart import Quart, render_template, request
import db_functions
import time

from js8Modem import Command
from tcpModem import types

target = Command.GET_POSTS
app = Quart(__name__)


@app.route("/", methods=['GET', 'POST'])
async def index():
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    if settings['js8modem']:
        with open('tmp/js8.spots', 'rb') as f:
            settings['js8spots'] = pickle.load(f)
        # settings['js8spots']['KD8HHH'] = {'blogger': True, 'hear_blog':['KD9YQK'], 'heard_blog':['KD9YQK'], 'hear_not':[],'heard_not':[]}
        # settings['js8spots']['KD9YQK'] = {'blogger': True, 'hear_blog': ['KD8HHH'], 'heard_blog': ['KD8HHH'], 'hear_not': [], 'heard_not': []}
    if request.method == 'POST':  # A search was used
        data = await request.form
        call = data['callsign'].upper()
        if call == "":
            blog = db_functions.get_all_blog()
            return await render_template("index.html", blog=blog, title="Main Feed", settings=settings, target=target)
        blog = db_functions.get_callsign_blog(call, 0)
        title = f"{call}'s Feed"
        if call == owncall:
            return await render_template("qth.html", blog=blog, title=title, settings=settings, target=target)
        else:
            return await render_template("index.html", blog=blog, title=title, settings=settings,
                                         target=f"{target} {call}")
    else:  # Default Main Page
        blog = db_functions.get_all_blog()
        return await render_template("index.html", blog=blog, title="Main Feed", settings=settings, target=target)


@app.route("/monitoring")
async def monitoring():
    settings = db_functions.get_settings()
    if settings['js8modem']:
        with open('tmp/js8.spots', 'rb') as f:
            settings['js8spots'] = pickle.load(f)
    blog = db_functions.get_monitoring_blog()
    return await render_template("index.html", blog=blog, title="Monitoring Feed", settings=settings, target=target)


@app.route("/qth", methods=['GET', 'POST'])
async def qth():
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    if settings['js8modem']:
        with open('tmp/js8.spots', 'rb') as f:
            settings['js8spots'] = pickle.load(f)
    if request.method == 'POST':
        data = await request.form
        msg = data['newmsg'].upper()
        t = int(time.time())
        db_functions.add_blog(t, owncall, msg)
        db_functions.add_outgoing_post(types.ADD_BLOG, t, owncall, msg)
    blog = db_functions.get_callsign_blog(owncall, 0)
    title = f"{owncall}'s Feed"
    return await render_template("qth.html", blog=blog, title=title, settings=settings, target=target)


@app.route("/callsign/<call>")
async def callsign(call):
    settings = db_functions.get_settings()
    owncall = settings['callsign']
    if settings['js8modem']:
        with open('tmp/js8.spots', 'rb') as f:
            settings['js8spots'] = pickle.load(f)
    blog = db_functions.get_callsign_blog(call, 0)
    title = f"{call}'s Feed"
    if call == owncall:
        return await render_template("qth.html", blog=blog, title=title, settings=settings, target=target)
    else:
        return await render_template("index.html", blog=blog, title=title, settings=settings, target=f"{target} {call}")


###########################################
# Background processes without refreshing #
###########################################
@app.route('/addmon', methods=['POST'])
async def addmon():
    data = await request.form
    call = data['addmon']
    db_functions.add_monitoring(call)
    return "nothing"


@app.route('/delmon', methods=['POST'])
async def delmon():
    data = await request.form
    call = data['delmon']
    db_functions.remove_monitoring(call)
    return "nothing"


@app.route('/getjs8target', methods=['POST'])
async def getjs8target():
    data = await request.form
    trgt = data['js8station']
    msg = data['js8msg']
    db_functions.add_outgoing_post(types.GET_MSG_TARGET, 0, trgt, msg)
    return "nothing"


@app.route('/getblog', methods=['POST'])
async def getblog():
    data = await request.form
    trgt = data['getblog']
    settings = db_functions.get_settings()
    if trgt == 'POST?':
        db_functions.add_outgoing_post(types.GET_ALL_MSGS, 0, settings['js8group'], trgt)
    else:
        db_functions.add_outgoing_post(types.GET_CALLSIGN, 0, trgt.split(' ')[1], '')
    return "nothing"


if __name__ == "__main__":
    print('')
    print('#########################################')
    print('#  Ham Microblog Web Frontend')
    print('#  Bob KD9YQK - http://www.kd9yqk.com/')
    print('#########################################')
    print('')
    app.run(host="0.0.0.0")
