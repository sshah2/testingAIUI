import openai
from docx import Document
import json
import re
import csv
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import process

# Set up OpenAI API key from environment variable for security
openai.api_key = "***REMOVED***"

# Specify the path to the CSV file
csv_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\AssessmentTask.csv'

# Helper function to clean text
def clean_text(text):
    # Remove special characters and extra whitespace
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

# Load the data dictionary from the CSV file
def load_data_dict(csv_file_path):
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
    return data_dict

data_dict = load_data_dict(csv_file_path)

# Create a TF-IDF vectorizer and fit it on the field labels
vectorizer = TfidfVectorizer().fit([item['Field Label'] for item in data_dict])
data_dict_vectors = vectorizer.transform([item['Field Label'] for item in data_dict])

# Load the Word document
file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\SCR0001-1.docx'
document = Document(file_path)

# Extract tables from the document
tables = document.tables

# Extract the table with fields data
fields_table_data, validation_table_data, business_table_data = None, None, None

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
    "Textbox": "Textbox",
    "Type ahead textbox": "Type Ahead Textbox",
    "Picklist": "Picklist",
    "Date": "Date",
    "Label": "Label",
    "Hyperlink": "Hyperlink"
}

# Function to use OpenAI API to refine field label matching
def refine_match(field_label, candidate_labels, candidate_field_names):
    prompt = f"Match the following field label to the closest field name from the candidates:\n\nField Label: {field_label}\n\nCandidates:\n"
    for label, field_name in zip(candidate_labels, candidate_field_names):
        prompt += f"Field Label: {label}, Field Name: {field_name}\n"
    prompt += "\nClosest match:"

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with matching field labels to field names."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=50
    )

    match = response['choices'][0]['message']['content'].strip()
    # Extracting the field name from the response
    for label, field_name in zip(candidate_labels, candidate_field_names):
        if field_name in match:
            return field_name
    return "Unknown__C"

# Function to match field labels using similarity and fuzzy matching
def match_field_label(field_label, data_dict, data_dict_vectors, top_n=10):
    field_label_vector = vectorizer.transform([field_label])
    similarities = cosine_similarity(field_label_vector, data_dict_vectors).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]

    candidate_labels = [data_dict[i]['Field Label'] for i in top_indices]
    candidate_field_names = [data_dict[i]['Field Name'] for i in top_indices]

    # Additional fuzzy matching
    fuzzy_match = process.extractOne(field_label, candidate_labels)
    if fuzzy_match:
        match_label = fuzzy_match[0]
        match_index = candidate_labels.index(match_label)
        candidate_labels.insert(0, candidate_labels.pop(match_index))
        candidate_field_names.insert(0, candidate_field_names.pop(match_index))

    # Send top candidates to OpenAI for refinement
    return refine_match(field_label, candidate_labels, candidate_field_names)

# Prepare the data for JSON conversion
def process_fields_table(fields_table_data):
    json_data = []
    if fields_table_data:
        for i, row in enumerate(fields_table_data.rows[1:]):  # Skip header row
            try:
                cells = row.cells
                field_type = cells[2].text.strip()
                mapped_field_type = valid_field_types.get(field_type, "Unknown")

                picklist_values = clean_text(cells[6].text.strip())
                required_rule, display_rule, validation_rule = "", "", ""

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
                field_name = match_field_label(field_label, data_dict, data_dict_vectors)
                field_info = next((item for item in data_dict if item["Field Name"] == field_name),
                                  {"Field Name": "Unknown__C", "Data Type": "Unknown"})

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
                    "Business Rule Expression": "",
                    "Required Rule": required_rule,
                    "Display Rule": display_rule,
                    "Validation English Rule": validation_rule,
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
                print(f"Error processing row {i + 1}: {e}")
                continue
    return json_data

json_data = process_fields_table(fields_table_data)

# Convert the list to a JSON structure
json_output = {"data": json_data}

# Save the JSON to a file
output_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\output_from_docx.json'
with open(output_file_path, 'w') as json_file:
    json.dump(json_output, json_file, indent=4)

print(f"JSON output has been saved to {output_file_path}")

# Rule Identification and Conversion Process
# Function to identify the corresponding label for a validation rule
def identify_corresponding_label(rule_description, field_string):
    prompt = (
        f"Given the following rule description, break the rule into multiple tokens (variables, labels and constants), "
        f"and from the tokens, identify which label corresponds to one of the labels in the provided field string.\n\n"
        f"Rule Description: {rule_description}\n\n"
        f"Field String: {field_string}\n\n"
        f"Format the result as: Corresponding Label: <label>"
    )

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that helps with identifying corresponding labels for validation rules."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200
    )

    result = response['choices'][0]['message']['content'].strip()
    #print(f"Identification Result: {result}")  # Debugging: Print identification results
    match = re.search(r'Corresponding Label:\s*(.*)', result)
    if match:
        return match.group(1).strip()
    return None

# Create a string of all captured labels
field_labels = [field['Field Label'] for field in json_data]
field_string = ', '.join(field_labels)

# Process validation rules
def process_validation_rules(validation_table_data, json_data, field_string):
    if validation_table_data:
        for rule_row in validation_table_data.rows[1:]:
            rule_cells = rule_row.cells
            rule_description = clean_text(rule_cells[2].text.strip())
            error_message = clean_text(rule_cells[3].text.strip())

            corresponding_label = identify_corresponding_label(rule_description, field_string)
            print("CL")
            print(corresponding_label)
            if corresponding_label:
                for field in json_data:
                    if field["Field Label"] == corresponding_label:
                        field_api_name = field["Field API Name"]
                        field["Error Message"] = error_message
                        prompt = (
                            f"Given the following Rule Description, follow the following steps: "
                            f"1) Figure out all the labels that are present in the rule and identify which label "
                            f"corresponds to <{corresponding_label}> "
                            f"2) Now convert the Rule Description into a pseudo-code based validation condition – "
                            f"and in that validation condition, you will: "
                            f" a.Replace the label that corresponded to <{corresponding_label}> with {field_api_name} "
                            f" b.For all variables that are remaining in the rule, replace them with the format "
                            f"NOT_FOUND_VARIABLE_name "
                            f"c.Now, create the rest of the pseudo-code based validation condition using the "
                            f"appropriate constants and operators "
                            f"d. Do not include any user actions or messaging instructions in the validation condition"
                            f"3) The resulting final pseudo-code based validation condition should start with || and "
                            f"end the condition also with || so that I can extract it later \n\n"
                            f"Rule Description: {rule_description}\n\n"
                            )

                        response = openai.ChatCompletion.create(
                            model="gpt-4",
                            messages=[
                                {"role": "system",
                                 "content": "You are an assistant that helps with identifying the appropriate pseudo code for validation rules."},
                                {"role": "user", "content": prompt}
                            ],
                            max_tokens=200
                        )

                        #print(f"Prompt: {prompt}")
                        #print(f"Response: {response}")

                        result = response['choices'][0]['message']['content'].strip()
                        print(f"Result: {result}")
                        updated_rule_description = rule_description  # Assigning the original rule description
                        # Updating with the result if it is not empty
                        if result:
                            pattern = re.escape("||") + r"(.*?)" + re.escape("||")
                            match = re.search(pattern, result, re.DOTALL)
                            if match:
                                updated_rule_description = match.group(1).strip()
                        # Ensuring the field's validation rule is updated
                        field["Validation Rule"] = updated_rule_description
                        break

process_validation_rules(validation_table_data, json_data, field_string)

# Save the updated JSON to a file
output_file_path = r'C:\Users\sashah\Desktop\Projects\CA DMV\updated_output_from_docx.json'
with open(output_file_path, 'w') as json_file:
    json.dump(json_data, json_file, indent=4)

print(f"Updated JSON output has been saved to {output_file_path}")
