import React, { useState } from 'react'
import { gql, useMutation, useQuery } from '@apollo/client'

const PROCESS_NATURAL_LANGUAGE = gql`
  mutation ProcessMessage($input: String!) {
    processNaturalLanguage(input: $input)
  }
`

export const GET_BOOKINGS = gql`
  query GetBookings {
    bookings {
      id
      name
      profession
      date
      time
    }
  }
`

function App() {
  const [messages, setMessages] = useState([
    { id: 0, text: "Hello! How can I help you today?", sender: 'system' }
  ])
  const [inputMessage, setInputMessage] = useState('')

  const [processMessage] = useMutation(PROCESS_NATURAL_LANGUAGE)
  const { data: bookingsData } = useQuery(GET_BOOKINGS)

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage = {
      id: Date.now(),
      text: inputMessage,
      sender: 'user'
    }

    setMessages(prev => [...prev, userMessage])

    try {
      const { data } = await processMessage({
        variables: { input: inputMessage }
      })

      const systemMessage = {
        id: Date.now() + 1,
        text: data.processNaturalLanguage,
        sender: 'system'
      }

      setMessages(prev => [...prev, systemMessage])
    } catch (error) {
      console.error('Message processing error:', error)
    }

    setInputMessage('')
  }

  return (
    <div style={{
      maxWidth: '28rem',
      margin: '0 auto',
      padding: '1rem',
      fontFamily: 'Arial, sans-serif'
    }}>
      <h1 style={{
        fontSize: '1.5rem',
        fontWeight: 'bold',
        marginBottom: '1rem',
        textAlign: 'center'
      }}>
        Technician Booking
      </h1>

      <div style={{
        border: '1px solid #e0e0e0',
        borderRadius: '0.5rem',
        height: '24rem',
        overflowY: 'auto',
        marginBottom: '1rem',
        padding: '0.5rem'
      }}>
        {messages.map((msg) => (
          <div
            key={msg.id}
            style={{
              display: 'flex',
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '0.5rem'
            }}
          >
            <div
              style={{
                maxWidth: '80%',
                padding: '0.5rem',
                borderRadius: '0.5rem',
                backgroundColor: msg.sender === 'user' ? '#2196f3' : '#e0e0e0',
                color: msg.sender === 'user' ? 'white' : 'black'
              }}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      <div style={{
        display: 'flex',
        alignItems: 'center'
      }}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message..."
          style={{
            flexGrow: 1,
            padding: '0.5rem',
            border: '1px solid #ccc',
            borderRadius: '0.25rem',
            marginRight: '0.5rem'
          }}
        />
        <button
          onClick={handleSendMessage}
          style={{
            backgroundColor: '#2196f3',
            color: 'white',
            padding: '0.5rem 1rem',
            border: 'none',
            borderRadius: '0.25rem',
            cursor: 'pointer'
          }}
        >
          Send
        </button>
      </div>

      <div style={{ marginTop: '1rem' }}>
        <h2 style={{
          fontSize: '1.25rem',
          fontWeight: 'bold',
          marginBottom: '0.5rem'
        }}>
          Current Bookings
        </h2>
        <ul>
          {bookingsData?.bookings.map((booking) => (
            <li
              key={booking.id}
              style={{
                padding: '0.5rem',
                border: '1px solid #e0e0e0',
                borderRadius: '0.25rem',
                marginBottom: '0.5rem'
              }}
            >
              {booking.name} - {booking.profession} on {booking.date} at {booking.time}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

export default App
