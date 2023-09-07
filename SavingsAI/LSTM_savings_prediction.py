import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.model_selection import train_test_split
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import Adam
from keras.regularizers import l2
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import pytz

# load csv data for testing
data = pd.read_csv('Sample data.csv')

# Convert "postDate" column to datetime format
data['postDate'] = pd.to_datetime(data['postDate'], utc=True)

# Sort the DataFrame by "postDate"
data = data.sort_values(by='postDate')

# Function to extract and normalize time components
def preprocess_timestamp(timestamp):
    year = timestamp.year
    month = timestamp.month
    day = timestamp.day
    hour = timestamp.hour
    minute = timestamp.minute

    # Normalize time components
    normalized_year = (year - min_year) / (max_year - min_year)
    normalized_month = (month - 1) / 11  # Month range: 1-12
    normalized_day = (day - 1) / 30      # Assuming 30 days in a month
    normalized_hour = hour / 23
    normalized_minute = minute / 59

    return [normalized_year, normalized_month, normalized_day, normalized_hour, normalized_minute]

# Calculate min_year and max_year from your dataset
min_year = data["postDate"].apply(lambda x: x.year).min()
max_year = data["postDate"].apply(lambda x: x.year).max()

# Apply preprocessing function to the "postDate" column and create new columns
data[["year", "month", "day", "hour", "minute"]] = data["postDate"].apply(preprocess_timestamp).apply(pd.Series)

# Print the updated DataFrame
#print(data)

# Feature Engineering
# Currently using 'amount', 'balance' and date fields as features
features = ['amount', 'balance', 'year', 'month', 'day']
X = data[features].values
scaler = StandardScaler()
X = scaler.fit_transform(X)

# Creating Sequences
sequence_length = 10
X_sequences = []
y = []
for i in range(len(X) - sequence_length):
    X_sequences.append(X[i:i+sequence_length])
    y.append(X[i+sequence_length, 1])  # 'balance' is the target variable

X_sequences = np.array(X_sequences)
y = np.array(y)

# Train-Validation-Test Split
X_train, X_temp, y_train, y_temp = train_test_split(X_sequences, y, test_size=0.3, shuffle=False)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, shuffle=False)

# Build LSTM Model
model = Sequential()
model.add(LSTM(50, activation='relu', input_shape=(sequence_length, len(features))))
model.add(Dense(1))
model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

# Training
model.fit(X_train, y_train, epochs=100, batch_size=32, validation_data=(X_val, y_val))

# Evaluation
y_pred = model.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Mean Squared Error: {mse}")

# Mean Absolute Error
mae = np.mean(np.abs(y_test - y_pred))
print(f"Mean Absolute Error: {mae}")

# Root Mean Squared Error
rmse = np.sqrt(np.mean((y_test - y_pred)**2))
print(f"Root Mean Squared Error: {rmse}")

model.save('LSTM_savings_model.h5')