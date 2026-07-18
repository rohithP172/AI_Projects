from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required to use sessions

# ---- Your existing code remains unchanged ----

def search_google_books(title):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={title}")
    if response.status_code == 200:
        data = response.json()
        if 'items' in data and len(data['items']) > 0:
            book = data['items'][0]['volumeInfo']
            return {
                'title': book.get('title', 'Not found'),
                'authors': ', '.join(book.get('authors', [])),
                'description': book.get('description', 'No description available.')[:300] + "...",
                'thumbnail': book.get('imageLinks', {}).get('thumbnail', ''),
                'genre': ', '.join(book.get('categories', [])),
                'preview': book.get('previewLink', ''),
                'rating': book.get('averageRating', 'N/A'),
                'pageCount': book.get('pageCount', 'N/A'),
                'mood': infer_mood_from_title(title)
            }
    return None

def infer_mood_from_title(title):
    title = title.lower()
    if any(word in title for word in ['happy', 'joy', 'funny', 'comedy']):
        return 'Uplifting'
    elif any(word in title for word in ['sad', 'loss', 'tragedy', 'dark']):
        return 'Emotional'
    elif any(word in title for word in ['mystery', 'detective', 'thriller', 'crime']):
        return 'Suspenseful'
    elif any(word in title for word in ['love', 'romance', 'heart']):
        return 'Romantic'
    elif any(word in title for word in ['war', 'battle', 'history']):
        return 'Historical'
    elif any(word in title for word in ['fantasy', 'magic', 'dragon']):
        return 'Fantasy'
    elif any(word in title for word in ['space', 'alien', 'robot']):
        return 'Sci-Fi'
    else:
        return 'General'

def get_similar_books(title):
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q=related+to+{title}")
    similar = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', [])[1:4]:
            info = item.get('volumeInfo', {})
            similar.append({
                'title': info.get('title', 'Unknown'),
                'description': info.get('description', 'No description.')[:200] + "...",
                'thumbnail': info.get('imageLinks', {}).get('thumbnail', '')
            })
    return similar

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    title = request.form['book'].strip()
    book_info = search_google_books(title)
    if not book_info or book_info['title'] == 'Not found':
        return render_template('index.html', error="No book found. Please try a different title or genre.")
    similar_books = get_similar_books(title)
    return render_template('index.html', book_info=book_info, similar_books=similar_books)

@app.route('/add_favorite', methods=['POST'])
def add_favorite():
    book = {
        'title': request.form['title'],
        'authors': request.form['authors'],
        'thumbnail': request.form['thumbnail']
    }
    if 'favorites' not in session:
        session['favorites'] = []
    session['favorites'].append(book)
    session.modified = True
    return redirect(url_for('home'))

@app.route('/favorites')
def favorites():
    favs = session.get('favorites', [])
    return render_template('favorites.html', favorites=favs)

@app.route('/autocomplete')
def autocomplete():
    query = request.args.get("q", "")
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query}")
    suggestions = []
    if response.status_code == 200:
        data = response.json()
        suggestions = [item["volumeInfo"]["title"] for item in data.get("items", [])[:5]]
    return jsonify(suggestions)

@app.route('/chatbot', methods=['POST'])
def chatbot():
    message = request.json.get("message", "").lower()
    if "sad" in message and "fantasy" in message:
        return jsonify(response="You might enjoy an emotional fantasy like *The Name of the Wind* or *The Ocean at the End of the Lane*.")
    elif "happy" in message and "romance" in message:
        return jsonify(response="Try uplifting romances like *The Rosie Project* or *To All the Boys I've Loved Before*.")
    elif "sad" in message:
        return jsonify(response="You might like emotional books such as *A Man Called Ove* or *The Fault in Our Stars*.")
    elif "happy" in message:
        return jsonify(response="Try uplifting reads like *The Alchemist* or *Eleanor Oliphant Is Completely Fine*.")
    elif "love" in message or "romantic" in message:
        return jsonify(response="How about romantic titles like *Pride and Prejudice* or *Me Before You*?")
    elif "mystery" in message or "thriller" in message:
        return jsonify(response="You could enjoy thrillers like *Gone Girl* or *The Girl with the Dragon Tattoo*.")
    elif "fantasy" in message:
        return jsonify(response="Explore fantasy worlds in *Harry Potter*, *The Hobbit*, or *A Game of Thrones*.")
    elif "sci-fi" in message or "science fiction" in message:
        return jsonify(response="Check out science fiction books like *Dune*, *Ender's Game*, or *The Martian*.")
    elif "history" in message:
        return jsonify(response="Consider historical reads like *The Book Thief* or *All the Light We Cannot See*.")
    elif "self-help" in message or "motivational" in message:
        return jsonify(response="Books like *Atomic Habits*, *The Power of Now*, or *You Are a Badass* might help uplift your mood.")
    else:
        return jsonify(response="I recommend trying *The Midnight Library* or *Atomic Habits*. You can also ask by mood or genre!")

if __name__ == '__main__':
    app.run(debug=True)
