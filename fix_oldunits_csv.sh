#!/bin/zsh

# Check if a file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <csv_file>"
    exit 1
fi

csv_file="$1"
concatenated_lines=""

while IFS= read -r line; do
    # Check if the line starts with a numeric character
    if [[ $line =~ ^[0-9] ]]; then
        # Extract the first word of the line
        first_word=$(echo "$line" | awk '{print $1}')
        
        # Check if the first word contains two "/"
        if [[ $first_word =~ .*/.*/.* ]]; then
            # Print the concatenated lines and reset the variable
            echo "$concatenated_lines"
            concatenated_lines=""
        fi
    fi
    
    # Append the line to the concatenated variable
    concatenated_lines+="$line "
done < "$csv_file"

# Print any remaining concatenated lines
if [ -n "$concatenated_lines" ]; then
    echo "$concatenated_lines"
fi