import re

# Define the input and output file paths
input_file_path = 'SQLS04.csv'
output_file_path = 'output.csv'

# Define the regular expression pattern to match the date format
date_pattern = re.compile(r',\"(\d{1,2})/(\d{1,2})/(\d{4})\",')

# Open the input CSV file for reading
with open(input_file_path, 'r') as input_file:
    # Open the output CSV file for writing
    with open(output_file_path, 'w') as output_file:
        # Read each line from the input file
        for line in input_file:
            # Replace the date format using the regular expression
            modified_line = date_pattern.sub(r',"\3-\1-\2",', line)
            # Write the modified line to the output file
            output_file.write(modified_line)

print("Date format conversion completed.")