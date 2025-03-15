from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sqlite3
import uuid
from ariadne import make_executable_schema, graphql_sync, ObjectType, MutationType
from datetime import datetime, timedelta
import re

app = Flask(__name__, static_folder='build')
CORS(app)

DATABASE = os.environ.get('DATABASE', 'bookings.db')
LAST_BOOKING_ID = None

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
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM bookings")
    if cursor.fetchone()[0] == 0:
        initial_bookings = [
            ('1', 'Nicolas Woollett', 'Plumber', '15/10/2022', '10:00'),
            ('2', 'Franky Flay', 'Electrician', '16/10/2022', '18:00'),
            ('3', 'Griselda Dickson', 'Welder', '18/10/2022', '11:00')
        ]
        cursor.executemany(
            "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
            initial_bookings
        )
    db.commit()
    db.close()

init_db()

type_defs = """
    type Query {
        hello: String!
        bookings: [Booking]
        booking(id: ID!): Booking
    }
    type Mutation {
        createBooking(name: String!, profession: String!, date: String!, time: String!): Booking
        deleteBooking(id: ID!): Boolean
        processNaturalLanguage(input: String!): String
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
    return "Hello! How can I help you today?"

@query.field("bookings")
def resolve_bookings(*_):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bookings")
    bookings = [dict(row) for row in cursor.fetchall()]
    db.close()
    return bookings

@query.field("booking")
def resolve_booking(*_, id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM bookings WHERE id = ?", (id,))
    booking = cursor.fetchone()
    db.close()
    return dict(booking) if booking else None

@mutation.field("createBooking")
def resolve_create_booking(*_, name, profession, date, time):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        "SELECT * FROM bookings WHERE profession = ? AND date = ? AND time = ?",
        (profession, date, time)
    )
    if cursor.fetchone():
        db.close()
        raise Exception("Time slot already booked")

    booking_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
        (booking_id, name, profession, date, time)
    )
    db.commit()

    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = dict(cursor.fetchone())

    global LAST_BOOKING_ID
    LAST_BOOKING_ID = booking_id

    db.close()
    return booking

@mutation.field("deleteBooking")
def resolve_delete_booking(*_, id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("DELETE FROM bookings WHERE id = ?", (id,))
    deleted = cursor.rowcount > 0

    db.commit()
    db.close()

    return deleted

@mutation.field("processNaturalLanguage")
def resolve_process_natural_language(*_, input):
    global LAST_BOOKING_ID
    input_lower = input.lower()
    db = get_db()
    cursor = db.cursor()

    # Book a gardener
    if 'book' in input_lower and 'gardener' in input_lower:
        booking_id = str(uuid.uuid4())
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        cursor.execute(
            "INSERT INTO bookings VALUES (?, ?, ?, ?, ?)",
            (booking_id, 'User', 'Gardener', tomorrow, '17:00')
        )
        db.commit()
        LAST_BOOKING_ID = booking_id
        db.close()
        return f"Booking confirmed for tomorrow at 5:00pm. Your booking ID is {booking_id}."

    if 'booking id' in input_lower:
        if LAST_BOOKING_ID:
            db.close()
            return f"Your last booking ID is {LAST_BOOKING_ID}."
        else:
            db.close()
            return "No bookings found."

    # Cancel booking
    if 'cancel booking' in input_lower:
        booking_id_to_cancel = LAST_BOOKING_ID

        match = re.search(r'cancel\s+booking\s+(\w+)', input_lower)
        if match:
            booking_id_to_cancel = match.group(1)

        if booking_id_to_cancel:
            cursor.execute("DELETE FROM bookings WHERE id = ?", (booking_id_to_cancel,))
            db.commit()
            LAST_BOOKING_ID = None
            db.close()
            return f"Booking {booking_id_to_cancel} cancelled."
        else:
            db.close()
            return "No booking to cancel."

    db.close()
    return "I'm not sure how to handle that request."

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
