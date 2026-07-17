import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

print("Starting training pipeline...")

# Fallback/base events
indian_events = pd.DataFrame([
    {"title": "Maargan", "genre": "Crime/Supernatural/Thriller"},
    {"title": "Jurassic World: Rebirth", "genre": "Action/Sci-Fi/Thriller"},
    {"title": "F1: The Movie", "genre": "Action/Drama/Sports"},
    {"title": "DNA", "genre": "Crime/Thriller"},
    {"title": "Kuberaa", "genre": "Action/Drama/Social/Thriller"}
])

genre_sentiment_map = {
    'action': 0.1,
    'thriller': 0.2,
    'comedy': 0.3,
    'drama': 0.15,
    'sci-fi': 0.1,
    'crime': -0.1,
    'social': 0.05
}

def genre_based_sentiment(genre):
    sentiment = 0
    genre = genre.lower()
    for key in genre_sentiment_map:
        if key in genre:
            sentiment += genre_sentiment_map[key]
    return sentiment

np.random.seed(42)
num_records = 1200
synthetic_events = []
genres_pool = ["Action/Sci-Fi/Thriller", "Action/Drama/Sports", "Crime/Thriller", "Action/Drama/Social/Thriller", "Comedy/Drama", "Horror/Thriller", "Drama/Romance"]

for i in range(num_records):
    base_event = indian_events.iloc[i % len(indian_events)]
    genre = np.random.choice(genres_pool)
    title = f"{base_event['title']} Part {i // len(indian_events) + 1}"
    
    # Calculate simulated sentiment (-1.0 to 1.0)
    sentiment = genre_based_sentiment(genre) + np.random.normal(0, 0.1)
    sentiment = max(-1.0, min(1.0, sentiment))
    
    # Simulated web demand / Google Trends score (0 to 100)
    web_demand = np.random.uniform(10, 100)
    
    # Competitor price (300 to 1200 INR)
    competitor_price = np.random.uniform(300, 1200)
    
    # Pricing formula incorporating genre sentiment, competitor price, and web demand
    recommended_price = (
        200 + 
        150 * sentiment + 
        0.8 * competitor_price + 
        2.5 * web_demand + 
        np.random.normal(0, 15)
    )
    recommended_price = max(250, min(2500, recommended_price))
    
    synthetic_events.append({
        "title": title,
        "genre": genre,
        "sentiment": sentiment,
        "web_demand": web_demand,
        "competitor_price": competitor_price,
        "price": recommended_price
    })

data = pd.DataFrame(synthetic_events)
print(f"Generated {len(data)} training samples.")

# 1. Train Linear Regression Model
X = data[['sentiment', 'competitor_price', 'web_demand']]
y = data['price']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = mean_squared_error(y_test, y_pred) ** 0.5

print(f"Linear Regression R2 Score: {r2:.4f}")
print(f"Linear Regression RMSE: {rmse:.4f}")

# Save the linear regression model
joblib.dump(model, "model.joblib")
print("Model successfully saved to model.joblib")

# 2. Run Q-learning Policy Simulation
price_levels = [500, 800, 1000, 1200, 1500]
q_table = pd.DataFrame(0.0, index=['low', 'medium', 'high'], columns=price_levels)

def get_sentiment_state(score):
    if score < 0.1:
        return 'low'
    elif score < 0.2:
        return 'medium'
    else:
        return 'high'

data['sentiment_state'] = data['sentiment'].apply(get_sentiment_state)

alpha = 0.1
gamma = 0.9

for i, row in data.iterrows():
    sentiment = row['sentiment_state']
    for action in price_levels:
        if sentiment == 'high':
            multiplier = 1.2 if action >= 1000 else 1.0
        elif sentiment == 'medium':
            multiplier = 1.0 if action <= 1000 else 0.9
        else:
            multiplier = 0.8 if action <= 800 else 0.6

        reward = (1 + row['sentiment']) * multiplier
        old_q = q_table.loc[sentiment, action]
        q_table.loc[sentiment, action] = (1 - alpha) * old_q + alpha * (reward + gamma * q_table.loc[sentiment].max())

q_table = q_table / q_table.max().max()
print("Q-Learning Policy generated.")

# Save Q-table
q_table.to_csv("q_table.csv")
data.to_csv("event_data.csv", index=False)
print("Data and Q-table successfully saved.")
