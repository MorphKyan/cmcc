import csv
import json
import os
import shutil

input_file = r'data/devices.csv'
temp_file = r'data/devices_temp.csv'

# Ensure we use the correct encoding
encoding = 'utf-8'

try:
    with open(input_file, 'r', encoding=encoding, newline='') as infile, \
         open(temp_file, 'w', encoding=encoding, newline='') as outfile:
        
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        
        # Use QUOTE_ALL to mimic the input format which seems to quote all fields
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        
        for row in reader:
            name = row.get('name', '')
            
            # Function to process a specific column
            def process_col(col_value, match_name):
                if not col_value:
                    return col_value
                
                # Try to parse as JSON list
                try:
                    data = json.loads(col_value)
                    if isinstance(data, list):
                        # Filter out items that match 'name'
                        new_data = [x for x in data if x != match_name]
                        
                        # If list is empty, return empty string
                        if not new_data:
                            return ""
                        # Otherwise return JSON string
                        return json.dumps(new_data, ensure_ascii=False)
                    elif isinstance(data, str):
                         if data == match_name:
                             return ""
                except json.JSONDecodeError:
                    # If not JSON, check for exact string match
                    pass
                
                # Check for exact match if not list or JSON parse failed
                if col_value == match_name:
                    return ""
                
                return col_value

            # Process 'command' and 'view' columns
            row['command'] = process_col(row.get('command', ''), name)
            row['view'] = process_col(row.get('view', ''), name)
            
            writer.writerow(row)
            
    # Replace original file with temp file
    shutil.move(temp_file, input_file)
    print("Successfully processed devices.csv")

except Exception as e:
    print(f"Error processing file: {e}")
    if os.path.exists(temp_file):
        os.remove(temp_file)
