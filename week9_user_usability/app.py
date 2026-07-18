from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def home():
    return render_template('home.html')

# -------------------- USER-FRIENDLY ROUTES --------------------
@app.route('/user_friendly', methods=['GET', 'POST'])
def user_friendly():
    if request.method == 'POST':
        session['uf_navigation'] = request.form.get('uf_navigation')
        session['uf_visuals'] = request.form.get('uf_visuals')
        session['uf_notes'] = request.form.get('uf_notes')
        return redirect(url_for('cognitive_walkthrough'))
    return render_template('user_friendly.html')

@app.route('/cognitive_walkthrough', methods=['GET', 'POST'])
def cognitive_walkthrough():
    if request.method == 'POST':
        session['cw_task'] = request.form.get('cw_task')
        session['cw_expectation'] = request.form.get('cw_expectation')
        session['cw_feedback'] = request.form.get('cw_feedback')
        return redirect(url_for('user_friendly_result'))
    return render_template('cognitive_walkthrough.html')

@app.route('/user_friendly_result', methods=['GET', 'POST'])
def user_friendly_result():
    if request.method == 'POST':
        session['uf_navigation'] = request.form.get('uf_navigation')
        session['uf_visuals'] = request.form.get('uf_visuals')
        session['uf_notes'] = request.form.get('uf_notes')
        return redirect(url_for('user_evaluation_results'))
    return render_template('user_friendly_result.html')

@app.route('/user_evaluation_results', methods=['GET', 'POST'])
def user_evaluation_results():
    if request.method == 'POST':
        session['uf_navigation'] = request.form.get('uf_navigation')
        session['uf_visuals'] = request.form.get('uf_visuals')
        session['uf_notes'] = request.form.get('uf_notes')
        return redirect('/user_evaluation_results')
    return render_template('user_evaluation_results.html')


# -------------------- USABILITY ROUTES --------------------
@app.route('/usability', methods=['GET', 'POST'])
def usability():
    if request.method == 'POST':
        session['task_result'] = request.form.get('task_result')
        session['task_difficulty'] = request.form.get('task_difficulty')
        session['task_feedback'] = request.form.get('task_feedback')
        session['time_taken'] = request.form.get('time_taken')
        return redirect(url_for('sus'))
    return render_template('usability.html',
                           task_result=session.get('task_result'),
                           task_difficulty=session.get('task_difficulty'),
                           task_feedback=session.get('task_feedback'))

@app.route('/sus', methods=['GET', 'POST'])
def sus():
    if request.method == 'POST':
        total_score = 0
        for i in range(1, 11):
            try:
                score = int(request.form.get(f'q{i}', 0))
            except:
                score = 0
            total_score += score
        sus_score = total_score * 2.5
        session['sus_score'] = sus_score
        session['sus_comment'] = request.form.get('sus_comment')
        session['sus_recommend'] = request.form.get('sus_recommend')
        return redirect(url_for('heuristics'))
    return render_template('sus.html',
                           sus_score=session.get('sus_score'),
                           sus_comment=session.get('sus_comment'),
                           sus_recommend=session.get('sus_recommend'))

@app.route('/heuristics', methods=['GET', 'POST'])
def heuristics():
    if request.method == 'POST':
        session['heuristics'] = request.form.getlist('heuristics')
        session['heuristic_notes'] = request.form.get('heuristic_notes')

        file = request.files.get('evidence_screenshot')
        if file and file.filename:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            session['heuristic_screenshot'] = filename

        return redirect(url_for('card_sorting'))
    return render_template('heuristics.html',
                           heuristics=session.get('heuristics'),
                           heuristic_notes=session.get('heuristic_notes'))

@app.route('/card_sorting', methods=['GET', 'POST'])
def card_sorting():
    if request.method == 'POST':
        session['card_sort_categories'] = request.form.get('card_sort_categories')
        session['card_sort_notes'] = request.form.get('card_sort_notes')
        return redirect(url_for('tree_testing'))
    return render_template('card_sorting.html',
                           card_sort_categories=session.get('card_sort_categories'),
                           card_sort_notes=session.get('card_sort_notes'))

@app.route('/tree_testing', methods=['GET', 'POST'])
def tree_testing():
    if request.method == 'POST':
        session['tree_test_success'] = request.form.get('tree_test_success')
        session['tree_test_confusion'] = request.form.get('tree_test_confusion')
        return redirect(url_for('ab_testing'))
    return render_template('tree_testing.html',
                           tree_test_success=session.get('tree_test_success'),
                           tree_test_confusion=session.get('tree_test_confusion'))

@app.route('/ab_testing', methods=['GET', 'POST'])
def ab_testing():
    if request.method == 'POST':
        session['ab_preference'] = request.form.get('ab_preference')
        session['ab_reason'] = request.form.get('ab_reason')
        return redirect(url_for('analytics'))
    return render_template('ab_testing.html',
                           ab_preference=session.get('ab_preference'),
                           ab_reason=session.get('ab_reason'))

@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    if request.method == 'POST':
        session['avg_session_time'] = request.form.get('avg_session_time')
        session['bounce_rate'] = request.form.get('bounce_rate')
        session['task_success_rate'] = request.form.get('task_success_rate')
        return redirect(url_for('results'))
    return render_template('analytics.html',
                           avg_session_time=session.get('avg_session_time'),
                           bounce_rate=session.get('bounce_rate'),
                           task_success_rate=session.get('task_success_rate'))

@app.route('/results', methods=['GET'])
def results():
    return render_template('results.html', data=session)

if __name__ == '__main__':
    app.run(debug=True)
