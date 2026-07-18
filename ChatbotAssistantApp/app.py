from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import random
import wikipedia
from textblob import TextBlob

app = Flask(__name__, template_folder="templates")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/assistant')
def assistant():
    return render_template('assistant.html')

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"
GOOGLE_CSE_ID = "YOUR_CSE_ID"

@app.route('/chatbot/query', methods=['POST'])
def chatbot_query():
    data = request.get_json()
    question = data.get('query', '').strip()
    response = ""

    if not question:
        return jsonify({'response': "Please ask me something so I can help!"})

    try:
        # 1. Google Custom Search API
        google_url = f"https://www.googleapis.com/customsearch/v1?q={question}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}"
        google_res = requests.get(google_url)
        if google_res.status_code == 200:
            google_data = google_res.json()
            if 'items' in google_data and len(google_data['items']) > 0:
                top_result = google_data['items'][0]
                response = top_result.get('snippet', '')

        # 2. Wikipedia fallback
        if not response:
            try:
                summary = wikipedia.summary(question, sentences=2)
                response = summary
            except wikipedia.exceptions.DisambiguationError as e:
                response = f"This topic is broad. Try something like: {e.options[0]}"
            except wikipedia.exceptions.PageError:
                response = ""

        # 3. DuckDuckGo fallback
        if not response:
            ddg_res = requests.get(f"https://api.duckduckgo.com/?q={question}&format=json&no_redirect=1&skip_disambig=1")
            if ddg_res.status_code == 200:
                ddg_data = ddg_res.json()
                response = ddg_data.get('Abstract') or ddg_data.get('Heading') or "I couldn’t find anything useful."

        # 4. Sentiment Detection
        blob = TextBlob(question)
        if blob.sentiment.polarity < -0.3:
            response += " I sense you're feeling down. I'm here for you."

    except Exception as e:
        print(f"Error: {e}")
        response = "Oops! Something went wrong while processing your question."

    return jsonify({'response': response})

@app.route('/assistant/query', methods=['POST'])
def assistant_query():
    data = request.get_json()
    user_input = data.get('query', '').lower()
    now = datetime.now()
    sentiment = TextBlob(user_input).sentiment.polarity

    mood_books = {
        "happy": ["The Alchemist by Paulo Coelho", "The Rosie Project by Graeme Simsion"],
        "sad": ["A Man Called Ove by Fredrik Backman", "Eleanor Oliphant Is Completely Fine by Gail Honeyman"],
        "motivated": ["Atomic Habits by James Clear", "Grit by Angela Duckworth"],
        "tired": ["The Midnight Library by Matt Haig", "Big Magic by Elizabeth Gilbert"]
    }
    mood_music = {
        "happy": ["Happy - Pharrell Williams", "Walking on Sunshine - Katrina & The Waves"],
        "sad": ["Fix You - Coldplay", "Someone Like You - Adele"],
        "motivated": ["Stronger - Kanye West", "Eye of the Tiger - Survivor"],
        "tired": ["Weightless - Marconi Union", "Breathe Me - Sia"]
    }


    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(greet in user_input for greet in greetings):
        response = "Hey there! I'm Ava — your assistant. How can I help you today?"
    elif 'time' in user_input and 'date' in user_input:
        response = f"Today is {now.strftime('%A, %B %d, %Y')} and it's {now.strftime('%H:%M:%S')} right now."
    elif 'time' in user_input:
        response = f"It's currently {now.strftime('%H:%M:%S')}."
    elif 'date' in user_input:
        response = f"Today's date is {now.strftime('%A, %B %d, %Y')}."
    elif 'reminder' in user_input:
        response = "Got it! Your reminder is set."
    elif 'weather' in user_input:
        response = "Looks like it's sunny with some clouds — perfect for a walk!"
    elif 'name' in user_input or 'who are you' in user_input:
        response = "I'm Ava, your friendly virtual assistant. Like Siri, but sassier!"
    elif 'joke' in user_input:
        response = "Why did the developer go broke? Because they used up all their cache!"
    elif 'motivate' in user_input or 'quote' in user_input:
        response = "Believe in yourself. You're capable of amazing things."
    elif 'birthday' in user_input:
        response = "Wishing you the happiest birthday ever! 🎉"
    elif 'fun fact' in user_input:
        response = "Fun fact: Bananas are berries, but strawberries aren't!"
    elif 'add to my list' in user_input or 'add task' in user_input:
        response = "I’ve added that to your list!"
    elif 'set a timer' in user_input:
        response = "Timer started! 5 minutes and counting ⏳"
    elif 'where am i' in user_input:
        response = "You're virtually in Denton, Texas – go Mean Green!"
    elif 'what can you do' in user_input:
        response = "I can help with reminders, weather, books, motivation, jokes, and more!"
    elif 'thank you' in user_input or 'thanks' in user_input:
        response = "You're very welcome! 😊 Always here if you need me."
    elif 'bye' in user_input or 'goodbye' in user_input:
        response = "Goodbye! Take care and have a great day ahead!"
    elif 'music' in user_input or 'song' in user_input:
        mood = "motivated" if sentiment > 0.5 else "sad" if sentiment < -0.2 else "tired"
        song = random.choice(mood_music[mood])
        response = f"Let me lift your mood with this song: {song}"
    elif 'story' in user_input:
        response = "Once upon a time, you asked a chatbot for a story, and it replied with kindness. The end... or the beginning?"
    elif any(mood in user_input for mood in mood_books):
        for mood in mood_books:
            if mood in user_input:
                book = random.choice(mood_books[mood])
                response = f"Sounds like a {mood} day. Try reading: {book}"
                break
    else:
        response = "Hmm, I didn’t catch that. Could you rephrase it for me?"

    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
