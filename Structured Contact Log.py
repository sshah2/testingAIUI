import json
import openai

# Replace with your actual OpenAI API key
openai.api_key = "***REMOVED***"


def analyze_contact_notes_with_gpt4(text, known_focus_children, known_participants):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that extracts structured data from freeform text and returns it in a valid JSON format. Use the information provided to fill in the details as completely as possible. If specific details are not mentioned, infer or leave fields empty only if no reasonable inference can be made."},
                {"role": "user",
                 "content": f"Extract the following fields from the contact notes and return the results as JSON. Include only the focus children and participants if they are mentioned in the notes:\n\n1. Contact Status\n2. Contact Purpose\n3. Contact Start Date\n4. Contact Start Time\n5. Contact End Date\n6. Contact End Time\n7. Staff Person\n8. Other Staff Present\n9. Method\n10. Location\n11. Documentation Status\n12. Folio Information\n13. Focus Child (Folio Name, Validated Person Name, Role)\n14. Other Focus Children\n15. Participants (First Name, Last Name, Role)\n16. Interaction Details (Met Alone With Child, Dressed Appropriately, Observed Injuries)\n17. Indian Ancestry\n18. Case Plan Progress (What Is Working Well, What Are We Worried About, Is Child Participating In Services, Is Youth Participating In ILP, Has TILP Been Updated)\n19. Child And Family Team (Life-Long Connections, Formal Supports)\n20. Family's Capacity to Provide for Needs (Needs And Services, Case Planning, Social Worker Visits)\n21. Safety In Home (Persons In Home, Living Environment, Safety And Supervision)\n22. Educational Needs (Attending School, On Track To Graduate, Has Graduated High School, Interested In Post-Secondary Education, Next IEP Due, Biennial IEP Due, 504 Plan Due, Education Rights Holder)\n23. Physical And Mental Health Needs (Physical Health, Mental/Behavioral Health, Substance Use, Psychotropic Medication, CANS Update Required)\n\nContact Notes: {text}"}
            ],
            max_tokens=1500,
        )

        response_text = response['choices'][0]['message']['content']
        response_text = response_text.strip().strip('```')

        # Corrected method name from 'endsWith' to 'endswith'
        if not response_text.startswith("{") or not response_text.endswith("}"):
            raise ValueError("Response is not in valid JSON format.")

        return json.loads(response_text)

    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {str(json_err)}")
        return {}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}


def validate_json_structure(data, mandatory_fields):
    missing_mandatory = []
    empty_fields = []

    for path in mandatory_fields:
        node = data
        for key in path:
            if isinstance(node, list):
                if len(node) == 0:  # Check if the list is empty
                    missing_mandatory.append(".".join(path))
                    break
                node = node[0]  # Proceed with the first item in the list
            if key in node:
                node = node[key]
            else:
                missing_mandatory.append(".".join(path))
                break
        if node == "" or node is None or (isinstance(node, list) and len(node) == 0):
            missing_mandatory.append(".".join(path))  # Treat empty mandatory fields as missing
            empty_fields.append(".".join(path))

    return missing_mandatory, empty_fields


def process_contact_notes(text, known_focus_children, known_participants):
    analyzed_data = analyze_contact_notes_with_gpt4(text, known_focus_children, known_participants)

    if not analyzed_data:
        print("No data was processed due to an earlier error.")
        return

    # Define your mandatory fields here, adjusted to the flat structure
    mandatory_fields = [
        ("Contact Purpose",),
        ("Location",),
        ("Participants", "Role"),
        ("Indian Ancestry",),
        ("Case Plan Progress", "What Are We Worried About"),
        ("Safety In Home", "Living Environment"),
        ("Educational Needs", "Attending School"),
        ("Educational Needs", "On Track To Graduate"),
        ("Physical And Mental Health Needs", "Mental/Behavioral Health"),
    ]

    missing_mandatory, empty_fields = validate_json_structure(analyzed_data, mandatory_fields)

    print("Populated JSON Structure:")
    print(json.dumps(analyzed_data, indent=4))

    # Update to correctly handle missing mandatory fields
    if missing_mandatory:
        print("\nMissing Mandatory Fields:")
        for field in missing_mandatory:
            print(f"- {field}")
    else:
        print("\nAll mandatory fields are populated.")

    if empty_fields:
        print("\nFields with No Values Provided:")
        for field in empty_fields:
            print(f"- {field}")
    else:
        print("\nNo empty fields.")


# Example known focus children and participants
known_focus_children = [
    {"name": "John Doe", "Folio Name": "12345", "Validated Person Name": "John Doe", "Role": "Focus Child"},
    {"name": "Jane Doe", "Folio Name": "67890", "Validated Person Name": "Jane Doe", "Role": "Focus Child"}
]

known_participants = [
    {"name": "Mr. Smith", "First Name": "John", "Last Name": "Smith", "Role": "Teacher"},
    {"name": "Mrs. Johnson", "First Name": "Mary", "Last Name": "Johnson", "Role": "Social Worker"}
]

contact_notes = """
The social worker, Mrs. Johnson initiated the contact for a regular follow-up.
John Doe is doing well in school but there are concerns about his home environment.
Mrs. Johnson, noted that John was dressed appropriately and observed no injuries.
However, John mentioned feeling isolated from peers.
"""

process_contact_notes(contact_notes, known_focus_children, known_participants)
