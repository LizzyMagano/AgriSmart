import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Loading data from CSV...")

# 1. Load the CSV (Ensure this matches your exact file name)
df = pd.read_csv('climate_data_rows.csv')

# 2. Prepare Features (X) and Target (y)
X = df[['rainfall_mm', 'avg_temperature_c']]

# 3. Create categories matching YOUR data
def get_category(row):
    rain = row['rainfall_mm']
    if rain < 400: 
        return 0      # Low
    elif rain < 600: 
        return 1      # Moderate
    else: 
        return 2      # High (Chobe & North West)

y = df.apply(get_category, axis=1)

# 4. Train the Random Forest
print("Training the Random Forest model...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 5. Evaluate
predictions = rf_model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Model trained! Accuracy: {accuracy * 100:.2f}%")

# 6. Verify classes
print(f"Classes learned by model: {rf_model.classes_}") # Must print [0 1 2]

# 7. Save the model
joblib.dump(rf_model, 'agrismart_rf_model.pkl')
print("SUCCESS: 'agrismart_rf_model.pkl' recreated!")
