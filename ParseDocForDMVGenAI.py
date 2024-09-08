import openai
from docx import Document
import json
import re
import csv
import time

# OpenAI API key configuration
openai.api_key = "***REMOVED***"

# Specify the path to the CSV file
csv_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\AssessmentTask.csv'

# Helper function to clean text
def clean_text(text):
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# Load the data dictionary from the CSV file
data_dict = []
try:
    with open(csv_file_path, mode='r', encoding='latin1') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            field_label = clean_text(row["FIELD LABEL"])
            field_name = row["FIELD NAME"]
            data_type = row["DATA TYPE"]
            data_dict.append({"Field Label": field_label, "Field Name": field_name, "Data Type": data_type})
except FileNotFoundError:
    print(f"File not found: {csv_file_path}")
    exit(1)

# Load the Word document
file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\SCR0001-1.docx'
document = Document(file_path)

# Extract tables from the document
tables = document.tables

# Extract the table with fields data
fields_table_data = None
validation_table_data = None
business_table_data = None

for table in tables:
    headers = [cell.text.strip() for cell in table.rows[0].cells]
    if headers[:5] == ['Field #', 'Field Label', 'Field Type', 'Description', 'Field Length']:
        fields_table_data = table
    elif headers[:2] == ['V. Rule#', 'V. Rule Name']:
        validation_table_data = table
    elif headers[:2] == ['BR#', 'BR Name']:
        business_table_data = table

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

# Function to use OpenAI API to match field labels with retry mechanism
def match_field_label(field_label, data_dict, max_retries=5):
    prompt = f"Match the following field label to the closest field name from the data dictionary:\n\nField Label: {field_label}\n\nData Dictionary:\n"
    for item in data_dict[:20]:  # Limit to 20 entries to reduce token usage
        prompt += f"Field Label: {item['Field Label']}, Field Name: {item['Field Name']}, Data Type: {item['Data Type']}\n"
    prompt += "\nClosest match:"

    retries = 0
    while retries < max_retries:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an assistant that helps with matching field labels to field names."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            match = response['choices'][0]['message']['content'].strip()
            for item in data_dict:
                if match in item['Field Label']:
                    return item
            return {"Field Name": "Unknown__C", "Data Type": "Unknown"}
        except openai.error.RateLimitError as e:
            print(f"Rate limit reached: {e}. Retrying in {2 ** retries} seconds...")
            time.sleep(2 ** retries)
            retries += 1
    return {"Field Name": "Unknown__C", "Data Type": "Unknown"}

# Prepare the data for JSON conversion
json_data = []
if fields_table_data:
    for i, row in enumerate(fields_table_data.rows[1:]):  # Skip header row
        try:
            cells = row.cells
            field_type = cells[2].text.strip()
            mapped_field_type = valid_field_types.get(field_type, "Unknown")

            picklist_values = clean_text(cells[6].text.strip())
            required_rule = ""
            display_rule = ""
            validation_rule = ""

            if "Required Rule:" in picklist_values:
                required_rule = picklist_values.split("Required Rule:")[1].strip()
                picklist_values = picklist_values.split("Required Rule:")[0].strip()
            if "Display Rule:" in picklist_values:
                display_rule = picklist_values.split("Display Rule:")[1].strip()
                picklist_values = picklist_values.split("Display Rule:")[0].strip()
            if "Validation Rule:" in picklist_values:
                validation_rule = picklist_values.split("Validation Rule:")[1].strip()
                picklist_values = picklist_values.split("Validation Rule:")[0].strip()

            field_label = clean_text(cells[1].text.strip())
            field_info = match_field_label(field_label, data_dict)

            field_dict = {
                "#": clean_text(cells[0].text.strip()),
                "Type": mapped_field_type,
                "Field Label": field_label,
                "Field API Name": field_info["Field Name"],
                "Field Description": clean_text(cells[3].text.strip()),
                "Field Type": field_info["Data Type"],
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
                "Field": field_info["Field Name"],
                "Object": "AssessmentTask",
                "Row": "",
                "Column": ""
            }
            json_data.append(field_dict)
        except Exception as e:
            print(f"Error processing row {i+1}: {e}")
            continue

# Function to use OpenAI API to correlate rules
def correlate_rules(fields, rules, rule_type):
    for rule_row in rules:
        rule_cells = rule_row.cells
        rule_number = clean_text(rule_cells[0].text.strip())
        rule_name = clean_text(rule_cells[1].text.strip())
        rule_description = clean_text(rule_cells[2].text.strip())
        error_message = clean_text(rule_cells[3].text.strip()) if len(rule_cells) > 3 else ""

        for field in fields:
            prompt = f"Does the following {rule_type} apply to the field '{field['Field Label']}'?\n\n{rule_type} Name: {rule_name}\n{rule_type} Description: {rule_description}\nError Message: {error_message if rule_type == 'Validation Rule' else ''}"
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an assistant that helps with correlating rules to fields in a document."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50
            )
            if "Yes" in response['choices'][0]['message']['content']:
                if rule_type == "Validation Rule":
                    field["Validation Rule"] = f"{rule_name}: {rule_description}"
                    field["Error Message"] = error_message
                    # Replace label with API name in validation rule
                    field["Validation Rule"] = field["Validation Rule"].replace(field["Field Label"], field["Field API Name"])
                else:
                    field["Business Rule Name"] = rule_name
                    field["Business Rule Description"] = rule_description

# Add validation rules from Section 1.7
if validation_table_data:
    correlate_rules(json_data, validation_table_data.rows[1:], "Validation Rule")

# Add business rules from Section 1.9
if business_table_data:
    correlate_rules(json_data, business_table_data.rows[1:], "Business Rule")

# Convert the list to a JSON structure
json_output = {"data": json_data}

# Save the JSON to a file
output_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\output_from_docx.json'
with open(output_file_path, 'w') as json_file:
    json.dump(json_output, json_file, indent=4)

print(f"JSON output has been saved to {output_file_path}")
