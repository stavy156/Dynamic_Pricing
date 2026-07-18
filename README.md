# Dynamic Pricing Model for Local Events

This project implements an end-to-end dynamic pricing engine for local events and experiences. It combines web demand signals, competitor pricing, and public sentiment to output recommended event ticket prices. The system features a research pipeline, a standalone training script, and a Flask REST API configured for deployment to AWS Elastic Beanstalk.

## Project Structure

* **DynamicPrice_project.ipynb**: The development notebook used for web scraping prototyping, exploratory data analysis, and model validation.
* **train_models.py**: The production training script that generates the dataset, trains the machine learning models, and saves the outputs.
* **application.py**: The Flask REST API that loads the trained models and exposes prediction endpoints.
* **requirements.txt**: The list of Python library dependencies required for the project.
* **Procfile**: Defines the command AWS Elastic Beanstalk uses to start the web application.
* **.ebextensions/flask.config**: Configuration file instructing AWS Elastic Beanstalk to route web traffic to the Flask application.
* **model.joblib**: The saved Linear Regression model.
* **q_table.csv**: The saved lookup table containing optimal pricing actions learned from Reinforcement Learning.

## How the Models Work

1. **Linear Regression**: Predicts recommended ticket prices based on numerical inputs including competitor pricing, web search demand, and public sentiment scores.
2. **Reinforcement Learning (Q-Learning)**: Optimizes ticket prices dynamically by mapping sentiment categories (low, medium, high) to price points that maximize normalized revenue rewards.

## Getting Started

### Prerequisites
Make sure your Python virtual environment is activated and dependencies are installed:
```bash
pip install -r requirements.txt
```

### 1. Train the Models
To train the models and generate the serialization files, run the standalone pipeline:
```bash
python train_models.py
```

### 2. Start the REST API
Run the Flask server locally:
```bash
python application.py
```
The server will start on http://127.0.0.1:5000.
or on the browser run this - http://127.0.0.1:5000/predict?genre_sentiment=0.35&competitor_price=750&web_demand=82 ---can change values

### 3. API Endpoints

* **Health Check**:
  * URL: `/health`
  * Method: GET
  * Description: Verifies that the server is active and the models are successfully loaded.
* **Predict Price**:
  * URL: `/predict`
  * Method: GET or POST
  * Parameters:
    * `genre_sentiment`: Float between -1.0 and 1.0 representing NLP sentiment.
    * `competitor_price`: Float representing competitor ticket price.
    * `web_demand`: Float between 10 and 100 representing Google Trends demand.
  * Description: Returns dynamic price recommendations from both the Linear Regression and Q-Learning models.

### Terminal and running stats -
* PS C:\Users\Stavya> cd C:\Java_DSA\DynamicPrice_project
* PS C:\Java_DSA\DynamicPrice_project> C:\msys64\ucrt64\bin\python.exe train_models.py
Starting training pipeline...
Initiating Selenium scraper for BookMyShow...
Error during scraping (will use fallback event list): Message:
Using fallback/base events list.
Generated 1200 training samples.
Linear Regression R2 Score: 0.9955
Linear Regression RMSE: 15.3989
Model successfully saved to model.joblib
Q-Learning Policy generated.
Data and Q-table successfully saved.

* PS C:\Java_DSA\DynamicPrice_project> C:\msys64\ucrt64\bin\python.exe application.py
Successfully loaded Linear Regression model.
Successfully loaded Q-learning Table.
 * Serving Flask app 'application'
 * Debug mode: on
