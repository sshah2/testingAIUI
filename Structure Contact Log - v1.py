import openai
import streamlit as st
import json
from datetime import date, datetime
import os

# Load API key from environment variable
openai.api_key = "***REMOVED***"

# Textual month, day and year
todays_date = date.today().strftime("%B %d, %Y")

st.subheader("No-UI UI")

# Create tabs
tab1, tab2 = st.tabs(["Unstructured Contact Note", "Screening Narrative"])

# Main application logic
def main():
    # Initialize session state for messages early in the main function
    #if "messages" not in st.session_state:
    #    st.session_state["messages"] = []
    #if "screening_narrative" not in st.session_state:
    #    st.session_state["screening_narrative"] = ""

    setup_sidebar()

    # Display chat messages in the first tab
    # display_chat_messages()

    # Chat input in the main body for Unstructured Contact Note in the first tab
    #prompt = st.chat_input("Enter unstructured contact notes:")
    #if prompt:
    with tab1:
        #analyzed_data = process_chat_input(prompt)
        notes_prompt = st.text_area("Enter the unstructured contact notes:", height=300)
        if st.button("Process Notes"):
            analyzed_data = process_chat_input(notes_prompt)
            display_app_details_in_tab(analyzed_data)

    # Screening Narrative input in the Screening Narrative tab (second tab)
    with tab2:
        screening_prompt = st.text_area("Enter the screening narrative:", height=400)
        if st.button("Process Screening Narrative"):
            screening_data = process_screening_narrative(screening_prompt)
            display_screening_details_in_tab(screening_data)

def setup_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] { width: 500px !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.title("Welcome to the new world of ***No-UI UI***")
        #text = "This interface allows you to convert unstructured to structured contact notes:"
        #st.markdown(text)

#def display_chat_messages():
#    for msg in st.session_state.messages:
#        if msg["content"]:
#            role_message = msg["role"]
#            if role_message != "system":
#                with tab1:
#                    st.chat_message(msg["role"]).write(msg["content"])

def process_chat_input(prompt):
    with tab1:
        # st.chat_message("user").write(prompt)

        known_focus_children = [
            {"name": "John Doe", "Folio Name": "12345", "Validated Person Name": "John Doe", "Role": "Focus Child"},
            {"name": "Jane Doe", "Folio Name": "67890", "Validated Person Name": "Jane Doe", "Role": "Focus Child"}
        ]

        known_participants = [
            {"name": "Mr. Smith", "First Name": "John", "Last Name": "Smith", "Role": "Teacher"},
            {"name": "Mrs. Johnson", "First Name": "Mary", "Last Name": "Johnson", "Role": "Social Worker"}
        ]

        return process_contact_notes(prompt, known_focus_children, known_participants)

def process_contact_notes(text, known_focus_children, known_participants):
    analyzed_data = analyze_contact_notes_with_gpt4(text, known_focus_children, known_participants)

    if not analyzed_data:
        print("No data was processed due to an earlier error.")
        return {}

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
    st.subheader("Extracted JSON Structure")
    st.json(analyzed_data)

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

    return analyzed_data


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

        if not response_text.startswith("{") or not response_text.endswith("}"):
            raise ValueError("Response is not in valid JSON format.")

        return json.loads(response_text)

    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {str(json_err)}")
        return {}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}

def process_screening_narrative(narrative):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that extracts structured data from a screening narrative and returns it in a valid JSON format. Use the information provided to fill in the details as completely as possible. If specific details are not mentioned, infer or leave fields empty only if no reasonable inference can be made."},
                {"role": "user",
                 "content": f"Extract the following fields from the screening narrative and return the results as JSON:\n\n<Screening Information>\n* Call Date and Time\n* Reason for the Call\n* Screening Name\n* Safely Surrendered Baby\n\n<Caller Information>\n* Caller Type\n* SCAR Form Received\n* Caller First Name\n* Caller Last Name\n* Email\n* Method of Report\n* Fax Number\n* Preferred Method to Receive ERNRD\n* Preferred Language\n* Interpreter Needed\n* Mandated Reporter Type\n* Employer/Organization Name\n* Interpreter Name\n* Phone Type\n* Country Code\n* Phone\n* Address Line 1\n* Address Line 2\n* City\n* State\n* Zip Code\n* Country\n* Call back Required\n* Best Date Time to Call Back\n\n<Persons Involved>\n* Role\n* Collateral Type\n* First Name\n* Last Name\n* Unknown Person at the time of Screening\n* Date of Birth\n* Approximate Age\n* County\n* Address\n\n<Safety Alert Information>\n* Alleged Perpetrator has access to the child(ren)\n* Dangerous animals on premises\n* Alleged Perpetrator’s Access\n* Dangerous Environment\n* Firearms in Home\n* Gang Affiliation or Gang Activity\n* Remote or Isolated location\n* Severe Mental Health Status (person)\n* Hostile, Aggressive Client (person)\n* Threat or Assault on Staff Member\n* Other\n* Is the call pertaining to a Fatality/ Near Fatality of a child?\n\nScreening Narrative: {narrative}"}
            ],
            max_tokens=1500,
        )

        response_text = response['choices'][0]['message']['content']
        response_text = response_text.strip().strip('```')

        if not response_text.startswith("{") or not response_text.endswith("}"):
            raise ValueError("Response is not in valid JSON format.")

        return json.loads(response_text)

    except json.JSONDecodeError as json_err:
        print(f"JSON decoding error: {str(json_err)}")
        return {}
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return {}

def display_screening_details_in_tab(screening_data):
    with st.sidebar:
        st.markdown('<p style="font-size: 20px; font-weight:bold;">Screening Details</p>', unsafe_allow_html=True)

        if screening_data:
            for section, details in screening_data.items():
                st.markdown(f"### {section.replace('_', ' ')}")  # Section header
                if isinstance(details, dict):
                    for key, value in details.items():
                        st.text_input(key.replace('_', ' '), value, key=f"{section}_{key}")
                elif isinstance(details, list):
                    for i, item in enumerate(details):
                        st.markdown(f"#### {section} {i + 1}")
                        if isinstance(item, dict):
                            for key, value in item.items():
                                st.text_input(key.replace('_', ' '), value, key=f"{section}_{i}_{key}")
                        else:
                            st.text_input(f"{section} {i + 1}", item, key=f"{section}_{i}")
        else:
            st.write("No data available to display.")


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

def display_app_details_in_tab(json_data):
    with st.sidebar:
        st.markdown('<p style="font-size: 20px; font-weight:bold;">Extracted Contact Note Details</p>', unsafe_allow_html=True)

        if json_data:
            for section, details in json_data.items():
                st.markdown(f"### {section.replace('_', ' ')}")  # Section header
                if isinstance(details, dict):
                    for key, value in details.items():
                        # Ensure even empty values are shown
                        st.text_input(key.replace('_', ' '), value if value else "", key=f"{section}_{key}")
                elif isinstance(details, list):
                    for i, item in enumerate(details):
                        st.markdown(f"#### {section} {i + 1}")
                        if isinstance(item, dict):
                            for key, value in item.items():
                                st.text_input(key.replace('_', ' '), value if value else "", key=f"{section}_{i}_{key}")
                        else:
                            st.text_input(f"{section} {i + 1}", item if item else "", key=f"{section}_{i}")
                else:
                    # Handle top-level fields
                    st.text_input(section.replace('_', ' '), details if details else "", key=f"{section}")
        else:
            st.write("No data available to display.")

if __name__ == "__main__":
    main()
