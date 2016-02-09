from flask import Flask, render_template, request, redirect, url_for, flash, \
    jsonify
import random
import string
import psycopg2
from collections import namedtuple

from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog App FSND"

# Series of helper functions for connecting to and editing database


def connect():
    # returns connection and cursor for psql database
    try:
        db = psycopg2.connect("dbname=catalog")
        cursor = db.cursor()
        return db, cursor
    except:
        print("Could not connect to database.")


def add_ItemDB(name, category, description, imgurl):
    # adds a new item to the item table
    db, c = connect()

    query = "INSERT INTO items(name, category, description,"\
        " imgurl) VALUES(%s, %s, %s, %s) RETURNING id;"
    param = (name, category, description, imgurl)
    c.execute(query, param)
    itemid = c.fetchone()[0]

    db.commit()
    c.close()
    db.close()

    return itemid


def edit_itemDB(id, name, category, description, imgurl):
    db, c = connect()

    query = "UPDATE items SET name = %s, category = %s, "\
        "description = %s, imgurl = %s WHERE id = %s"
    param = (name, category, description, imgurl, id)
    c.execute(query, param)
    db.commit()
    c.close()
    db.close()


def delete_itemDB(id):
    # remove an item based on its unique id from the item table
    db, c = connect()

    query = "DELETE FROM items WHERE id=%s"
    param = (id,)
    c.execute(query, param)

    db.commit()
    c.close()
    db.close()


def clearDatabase():
    # delete all items from item table.
    # for debug purposes only
    db, c = connect()

    query = "TRUNCATE items"
    c.execute(query)

    db.commit()
    c.close()
    db.close()


def getCategories():
    # since users can delete categories, we constantly update to hide them
    db, c = connect()
    query = "SELECT DISTINCT category FROM items ORDER BY category"
    c.execute(query)
    categories = c.fetchall()

    c.close()
    db.close()
    return categories


def getItem(itemid):
    # get an item and convert it into a namedtuple
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name',
                               'category', 'description', 'imgurl'])
    query = "SELECT * FROM items WHERE id=%s"
    param = (itemid,)
    c.execute(query, param)
    item = Item(*c.fetchone())

    c.close()
    db.close()
    return item


def serialize(self):

    return {
        'name': self.name,
        'description': self.description,
        'id': self.id,
        'category': self.category,
        'imgurl': self.imgurl,
    }


@app.route('/catalog/<category>')
def categoryItems(category):
    # Category page: category names are unique
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name',
                               'category', 'description', 'imgurl'])
    query = "SELECT * FROM items WHERE category=%s"
    param = (category,)
    c.execute(query, param)
    items = c.fetchall()
    nameditems = [Item(*i) for i in items]

    c.close()
    db.close()
    return render_template('categoryitems.html',
                           items=nameditems,
                           category=category,
                           categories=getCategories())


@app.route('/catalog/<category>/<int:itemid>')
@app.route('/catalog/<category>/<int:itemid>/<name>')
def item(itemid, name, category):
    # Item page: item names are not unique
    return render_template('item.html', item=getItem(itemid),
                           categories=getCategories())


# JSON API endpoints

@app.route('/catalog/<category>/JSON')
def categoryItemsJSON(category):
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name',
                               'category', 'description', 'imgurl'])
    query = "SELECT * FROM items WHERE category=%s"
    param = (category,)
    c.execute(query, param)
    items = c.fetchall()
    nameditems = [Item(*i) for i in items]

    c.close()
    db.close()
    return jsonify(categoryItems=[serialize(item) for item in nameditems])


@app.route('/catalog/<category>/<int:itemid>/JSON')
@app.route('/catalog/<category>/<int:itemid>/<name>/JSON')
def itemJSON(itemid, name, category):
    return jsonify(Item=serialize(getItem(itemid)))


@app.route('/catalog/<category>/<int:itemid>/edit', methods=['GET', 'POST'])
def editItem(itemid, category):
    if 'username' not in login_session:
        flash('please login to do that')
        return redirect('/login')
    item = getItem(itemid)
    newname, newcat, newdesc = item.name, item.category, item.description
    if(request.method == 'POST'):
        if request.form['name']:
            newname = request.form['name']
        if request.form['description']:
            newdesc = request.form['description']
        if request.form['category']:
            newcat = request.form['category']
        if request.form['imgurl']:
            newimg = request.form['imgurl']
        edit_itemDB(itemid, newname, newcat, newdesc, newimg)
        flash('item successfully edited')
        # redirect to the old category after editing, if it changed
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('editconfirmation.html', item=item,
                               categories=getCategories())


@app.route('/catalog/<category>/<int:itemid>/delete', methods=['GET', 'POST'])
def deleteItem(itemid, category):
    if 'username' not in login_session:
        flash('please login to do that')
        return redirect('/login')
    if(request.method == 'POST'):
        delete_itemDB(itemid)
        flash('item successfully deleted')
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('deleteconfirmation.html', itemid=itemid,
                               category=category, categories=getCategories())


@app.route('/catalog/addItem', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        flash('please login to do that')
        return redirect('/login')
    if(request.method == 'POST'):
        newname, newcat, newdesc, imgurl = "", "", "", ""
        if request.form['name']:
            newname = request.form['name']
        if request.form['category']:
            newcat = request.form['category']
        if request.form['description']:
            newdesc = request.form['description']
        if request.form['imgurl']:
            newimg = request.form['imgurl']
        itemid = add_ItemDB(newname, newcat, newdesc, newimg)
        print itemid, newname, newcat
        # redirect to newly created item
        return redirect(url_for('item', itemid=itemid, name=newname,
                                category=newcat))
    else:
        return render_template('addnewitem.html', categories=getCategories())

# Create anti-forgery state token


@app.route('/login')
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state,
                           categories=getCategories())


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:'\
        ' 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Check if a user is connected
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Execute HTTP GET request to revoke current token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('You are logged out')
        return redirect(url_for('catalogHome'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog')
def catalogHome():
    # Homepage shows 10 items in the catalog
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name', 'category',
                               'description', 'imgurl'])
    query = "SELECT * FROM items LIMIT 10"
    c.execute(query)
    items = c.fetchall()
    nameditems = [Item(*i) for i in items]

    c.close()
    db.close()
    return render_template('catalog.html', items=nameditems,
                           categories=getCategories())

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
