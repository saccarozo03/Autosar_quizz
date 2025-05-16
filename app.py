from flask import Flask, render_template, request, session, redirect, url_for
import json
import os
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Đổi thành chuỗi bất kỳ

QUIZ_FOLDER = os.path.join(os.path.dirname(__file__), 'quizzes')

def is_valid_quiz_id(quiz_id):
    # Only allow alphanumeric characters and underscores
    return bool(re.match(r'^[a-zA-Z0-9_]+$', quiz_id))

def get_available_quizzes():
    quizzes = []
    for file in os.listdir("quizzes"):
        if file.endswith(".json"):
            quiz_id = file[:-5]  # Remove .json extension
            if is_valid_quiz_id(quiz_id):
                quizzes.append(quiz_id)
    return quizzes

def load_quiz(quiz_id):
    if not is_valid_quiz_id(quiz_id):
        return None
        
    path = f"quizzes/{quiz_id}.json"
    if not os.path.exists(path):
        return None
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)
            # Validate quiz data structure
            if not isinstance(quiz_data, list):
                return None
            for q in quiz_data:
                if not isinstance(q, dict) or 'answer' not in q:
                    return None
            return quiz_data
    except (json.JSONDecodeError, IOError):
        return None

@app.route("/")
def home():
    quizzes = []
    for fname in os.listdir(QUIZ_FOLDER):
        if fname.endswith('.json'):
            quizzes.append(fname[:-5])
    user_scores = session.get('user_scores', {})
    quiz_lengths = {}
    for quiz in quizzes:
        try:
            with open(os.path.join(QUIZ_FOLDER, quiz + '.json'), encoding='utf-8') as f:
                questions = json.load(f)
                quiz_lengths[quiz] = len(questions)
        except Exception:
            quiz_lengths[quiz] = 0
    return render_template('home.html', quizzes=quizzes, user_scores=user_scores, quiz_lengths=quiz_lengths)

@app.route("/quiz/<quiz_id>", methods=["GET", "POST"])
def quiz(quiz_id):
    quiz_file = os.path.join(QUIZ_FOLDER, quiz_id + '.json')
    if not os.path.exists(quiz_file):
        return "Quiz not found", 404
    with open(quiz_file, encoding='utf-8') as f:
        questions = json.load(f)
    show_results = False
    score = 0
    user_answers = []
    if request.method == "POST":
        show_results = True
        for i, q in enumerate(questions):
            ans = request.form.get(f'q{i}')
            user_answers.append(ans)
            if ans == q['answer']:
                score += 1
        # Lưu điểm vào session
        user_scores = session.get('user_scores', {})
        prev_score = user_scores.get(quiz_id, 0)
        if score > prev_score:
            user_scores[quiz_id] = score
            session['user_scores'] = user_scores
    return render_template("quiz.html",
                           questions=questions,
                           quiz_id=quiz_id,
                           show_results=show_results,
                           score=score,
                           user_answers=user_answers)

if __name__ == "__main__":
    app.run(debug=True)
