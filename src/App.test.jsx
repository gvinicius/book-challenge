import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import App, { GET_BOOKINGS } from './App';

const mocks = [
  {
    request: {
      query: GET_BOOKINGS,
    },
    result: {
      data: {
        bookings: [
          {
            __typename: 'Booking',
            date: '15/10/2022',
            id: '1',
            name: 'Nicolas Woollett',
            profession: 'Plumber',
            time: '10:00',
          },
          {
            __typename: 'Booking',
            date: '16/10/2022',
            id: '2',
            name: 'Franky Flay',
            profession: 'Electrician',
            time: '18:00',
          },
          {
            __typename: 'Booking',
            date: '18/10/2022',
            id: '3',
            name: 'Griselda Dickson',
            profession: 'Welder',
            time: '11:00',
          },
        ],
      },
    },
  },
];

describe('BookingApp', () => {
  it('renders the page', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <App />
      </MockedProvider>
    );

    expect(await screen.findByText(/Technician Booking/i)).toBeTruthy();
    expect(await screen.findByText(/Nicolas Woollett/i)).toBeTruthy();
    expect(await screen.findByText(/Franky Flay/i)).toBeTruthy();
    expect(await screen.findByText(/Griselda Dickson/i)).toBeTruthy();
  });
});
