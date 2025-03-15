import pytest
import tempfile
import os
import uuid
from app import app, init_db, get_db

@pytest.fixture
def client():
    test_db = tempfile.mktemp()
    os.environ['DATABASE'] = test_db
    init_db()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    if os.path.exists(test_db):
        os.unlink(test_db)

def test_hello_query(client):
    response = client.post(
        '/graphql',
        json={'query': '{ hello }'}
    )
    assert response.status_code == 200
    assert 'How can I help you today' in response.json['data']['hello']

def test_initial_bookings(client):
    response = client.post(
        '/graphql',
        json={'query': '{ bookings { id name profession date time } }'}
    )
    assert response.status_code == 200
    bookings = response.json['data']['bookings']
    assert len(bookings) > 0
    assert any(booking['name'] == 'Nicolas Woollett' for booking in bookings)

def test_create_booking(client):
    # Use a unique timestamp to avoid conflict
    unique_time = str(uuid.uuid4())[:8]
    mutation = f'''
    mutation {{
        createBooking(
            name: "Test User",
            profession: "Test Technician",
            date: "2023-06-20",
            time: "{unique_time}"
        ) {{
            id
            name
            profession
            date
            time
        }}
    }}
    '''
    response = client.post(
        '/graphql',
        json={'query': mutation}
    )

    print(response.json)

    assert response.status_code == 200
    assert 'createBooking' in response.json['data']
    booking = response.json['data']['createBooking']
    assert booking['name'] == 'Test User'
    assert booking['time'] == unique_time

def test_natural_language_booking(client):
    mutation = '''
    mutation {
        processNaturalLanguage(input: "I want to book a gardener for tomorrow")
    }
    '''
    response = client.post(
        '/graphql',
        json={'query': mutation}
    )
    assert response.status_code == 200
    result = response.json['data']['processNaturalLanguage']
    assert 'Booking confirmed' in result
    assert 'booking ID' in result

def test_natural_language_booking_id(client):
    create_mutation = '''
    mutation {
        processNaturalLanguage(input: "I want to book a gardener for tomorrow")
    }
    '''
    client.post('/graphql', json={'query': create_mutation})

    query = '''
    mutation {
        processNaturalLanguage(input: "What is my booking ID?")
    }
    '''
    response = client.post(
        '/graphql',
        json={'query': query}
    )
    assert response.status_code == 200
    assert 'Your last booking ID is' in response.json['data']['processNaturalLanguage']

def test_natural_language_cancel_booking(client):
    create_mutation = '''
    mutation {
        processNaturalLanguage(input: "I want to book a gardener for tomorrow")
    }
    '''
    create_response = client.post('/graphql', json={'query': create_mutation})

    create_result = create_response.json['data']['processNaturalLanguage']
    booking_id_match = create_result.split('Your booking ID is ')
    assert len(booking_id_match) > 1, "Could not extract booking ID"
    booking_id = booking_id_match[1].strip('.')

    cancel_mutation = f'''
    mutation {{
        processNaturalLanguage(input: "cancel booking {booking_id}")
    }}
    '''
    response = client.post(
        '/graphql',
        json={'query': cancel_mutation}
    )

    print(response.json)

    assert response.status_code == 200
    result = response.json['data']['processNaturalLanguage']
    assert 'cancelled' in result.lower()
