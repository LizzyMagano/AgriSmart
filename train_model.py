import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Loading data from CSV...")

# 1. Load the CSV
df = pd.read_csv('climate_data_rows.csv')

# 2. Prepare Features (X) and Target (y)
X = df[['rainfall_mm', 'avg_temperature_c']]

# Create categories (0 = Low, 1 = Moderate, 2 = High)
def get_category(row):
    rain = row['rainfall_mm']
    if rain < 400: return 0
    elif rain < 800: return 1
    else: return 2

y = df.apply(get_category, axis=1)

# 3. Train the Random Forest
print("Training the Random Forest model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 4. Evaluate
predictions = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"🏆 Model trained! Accuracy: {accuracy * 100:.2f}%")

# 5. Save the model
joblib.dump(rf_model, 'agrismart_rf_model.pkl')
print("✅ SUCCESS: 'agrismart_rf_model.pkl' created!")