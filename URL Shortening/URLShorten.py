from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import hashlib

app = Flask(__name__, template_folder='C:/Users/alike/PycharmProjects/pythonProject2/URL Shortening')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///url_shortener.db'
db = SQLAlchemy(app)

class URLMapping(db.Model):
    short_url = db.Column(db.String(8), primary_key=True)
    original_url = db.Column(db.String(2048))

def create_tables():
    with app.app_context():
        db.create_all()

create_tables()  # Create tables when the application starts

def url_shortener(url):
    # Hash the URL using MD5
    hash_object = hashlib.md5(url.encode())
    hash_hex = hash_object.hexdigest()

    # Take the first 8 characters of the hash to create the short URL
    short_url = hash_hex[:8]

    # Store the mapping in the database
    db.session.merge(URLMapping(short_url=short_url, original_url=url))
    db.session.commit()

    return short_url

def url_exists(url):
    try:
        response = requests.head(url)
        return response.status_code < 400  # Check if status code is in the 2xx or 3xx range
    except requests.RequestException:
        return False  # If there's any error during the request, assume the URL does not exist

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    # Retrieve the URL submitted via the form
    original_url = request.form['url']

    # Check if the URL exists and is accessible
    if url_exists(original_url):
        # Generate the short URL
        short_url = url_shortener(original_url)

        # Redirect to the index page with the short URL as a parameter
        return render_template('index.html', short_url=short_url)
    else:
        # Return an error message if the URL is not accessible
        return render_template('index.html', error_message="The URL does not exist or could not be accessed.")

@app.route('/short/<short_url>')
def redirect_to_original(short_url):
    # Retrieve the original URL corresponding to the short URL from the database
    mapping = URLMapping.query.filter_by(short_url=short_url).first()

    if mapping:
        original_url = mapping.original_url
        # Redirect the user to the original URL
        return redirect(original_url)
    else:
        # Handle the case where the short URL is not found
        return render_template('error.html', error_message="Short URL not found")

if __name__ == '__main__':
    app.run(debug=True)
