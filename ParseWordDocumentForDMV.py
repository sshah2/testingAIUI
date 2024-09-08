from docx import Document
import json
import re

# Load the Word document
file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\SCR0001.docx'
document = Document(file_path)

# Extract tables from the document
tables = document.tables

# Find the table with the fields (assuming it's the first table for simplicity)
fields_table_data = None
for table in tables:
    # Check if the table has the expected headers
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    if headers[:5] == ['Field #', 'Field Label', 'Field Type', 'Description', 'Field Length']:
        fields_table_data = table
        break

# Define valid field types and mapping rules
valid_field_types = {
    "Label with Radio buttons": "Radio Button",
    "Label with Radio Buttons": "Radio Button",
    "Textbox": "Textbox",
    "Type ahead textbox": "Type Ahead Textbox",
    "Picklist": "Picklist",
    "Date": "Date",
    "Label": "Label",
    "Hyperlink": "Hyperlink"
}


# Function to clean text
def clean_text(text):
    # Remove special characters and extra whitespace
    return re.sub(r'\s+', ' ', text).strip()


# Prepare the data for JSON conversion
json_data = []
if fields_table_data:
    for row in fields_table_data.rows[1:]:  # Skip header row
        cells = row.cells

        # Map field type to valid types or assign "Unknown"
        field_type = cells[2].text.strip()
        mapped_field_type = valid_field_types.get(field_type, "Unknown")

        # Extract pick list values and assign to appropriate rules
        picklist_values = clean_text(cells[6].text.strip())
        required_rule = ""
        display_rule = ""
        validation_rule = ""

        # Logic to identify and extract rules from picklist values
        if "Required Rule:" in picklist_values:
            required_rule = picklist_values.split("Required Rule:")[1].strip()
            picklist_values = picklist_values.split("Required Rule:")[0].strip()
        if "Display Rule:" in picklist_values:
            display_rule = picklist_values.split("Display Rule:")[1].strip()
            picklist_values = picklist_values.split("Display Rule:")[0].strip()
        if "Validation Rule:" in picklist_values:
            validation_rule = picklist_values.split("Validation Rule:")[1].strip()
            picklist_values = picklist_values.split("Validation Rule:")[0].strip()

        field_dict = {
            "#": clean_text(cells[0].text.strip()),
            "Type": mapped_field_type,
            "Field Label": clean_text(cells[1].text.strip()),
            "Field API Name": "",
            "Field Description": clean_text(cells[3].text.strip()),
            "Field Type": mapped_field_type,
            "Field Length": clean_text(cells[4].text.strip()),
            "Required (Y/N)": clean_text(cells[5].text.strip()),
            "Picklist Values / Radio Button Values": picklist_values,
            "Error Message Trigger": "",
            "Error Message": "",
            "Business Rule Trigger": "",
            "Business Logic": "",
            "Business Rule Name": "",
            "Business Rule Description": "",
            "Required Rule": required_rule,
            "Display Rule": display_rule,
            "Validation Rule": validation_rule,
            "Validation Name": "",
            "Readonly": "",
            "Field": "",
            "Object": "",
            "Row": "",
            "Column": ""
        }
        json_data.append(field_dict)

# Convert the list to a JSON structure
json_output = {"data": json_data}

# Save the JSON to a file
output_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\output_from_docx.json'
with open(output_file_path, 'w') as json_file:
    json.dump(json_output, json_file, indent=4)

print(f"JSON output has been saved to {output_file_path}")
