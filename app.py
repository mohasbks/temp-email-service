from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import random
import string
import requests
import json
import time
import os

app = Flask(__name__)
CORS(app)

# Database configuration
if os.environ.get('DATABASE_URL'):
    # Use PostgreSQL in production
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL').replace('postgres://', 'postgresql://')
else:
    # Use SQLite in development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///emails.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

API_URL = "https://api.mail.tm"

# Database Model
class SavedEmail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    token = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }

def generate_password(length=12):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_available_domains():
    try:
        response = requests.get(f"{API_URL}/domains")
        response.raise_for_status()
        domains = response.json()
        if domains.get('hydra:member'):
            return domains['hydra:member'][0]['domain']
        return None
    except Exception as e:
        print(f"Error getting domains: {str(e)}")
        return None

def create_account():
    try:
        # Get available domain
        domain = get_available_domains()
        if not domain:
            raise Exception("No available domains")

        # Generate random username and password
        username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        password = generate_password()
        email = f"{username}@{domain}"

        # Create account
        account_data = {
            "address": email,
            "password": password
        }
        
        response = requests.post(
            f"{API_URL}/accounts",
            json=account_data
        )
        response.raise_for_status()
        
        # Get token
        token_data = {
            "address": email,
            "password": password
        }
        token_response = requests.post(
            f"{API_URL}/token",
            json=token_data
        )
        token_response.raise_for_status()
        token = token_response.json().get('token')
        
        return {
            "email": email,
            "token": token
        }
    except Exception as e:
        print(f"Error creating account: {str(e)}")
        return None

def get_messages(token):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/messages",
            headers=headers
        )
        response.raise_for_status()
        messages = response.json()
        return messages.get('hydra:member', [])
    except Exception as e:
        print(f"Error getting messages: {str(e)}")
        return []

def get_message(token, message_id):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{API_URL}/messages/{message_id}",
            headers=headers
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error getting message: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    account = create_account()
    if account:
        # Save the email and token to database
        saved_email = SavedEmail(
            email=account['email'],
            token=account['token']
        )
        db.session.add(saved_email)
        db.session.commit()
        return jsonify(account)
    return jsonify({'error': 'Failed to generate email'}), 500

@app.route('/messages', methods=['POST'])
def messages():
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    messages = get_messages(token)
    return jsonify({'messages': messages})

@app.route('/message/<message_id>', methods=['POST'])
def message(message_id):
    data = request.get_json()
    token = data.get('token')
    if not token:
        return jsonify({'error': 'Token is required'}), 400
    
    message = get_message(token, message_id)
    if message:
        return jsonify({'message': message})
    return jsonify({'error': 'Failed to fetch message'}), 500

@app.route('/saved-emails', methods=['GET'])
def get_saved_emails():
    saved_emails = SavedEmail.query.order_by(SavedEmail.created_at.desc()).all()
    return jsonify({'emails': [email.to_dict() for email in saved_emails]})

@app.route('/load-email/<int:email_id>', methods=['GET'])
def load_email(email_id):
    saved_email = SavedEmail.query.get_or_404(email_id)
    return jsonify({
        'email': saved_email.email,
        'token': saved_email.token
    })

# Create tables in development
if not os.environ.get('DATABASE_URL'):
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
