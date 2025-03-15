# Technician Booking System

A compact Flask + GraphQL (Ariadne) + React application for managing technician bookings.
Use an interactive chat that runs natural language processing in order to book a time.

## Tools

- GraphQL API for all booking operations
- SQLite database for data persistence
- React frontend with Material UI

## Backend Setup

1. Install dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

2. Run the Flask server:
   ```bash
   python app.py
   ```

   The backend will start at http://127.0.0.1:5000

3. Test with curl:
   ```bash
   curl -X POST \
     -H "Content-Type: application/json" \
     -d '{"query": "{ hello }"}' \
     http://127.0.0.1:5000/graphql
   ```

## Frontend Setup

1. Install dependencies:
   ```bash
   npm i
   ```

2. Start the development server:
   ```bash
   npm start
   ```

   The frontend will be available at http://localhost:5173

## Running Backend Tests

Run the tests with pytest:
```bash
pytest test_app.py
```

## Running Frontend Tests

Run the tests with vitest:
```bash
npm test
```
