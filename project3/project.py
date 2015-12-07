from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2
from collections import namedtuple

app = Flask(__name__)


def connect():
    # returns connection and cursor for psql database
    try:
        db = psycopg2.connect("dbname=catalog")
        cursor = db.cursor()
        return db, cursor
    except:
        print("Could not connect to database.")


def addItem(name, category, description):
    # adds a new item to the item table
    db, c = connect()

    query = "INSERT INTO items(name, category, description) VALUES(%s, %s, %s);"
    param = (name, category, description)
    c.execute(query, param)

    db.commit()
    c.close()
    db.close()

def edit_itemDB(id, name, category, description):
    db, c = connect()

    query = "UPDATE items SET name = %s, category = %s, description = %s WHERE id = %s"
    param = (name, category, description, id)
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
    db, c = connect()
    query = "SELECT DISTINCT category FROM items ORDER BY category"
    c.execute(query)
    categories = c.fetchall()

    c.close()
    db.close()
    return categories

def getItem(itemid):
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name', 'category', 'description'])
    query = "SELECT * FROM items WHERE id=%s"
    param = (itemid,)
    c.execute(query, param)
    item = Item(*c.fetchone())

    c.close()
    db.close()
    return item

@app.route('/items')
def displayItems():
    db, c = connect()

    Item = namedtuple('Item', ['id', 'name', 'category', 'description'])
    query = "SELECT * FROM items"
    c.execute(query)
    items = c.fetchall()
    nameditems = [Item(*i) for i in items]

    c.close()
    db.close()
    return render_template('items.html', items=nameditems)

@app.route('/catalog/<category>')
def categoryItems(category):

    db, c = connect()

    Item = namedtuple('Item', ['id', 'name', 'category', 'description'])
    query = "SELECT * FROM items WHERE category=%s"
    param = (category,)
    c.execute(query, param)
    items = c.fetchall()
    nameditems = [Item(*i) for i in items]

    c.close()
    db.close()
    return render_template('categoryitems.html', items=nameditems, category=category, categories=getCategories())

@app.route('/catalog/<category>/<int:itemid>')
@app.route('/catalog/<category>/<int:itemid>/<name>')
def item(itemid, name, category):
    # I want to allow for multiple items with the same name
    return render_template('item.html', item=getItem(itemid), categories=getCategories())


@app.route('/catalog/<category>/<int:itemid>/edit', methods=['GET', 'POST'])
def editItem(itemid, category):
    if(request.method == 'POST'):
        item = getItem(itemid)
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        edit_itemDB(itemid, item.name, item.category, item.description)
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('editconfirmation.html', itemid=itemid, category=category)


@app.route('/catalog/<category>/<int:itemid>/delete', methods=['GET', 'POST'])
def deleteItem(itemid, category):
    if(request.method == 'POST'):
        delete_itemDB(itemid)
        flash('item successfully deleted')
        return redirect(url_for('categoryItems', category=category))
    else:
        return render_template('deleteconfirmation.html', itemid=itemid, category=category, categories=getCategories())


@app.route('/')
@app.route('/catalog')
def HelloWorld():
    return render_template('catalog.html', categories=getCategories())

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
