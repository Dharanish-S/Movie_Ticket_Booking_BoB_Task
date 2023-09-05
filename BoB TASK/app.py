from flask import Flask, render_template, request, redirect, url_for, session
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Replace with your own secret key

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB URI
db = client["movie_ticket_booking"]

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/booktickets')
def book_tickets():
    # Retrieve movies currently showing from MongoDB
    movies = db.movies.find()
    return render_template('booktickets.html', movies=movies)

@app.route('/seat', methods=['GET', 'POST'])
def seat():
    if request.method == 'POST':
        # Process user's seat selection and store in session
        selected_date = request.form['date']
        selected_time = request.form['time']
        selected_seats = request.form.getlist('seats')

        session['selected_date'] = selected_date
        session['selected_time'] = selected_time
        session['selected_seats'] = selected_seats

        return redirect(url_for('payment'))

    return render_template('seat.html')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if request.method == 'POST':
        # Process payment details and save booking information to MongoDB
        user_name = request.form['name']
        card_number = request.form['card_number']

        booking = {
            'user_name': user_name,
            'movie_name': session.get('selected_movie'),
            'date': session.get('selected_date'),
            'time': session.get('selected_time'),
            'seats': session.get('selected_seats'),
            'booking_time': datetime.now()
        }

        db.bookings.insert_one(booking)

        return redirect(url_for('booked'))

    return render_template('payment.html')

@app.route('/booked')
def booked():
    # Retrieve booking information from session
    movie_name = session.get('selected_movie')
    date = session.get('selected_date')
    time = session.get('selected_time')

    # Clear session data
    session.pop('selected_movie', None)
    session.pop('selected_date', None)
    session.pop('selected_time', None)
    session.pop('selected_seats', None)

    return render_template('booked.html', movie_name=movie_name, date=date, time=time)

if __name__ == '__main__':
    app.run(debug=True)
