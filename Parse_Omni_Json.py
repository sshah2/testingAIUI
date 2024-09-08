import json
import pandas as pd


def extract_omniscript_and_dataraptor_details(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    # Initialize a dictionary to store extracted details
    extracted_details = {
        "Steps": [],
        "DataRaptors": []
    }

    # Print the structure of the JSON data for debugging
    print("JSON Data Structure:")
    print(json.dumps(json_data, indent=2)[:2000])  # Print the first 2000 characters of the JSON data for a preview

    # Function to recursively search for DataRaptor elements in the JSON structure
    def find_dataraptors(node):
        if isinstance(node, dict):
            if node.get('VlocityRecordSObjectType') == 'DRBundle':
                dataraptor_details = {
                    "DataRaptorName": node.get('Name'),
                    "FetchObjects": [],
                    "UpdateObjects": []
                }
                for mapping in node.get('DRBundleElement', []):
                    if 'DRBundleElementType' in mapping and mapping['DRBundleElementType'] == 'Extract':
                        for obj_mapping in mapping.get('ObjectMappings', []):
                            dataraptor_details["FetchObjects"].append(obj_mapping.get('ObjectName'))
                    if 'DRBundleElementType' in mapping and mapping['DRBundleElementType'] == 'Load':
                        for obj_mapping in mapping.get('ObjectMappings', []):
                            dataraptor_details["UpdateObjects"].append(obj_mapping.get('ObjectName'))
                extracted_details["DataRaptors"].append(dataraptor_details)
            else:
                for key, value in node.items():
                    find_dataraptors(value)
        elif isinstance(node, list):
            for item in node:
                find_dataraptors(item)

    # Iterate through elements to find steps and DataRaptors
    for data_pack in json_data.get('dataPacks', []):
        omni_process = data_pack.get('VlocityDataPackData', {}).get('OmniProcess', [])
        for element in omni_process:
            print("Element details:", json.dumps(element, indent=2)[:2000])  # Detailed debug print
            if element.get('VlocityRecordSObjectType') == 'OmniProcess':
                step_details = {
                    "StepName": element.get('Name'),
                    "SequenceNumber": element.get('SequenceNumber', 0),
                    "Blocks": [],
                    "Validations": [],
                    "Elements": []
                }

                # Iterate through nested elements within the step
                for sub_element in element.get('OmniProcessElement', []):
                    if sub_element.get('Type') == 'Block':
                        block_details = {
                            "BlockName": sub_element.get('Name'),
                            "Elements": []
                        }
                        # Add elements within the block
                        for block_sub_element in sub_element.get('OmniProcessElement', []):
                            property_set_config = block_sub_element.get('PropertySetConfig', '{}')
                            if isinstance(property_set_config, str):
                                property_set_config = json.loads(property_set_config)
                            block_details["Elements"].append({
                                "ElementName": block_sub_element.get('Name'),
                                "Label": property_set_config.get('label'),
                                "Type": block_sub_element.get('Type')
                            })
                        step_details["Blocks"].append(block_details)
                    elif sub_element.get('Type') == 'Validation':
                        property_set_config = sub_element.get('PropertySetConfig', '{}')
                        if isinstance(property_set_config, str):
                            property_set_config = json.loads(property_set_config)
                        step_details["Validations"].append({
                            "ValidationName": sub_element.get('Name'),
                            "Label": property_set_config.get('label'),
                            "Type": sub_element.get('Type'),
                            "Messages": property_set_config.get('messages', []),
                            "ValidationExpression": property_set_config.get('validateExpression')
                        })
                    else:
                        property_set_config = sub_element.get('PropertySetConfig', '{}')
                        if isinstance(property_set_config, str):
                            property_set_config = json.loads(property_set_config)
                        step_details["Elements"].append({
                            "ElementName": sub_element.get('Name'),
                            "Label": property_set_config.get('label'),
                            "Type": sub_element.get('Type')
                        })

                # Append the step details to the extracted details dictionary
                extracted_details["Steps"].append(step_details)

        # Search for DataRaptors in the entire structure
        find_dataraptors(data_pack)

    # Sort steps by sequence number
    extracted_details["Steps"] = sorted(extracted_details["Steps"], key=lambda x: x['SequenceNumber'])

    return extracted_details


# Path to the JSON file
file_path = "c:\\users\\sashah\\downloads\\CARES_FamilyTransfer.json"

# Extract OmniScript and DataRaptor details
details = extract_omniscript_and_dataraptor_details(file_path)

# Convert to DataFrame for better display
steps_df = pd.json_normalize(details, 'Steps')
dataraptors_df = pd.json_normalize(details, 'DataRaptors')

# Print the extracted details
print(json.dumps(details, indent=2))

# Optionally, save the extracted details to a JSON file
output_file = "c:\\users\\sashah\\downloads\\extracted_details.json"
with open(output_file, 'w') as file:
    json.dump(details, file, indent=2)

print(f"Extracted details saved to {output_file}")
