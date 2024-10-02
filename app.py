from flask import Flask, render_template, request, redirect, url_for, jsonify  # Import necessary Flask functions
from flask_sqlalchemy import SQLAlchemy
import google.generativeai as genai
import os

# Configure the Gemini API
os.environ["API_KEY"] = 'API KEY HERE'  # Replace with your actual API key
genai.configure(api_key=os.environ["API_KEY"])

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Define a database model for storing user names
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

# Home route to display motivational quote and collect the user's name
@app.route('/', methods=['GET', 'POST'])
def index():
    quote = get_motivational_quote()

    if request.method == 'POST':
        user_name = request.form['name']
        new_user = User(name=user_name)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('thank_you', name=user_name))  # Redirect to thank you page after submitting name

    return render_template('index.html', quote=quote)

# Route for the thank you page
@app.route('/thank_you/<name>')
def thank_you(name):
    return render_template('thank_you.html', name=name)

# Route to render chatbot interface
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_message = request.json.get('message')  # Get the user's message from the frontend
        response = get_ai_response(user_message)  # Get AI's response using Gemini API
        return jsonify({"response": response})

    return render_template('chatbot.html')

# Helper function to get the motivational quote from Gemini API
def get_motivational_quote():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = "Provide a motivational quote from classic Chinese literature."
        response = model.generate_content(prompt)
        return response.text if response.text else "The journey of a thousand miles begins with a single step. - Laozi"
    except Exception as e:
        print(f"Error fetching quote: {e}")
        return "The journey of a thousand miles begins with a single step. - Laozi"

# Helper function to get AI response from Gemini API
def get_ai_response(message):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"Respond with empathy and guidance and hold a good and positive conversation, provide answers that can help someone's mental health when needed: {message}"
        response = model.generate_content(prompt)
        return response.text if response.text else "I'm here to listen. Tell me more."
    except Exception as e:
        print(f"Error fetching AI response: {e}")
        return "Sorry, I am having trouble processing your request. Please try again."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
