import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import joblib

def train_and_export_model():
    csv_path = 'students.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print("Loading data from students.csv...")
    df = pd.read_csv(csv_path)
    
    # Features and Target
    # Columns: name,roll,study_hours_per_week,attendance_percentage,internal_exam_score,assignments_completed,marks,grade
    features = ['study_hours_per_week', 'attendance_percentage', 'internal_exam_score', 'assignments_completed']
    X = df[features]
    y = df['marks']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training model...")
    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
    ])
    
    pipeline.fit(X_train, y_train)
    
    score = pipeline.score(X_test, y_test)
    print(f"Model R^2 Score on Test Set: {score:.4f}")
    
    print("Exporting model to model.pkl...")
    joblib.dump(pipeline, 'model.pkl')
    print("Done! model.pkl is ready.")

if __name__ == "__main__":
    train_and_export_model()
