import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('TEMPEXPORT2.csv')

# Sort the DataFrame by SERIAL and COUNT in descending order
# Sorts the SERIAL column in ascending order and the COUNT column in descending order
# This way, the highest COUNT for each SERIAL will be the first occurrence
df_sorted = df.sort_values(by=['SERIAL', 'COUNT'], ascending=[True, False])

# Drop duplicates based on the SERIAL column, keeping the first occurrence (which has the highest COUNT due to sorting)
# So we'll only keep the first row with the highest COUNT for each SERIAL
df_deduplicated = df_sorted.drop_duplicates(subset='SERIAL', keep='first')

# Write the resulting DataFrame back to a CSV file
df_deduplicated.to_csv('NONDUPS_file.csv', index=False)