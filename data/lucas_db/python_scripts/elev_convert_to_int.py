import pandas as pd

# Load the CSV file with the correct delimiter
file_path = '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_retrieved.csv'
data = pd.read_csv(file_path, delimiter=';')

# Print the column names to confirm they are correctly separated
print("Column names:", data.columns)

# Now apply the integer conversion to the 'elevation' column
data['elevation'] = data['elevation'].apply(lambda x: int(x) if pd.notnull(x) else x)

# Save the updated DataFrame to a new CSV file
output_path = '/Users/maxsonntag/Documents/GitHub/SOC_predictor/data/lucas_db/location_elevation_fixed.csv'
data.to_csv(output_path, index=False)

print(f"Updated CSV saved to {output_path}")
