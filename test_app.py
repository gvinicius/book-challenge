import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_graphql_query(client):
    response = client.post(
        '/graphql',
        json={'query': '{ hello }'}
    )
    assert response.status_code == 200
    assert response.json['data']['hello'] == 'Hello, world!'
