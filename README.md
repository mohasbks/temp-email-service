# Temporary Email Service

A web application that provides temporary email addresses using the Mail.tm API. Users can generate temporary email addresses, receive messages, and save their email addresses for later use.

## Features

- Generate temporary email addresses
- View inbox messages in real-time
- Save email addresses for future use
- Copy email addresses to clipboard
- Modern and responsive user interface

## Technology Stack

- Backend: Python/Flask
- Frontend: HTML, CSS, JavaScript
- Database: PostgreSQL (Production) / SQLite (Development)
- API: Mail.tm

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python app.py
   ```
4. Open http://localhost:5000 in your browser

## Production Deployment

This application is ready to be deployed on Render.com or similar platforms. Make sure to:

1. Set up a PostgreSQL database
2. Configure the DATABASE_URL environment variable
3. Deploy the application

## Environment Variables

- `DATABASE_URL`: PostgreSQL database URL (required in production)
- `PORT`: Port number (optional, defaults to 5000)
