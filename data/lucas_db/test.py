import pandas as pd

# Load the CSV file
file_path = '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_retrieved.csv'
data = pd.read_csv(file_path)

# Print the column names
print("Column names:", data.columns)