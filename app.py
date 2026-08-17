import os
import csv
from flask import Flask, render_template, request, jsonify
import joblib

app = Flask(__name__)

# Safely load the model
MODEL_PATH = 'model.pkl'
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    model = None
    print(f"Warning: {MODEL_PATH} not found. Please run train_model.py first.")

def load_students():
    students = []
    try:
        with open('students.csv', mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert marks to int for averaging and display
                row['marks'] = int(row['marks'])
                students.append(row)
    except Exception as e:
        print(f"Error loading students.csv: {e}")
    return students

def get_grade(marks):
    """Maps a numerical score to a letter grade based on typical distribution."""
    if marks >= 90: return "A"
    elif marks >= 80: return "B"
    elif marks >= 70: return "C"
    elif marks >= 60: return "D"
    else: return "F"

@app.route("/")
def index():
    students = load_students()
    avg = sum(student["marks"] for student in students) / len(students) if students else 0
    return render_template(
        "index.html",
        students=students,
        avg=round(avg, 2)
    )

@app.route("/health")
def health():
    return {
        "status": "ok",
        "server": "AWS EC2",
        "experiment": "E3"
    }, 200

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Machine learning model is not loaded. Train the model first.'}), 500

    try:
        data = request.json if request.is_json else request.form
        
        study_hours = float(data.get('study_hours_per_week', 0))
        attendance = float(data.get('attendance_percentage', 0))
        internal_score = float(data.get('internal_exam_score', 0))
        assignments = int(data.get('assignments_completed', 0))
        
        # Validation checks
        if not (0 <= study_hours <= 168):
            return jsonify({'error': 'Study hours must be between 0 and 168.'}), 400
        if not (0 <= attendance <= 100):
            return jsonify({'error': 'Attendance must be between 0 and 100.'}), 400
        if not (0 <= internal_score <= 100):
            return jsonify({'error': 'Internal score must be between 0 and 100.'}), 400
        if not (0 <= assignments <= 50):
            return jsonify({'error': 'Assignments completed must be reasonable (0-50).'}), 400

        features = [[study_hours, attendance, internal_score, assignments]]
        predicted_marks = model.predict(features)[0]
        
        predicted_marks = max(0.0, min(100.0, predicted_marks))
        predicted_grade = get_grade(predicted_marks)
        
        return jsonify({
            'predicted_marks': round(predicted_marks, 2),
            'predicted_grade': predicted_grade
        })
        
    except ValueError:
        return jsonify({'error': 'Invalid input type. Please provide valid numbers.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    # host='0.0.0.0' makes the server accessible
    # from outside the EC2 instance.
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )

