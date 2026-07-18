from flask import Flask, render_template, request
import requests, wikipedia
from bs4 import BeautifulSoup

app = Flask(__name__)
OMDB_API_KEY = "2852a4f9"

def get_omdb_info(title):
    try:
        url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&t={title}"
        response = requests.get(url)
        data = response.json()
        if data.get("Response") == "True":
            genre_list = data.get("Genre", "").split(", ")
            return {
                "title": data.get("Title"),
                "year": data.get("Year"),
                "actors": data.get("Actors"),
                "rating": data.get("imdbRating"),
                "genre": genre_list,
                "source": "OMDb",
                "storyline": data.get("Plot"),
                "platform": "May be available on Netflix, Prime, Hulu, or Disney+",
                "link": f"https://www.google.com/search?q=watch+{title.replace(' ', '+')}+movie+online"
            }
    except:
        return None
    return None

def get_wikipedia_summary(title):
    try:
        summary = wikipedia.summary(title, sentences=2)
        page = wikipedia.page(title)
        return {
            "title": title,
            "storyline": summary,
            "source": "Wikipedia",
            "link": page.url
        }
    except:
        return None

def get_google_snippet(title):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://www.google.com/search?q={title.replace(' ', '+')}+movie"
        res = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        desc = soup.find("div", class_="BNeawe s3v9rd AP7Wnd")
        if desc:
            return {
                "title": title,
                "storyline": desc.text,
                "source": "Google",
                "link": url
            }
    except:
        return None

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/movie', methods=['POST'])
def movie():
    title = request.form["title"]
    info = get_omdb_info(title) or get_wikipedia_summary(title) or get_google_snippet(title)
    if not info:
        return render_template("not_found.html", title=title)

    # Similar movie suggestions (mocked by genre)
    similar = []
    if "genre" in info:
        genre = info["genre"][0]
        similar_url = f"http://www.omdbapi.com/?apikey={OMDB_API_KEY}&s={genre}"
        res = requests.get(similar_url).json()
        if res.get("Search"):
            for movie in res["Search"][:2]:
                similar.append(movie["Title"])

    return render_template("movie.html", movie=info, similar=similar)

if __name__ == "__main__":
    app.run(debug=True)
