import pandas as pd
import json

# Load JSON data from the file
with open('C:\\Users\\sashah\\Downloads\\section_1_vehicle_information_revised.json', 'r') as file:
    data = json.load(file)

# Parse JSON data
rows = []
for section in data:
    section_name = section['section_name']
    for field in section['fields']:
        label = field['field_label']
        field_type = field['field_type']
        required = field['required']
        picklist_values = field['picklist_values']
        conditional_display = field.get('conditional_display', '')
        validation = field.get('validation', '')

        # Create a dictionary for each row of data
        row = {
            'Section Name': section_name,
            'Label': label,
            'Field Type': field_type,
            'Required': required,
            'Picklist Values': picklist_values,
            'Conditional Display': conditional_display,
            'Validation': validation
        }
        rows.append(row)

# Convert list of dictionaries to DataFrame
df = pd.DataFrame(rows)

# Write DataFrame to Excel file
df.to_excel('C:\\Users\\sashah\\Downloads\\section_1_vehicle_information_revised.json.xlsx', index=False)

print("Excel file created successfully!")
