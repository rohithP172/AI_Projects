from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = 'adaptive_secret_key'

with open('category_questions.json') as f:
    QUESTIONS = json.load(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        session['category'] = request.form['category']
        return redirect(url_for('userinfo'))
    return render_template('index.html', categories=list(QUESTIONS.keys()))

@app.route('/userinfo', methods=['GET', 'POST'])
def userinfo():
    if request.method == 'POST':
        session['first_name'] = request.form['first_name']
        session['last_name'] = request.form['last_name']
        session['email'] = request.form['email']
        session['questions'] = random.sample(QUESTIONS[session['category']], min(20, len(QUESTIONS[session['category']])))
        session['answers'] = []
        session['current'] = 0
        return redirect(url_for('quiz'))
    return render_template('userinfo.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if request.method == 'POST':
        session['answers'].append(request.form.get('answer'))
        session['current'] += 1
        if session['current'] >= len(session['questions']):
            return redirect(url_for('result'))
    current_q = session['questions'][session['current']]
    return render_template('quiz.html',
                           question=current_q,
                           current=session['current'] + 1,
                           total=len(session['questions']),
                           progress=int((session['current'] + 1) / len(session['questions']) * 100))

@app.route('/result')
def result():
    score = sum(1 for i, q in enumerate(session['questions']) if session['answers'][i] == q['answer'])
    return render_template('result.html',
                           name=f"{session['first_name']} {session['last_name']}",
                           email=session['email'],
                           score=score,
                           total=len(session['questions']))

if __name__ == '__main__':
    app.run(debug=True)
