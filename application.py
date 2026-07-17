from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os

# Initialize Flask app
# AWS Elastic Beanstalk looks for a WSGI callable named "application" inside "application.py"
application = Flask(__name__)

# Paths to models
MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
Q_TABLE_PATH = os.path.join(os.path.dirname(__file__), "q_table.csv")

# Load models at startup
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Successfully loaded Linear Regression model.")
    else:
        model = None
        print("Warning: model.joblib not found. Linear Regression predictions will be unavailable.")
except Exception as e:
    model = None
    print(f"Error loading Linear Regression model: {e}")

try:
    if os.path.exists(Q_TABLE_PATH):
        # Read Q-table and set first column as index (low, medium, high)
        q_table = pd.read_csv(Q_TABLE_PATH, index_col=0)
        # Ensure column names are numeric price levels
        q_table.columns = [float(col) for col in q_table.columns]
        print("Successfully loaded Q-learning Table.")
    else:
        q_table = None
        print("Warning: q_table.csv not found. Q-learning predictions will be unavailable.")
except Exception as e:
    q_table = None
    print(f"Error loading Q-table: {e}")


def get_sentiment_state(score):
    """Categorizes numeric sentiment score to state matching Q-table indices."""
    if score < 0.1:
        return 'low'
    elif score < 0.2:
        return 'medium'
    else:
        return 'high'


@application.route("/health", methods=["GET"])
def health():
    """Health check endpoint for AWS Elastic Beanstalk monitoring."""
    return jsonify({
        "status": "healthy",
        "models_loaded": {
            "linear_regression": model is not None,
            "q_learning": q_table is not None
        }
    }), 200


@application.route("/predict", methods=["GET", "POST"])
def predict():
    """Exposes real-time event price prediction based on model inference."""
    # Support both GET query parameters and POST JSON requests
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
    else:
        data = request.args

    # Input extraction & validation
    try:
        genre_sentiment = float(data.get("genre_sentiment"))
        competitor_price = float(data.get("competitor_price"))
        web_demand = float(data.get("web_demand"))
    except (TypeError, ValueError) as e:
        return jsonify({
            "error": "Invalid or missing parameters. Required: 'genre_sentiment' (float), 'competitor_price' (float), and 'web_demand' (float)."
        }), 400

    results = {
        "inputs": {
            "genre_sentiment": genre_sentiment,
            "competitor_price": competitor_price,
            "web_demand": web_demand
        }
    }

    # 1. Inference with Linear Regression Model
    if model is not None:
        try:
            # Create a 1-row DataFrame matching training feature columns
            features = pd.DataFrame(
                [[genre_sentiment, competitor_price, web_demand]],
                columns=["sentiment", "competitor_price", "web_demand"]
            )
            lr_prediction = model.predict(features)[0]
            results["linear_regression_price"] = round(float(lr_prediction), 2)
        except Exception as e:
            results["linear_regression_price"] = None
            results["lr_error"] = str(e)
    else:
        results["linear_regression_price"] = None
        results["lr_error"] = "Model not loaded"

    # 2. Inference with Q-learning Policy
    if q_table is not None:
        try:
            state = get_sentiment_state(genre_sentiment)
            if state in q_table.index:
                # Find the column price level with the highest Q-value
                q_action = q_table.loc[state].idxmax()
                results["q_learning_price"] = float(q_action)
                results["q_learning_state"] = state
            else:
                results["q_learning_price"] = None
                results["q_learning_error"] = f"Unknown state: {state}"
        except Exception as e:
            results["q_learning_price"] = None
            results["q_learning_error"] = str(e)
    else:
        results["q_learning_price"] = None
        results["q_learning_error"] = "Q-table not loaded"

    return jsonify(results), 200


if __name__ == "__main__":
    # Host on 0.0.0.0 and port 5000 for local runs and dev environment
    application.run(host="0.0.0.0", port=5000, debug=True)
