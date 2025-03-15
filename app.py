from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3
from ariadne import make_executable_schema, graphql_sync, ObjectType, MutationType

app = Flask(__name__, static_folder='build')
CORS(app)

# SQLite setup
DATABASE = 'bookings.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    db.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            profession TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL
        )
    ''')
    db.commit()
    db.close()

init_db()

type_defs = """
    type Query {
        hello: String!
        bookings: [Booking]
    }

    type Mutation {
        createBooking(name: String!, profession: String!, date: String!, time: String!): Booking
    }

    type Booking {
        id: ID!
        name: String!
        profession: String!
        date: String!
        time: String!
    }
"""

query = ObjectType("Query")
mutation = MutationType()

@query.field("hello")
def resolve_hello(*_):
    return "Hello, world!"

@query.field("bookings")
def resolve_bookings(*_):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bookings")
    bookings = [dict(row) for row in cursor.fetchall()]
    db.close()
    return bookings

@mutation.field("createBooking")
def resolve_create_booking(*_, name, profession, date, time):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(*) FROM bookings")
    count = cursor.fetchone()[0]
    booking_id = str(count + 1)

    cursor.execute(
        "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
        (booking_id, name, profession, date, time)
    )
    db.commit()

    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = dict(cursor.fetchone())
    db.close()

    return booking

schema = make_executable_schema(type_defs, [query, mutation])

@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
