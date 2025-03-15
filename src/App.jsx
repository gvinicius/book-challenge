import React, { useState, useEffect } from 'react';

function App() {
  const [bookings, setBookings] = useState([]);
  const [name, setName] = useState('');
  const [profession, setProfession] = useState('');
  const [date, setDate] = useState('');
  const [time, setTime] = useState('');

  useEffect(() => {
    fetch('http://localhost:5000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '{ bookings { id name profession date time } }' })
    })
    .then(res => res.json())
    .then(result => {
      if (result.data && result.data.bookings) {
        setBookings(result.data.bookings);
      }
    });
  }, []);

  // Create booking
  const handleSubmit = (e) => {
    e.preventDefault();

    fetch('http://localhost:5000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: `mutation {
          createBooking(
            name: "${name}",
            profession: "${profession}",
            date: "${date}",
            time: "${time}"
          ) {
            id name profession date time
          }
        }`
      })
    })
    .then(res => res.json())
    .then(result => {
      if (result.data && result.data.createBooking) {
        setBookings([...bookings, result.data.createBooking]);
        setName('');
        setProfession('');
        setDate('');
        setTime('');
      }
    });
  };

  return (
    <div>
      <h1>Technician Booking System</h1>

      <form className="form" onSubmit={handleSubmit}>
        <input
          placeholder="Name"
          value={name}
          onChange={e => setName(e.target.value)}
          required
        />
        <input
          placeholder="Profession"
          value={profession}
          onChange={e => setProfession(e.target.value)}
          required
        />
        <input
          placeholder="Date"
          value={date}
          onChange={e => setDate(e.target.value)}
          required
        />
        <input
          placeholder="Time"
          value={time}
          onChange={e => setTime(e.target.value)}
          required
        />
        <button type="submit">Book</button>
      </form>

      <h2>Bookings</h2>
      {bookings.length === 0 ? (
        <p>No bookings yet</p>
      ) : (
        bookings.map(booking => (
          <div className="booking" key={booking.id}>
            <p><strong>{booking.name}</strong> - {booking.profession}</p>
            <p>{booking.date} at {booking.time}</p>
          </div>
        ))
      )}
    </div>
  );
}

export default App;
