from flask import Flask
app = Flask(__name__)

import psycopg2


def connect():
    try:
        db = psycopg2.connect("dbname=catalog")
        cursor = db.cursor()
        return db, cursor
    except:
        print("Could not connect to database.")

def addItem(name, category, description):
	db, c = connect()

	query = "INSERT INTO items(name, category, description) VALUES(%s, %s, %s);"
	param = (name, category, description)
	c.execute(query, param)

	db.commit()
	c.close()
	db.close()

def removeItem(id):
	db, c = connect()

	query = "DELETE FROM items WHERE id=%s"
	param = (id,)
	c.execute(query, param)

	db.commit()
	c.close()
	db.close()


@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello World"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)