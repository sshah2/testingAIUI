import openai
import streamlit as st
import json
from pydantic import BaseModel, Field, field_validator
from typing import List
from instructor import OpenAISchema
from datetime import date, datetime

openai.api_key = "***REMOVED***"
# Textual month, day and year
todays_date = date.today().strftime("%B %d, %Y")

st.subheader("Conversational UI")

tab1, tab2, tab3 = st.tabs(["Prompt", "Insights", "Next Best Action"])

# Content for Tab 1
# with tab1:
# st.write("This is the content of Tab 1")
# You can add more widgets or content here

# Content for Tab 2
with tab2:
    st.write("Here are some tangible insights:")
    # You can add more widgets or content here

# Content for Tab 3
with tab3:
    st.write("Here are the proposed Next Best Action(s):")
    # You can add more widgets or content here


class UserDetails(OpenAISchema):
    """Model for user details."""
    firstname: str = Field(..., description="First Name")
    lastname: str = Field(..., description="Last Name")
    dob: str = Field(..., description="Date of birth")
    ssn: str = Field(..., description="SSN")
    citizenshipstatus : str = Field(..., description="Citizenship Status")
    residencystatus: str = Field(..., description="Residency Status")
    taxfilingstatus: str = Field(..., description="Tax Filing Status")
    email: str = Field(..., description="Email")
    isdependent: str = Field(..., description="Is this individual a dependent?")
    allverified: str = Field(..., description="Is all data verified?")

    #@field_validator('dob')
    #def check_dob(cls, value):
    #    try:
    #        parsed_dob = datetime.strptime(value, '%Y-%m-%d').date()  # Adjust format as needed
    #        if parsed_dob > date.today():
    #            raise ValueError('Date of birth cannot be in the future')
    #    except ValueError:
    #        raise ValueError("Invalid date format for dob. Please use YYYY-MM-DD format.")
    #    return value


class Employments(OpenAISchema):
    """Employment Details"""
    individualname: str = Field(..., description="Individual Name")
    employername: str = Field(..., description="Employer Name")
    startdate: str = Field(..., description="Employment Start Date")
    enddate: str = Field(..., description="Employment End Date")
    salary: str = Field(..., description="Salary")
    allverified: str = Field(..., description="Is all data verified?")


class Expenses(OpenAISchema):
    """Expense Details"""
    individualname: str = Field(..., description="Individual Name")
    expensetype: str = Field(..., description="Expense Type")
    expensedate: str = Field(..., description="Expense Date")
    expenseamount: str = Field(..., description="Expense Amount")


class AppDetails(OpenAISchema):
    """App Details"""
    individuals: List[UserDetails]
    employments: List[Employments]
    expenses: List[Expenses]


class CaseDetails(OpenAISchema):
    """App Details"""
    caseNumber: str
    caseName: str
    individuals: List[UserDetails]
    employments: List[Employments]
    expenses: List[Expenses]


def conduct_interview():
    return {
        "name": "conductInterview",
        "parameters": {
            "type": "object",
            "properties": {
                "case_situation": {
                    "type": "string"
                }
            },
            "required": ["case_situation"],
        },
        "description": """This function helps in conducting an interview for the user-provided household situation.
        You should not proceed if the household situation has not been provided"""
    }


def get_case():
    return {
        "name": "getCase",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string"
                }
            },
            "required": ["case_id"],
        },
        "description": """This function retrieves case information based on the user provided case ID. 
        You should not proceed if a case number has not been provided"""
    }


def update_case():
    return {
        "name": "updateCase",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {"type": "string"},
                "updatescenario": {"type": "string"}
                        },
            "required": ["case_id", "updatescenario"],
        },
        "description": """This function updates data based on the user-provided scenario and for the user-provided case ID. 
        You should not proceed if a case number or the update scenario has not been provided"""
    }


def run_eligibility():
    return {
        "name": "runEligibility",
        "parameters": {
            "type": "object",
            "properties": {
                "case_id": {
                    "type": "string"
                }
            },
            "required": ["case_id"],
        },
        "description": """This function will run eligibility on the user provided case ID. 
        You should not proceed if a case number has not been provided"""
    }


def get_vcl():
    return {
        "name": "getVCL",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        "description": "This function will get the verification checklist for the provided case ID."
        }


# Main application logic
def main():

    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] { width: 500px !important; }
            </style>
            """,
            unsafe_allow_html=True,
        )
    #    # st.image("../../Downloads/copilot1.png")
        st.title("Generic Case Management")
        # Text with Markdown for bold and italics
        text = "Welcome to the new world of ***No-UI UI***. This interface allows you to perform the following case management actions:"
        st.markdown(text)

        # Defining available functions for Case management

        list_items = """
            - Conduct an interview
            - Get Case details
            - Case Actions
                - Update Case
                - Run Medi-Cal Eligibility
                - Get Verification Checklist
            """

        # Display the list in Streamlit
        st.markdown(list_items)

    # Create tabs

    # Initialize state variables if they don't exist
    if "messages" not in st.session_state:
        content_string = "What action do you want me to perform now?"
        st.session_state["messages"] = [{"role": "assistant", "content": content_string}]
        st.session_state["case_number"] = ""
        st.session_state["intake_scenario"] = ""
        st.session_state["update_scenario"] = ""
        st.session_state["case_situation"] = ""

    # Displaying chat messages
    for msg in st.session_state.messages:
        if msg["content"]:
            role_message = msg["role"]

            if role_message != "system":
                with tab1:
                    st.chat_message(msg["role"]).write(msg["content"])

    # Chat input in the main body
    #with tab1:
    prompt = st.chat_input()
    if prompt:
        # Process the chat input here
        with tab1:
            st.chat_message("user").write(prompt)
        arguments_array = []
        return_value = getFunctionCall(prompt, arguments_array)
        if return_value == "conductInterview":
            st.session_state["intake_scenario"] = arguments_array[0]
            conduct_Interview(prompt)
        elif return_value == "getCase":
            st.session_state["case_number"] = arguments_array[0]
            get_Case(prompt)
        elif return_value == "updateCase":
            st.session_state["case_number"] = arguments_array[0]
            st.session_state["update_scenario"] = arguments_array[1]
            update_Case(prompt)
        elif return_value == "runEligibility":
            st.session_state["case_number"] = arguments_array[0]
            run_Eligibility(prompt)
        elif return_value == "getVCL":
            get_Vcl(prompt)


def getFunctionCall(prompt, arguments_array):

    system_prompt = """As an AI assistant, your primary task is to identify which specific function needs to be called 
    based on the user prompt. The available functions are 'conduct_interview()', 'get_case()', 'run_eligibility()'
    , 'update_case()' and 'get_vcl()'"""

    st.session_state.messages.append({"role": "user", "content": prompt})
    temp_message = st.session_state.messages
    temp_message.append({"role": "system", "content": system_prompt})
    temp_message.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        functions=[conduct_interview(), get_case(), update_case(), run_eligibility(), get_vcl()],
        temperature=1,
        messages=temp_message,
    )

    if response.choices[0].finish_reason == "function_call":
        function_call = response.choices[0].message.function_call

        # Extracting the arguments string
        arguments_str = response["choices"][0]["message"]["function_call"]["arguments"]

        # Parsing the arguments string into a dictionary
        arguments_dict = json.loads(arguments_str)

        # Converting the dictionary values into an array of strings
        arguments_array.extend([str(value) for value in arguments_dict.values()])

        if function_call.name == "conductInterview":
            return "conductInterview"
        elif function_call.name == "getCase":
            return "getCase"
        elif function_call.name == "updateCase":
            return "updateCase"
        elif function_call.name == "runEligibility":
            return "runEligibility"
        elif function_call.name == "getVCL":
            return "getVCL"
        else:
            return "None"
    else:
        with tab1:
            st.chat_message("assistant").write(response.choices[0].message.content)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        return "None"


def conduct_Interview(prompt: str):

    if prompt:

        system_prompt = """You are a case worker for Human Services Programs conducting an interview. 
                            All dates should be converted to mm-dd-yyyy format. 
                            IF any date calculations are needed, use""" + todays_date + """" as the current date.
                            All names should be converted to proper case.
                            All 'name' and 'type' fields should be converted to proper case.
                            You should not make up any data for any of the fields that is not provided."""

        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": st.session_state["intake_scenario"]})

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            functions=[AppDetails.openai_schema],
            temperature=0,
            messages=temp_message,
        )

        if response.choices[0].finish_reason == "function_call":
            app_details = AppDetails.from_response(response)

            msg = response.choices[0].message
            st.session_state.messages.append(msg)

            with st.sidebar:
                st.markdown(
                    """
                    <style>
                        section[data-testid="stSidebar"] { width: 500px !important; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                    )

            # Display the new tab
            display_app_details_in_tab(app_details)
        else:
            if response.choices[0].message.content:
                with tab1:
                    st.chat_message("assistant").write(response.choices[0].message.content)


def display_app_details_in_tab(app_details_param):
    # This function will show the actual app details
    with st.sidebar:

        st.markdown('<p style="font-size: 20px; font-weight:bold;">Data Entry Form</p>', unsafe_allow_html=True)

        with st.expander("Demographics", expanded=True):
            tablist = list()
            for a in getattr(app_details_param, "individuals"):
                tablist.append(a.firstname)
            tab = st.tabs(tablist)
            for i, ind in enumerate(getattr(app_details_param, "individuals")):
                for key, value in UserDetails.openai_schema["parameters"]["properties"].items():
                    elementKey = 'in' + str(i) + key
                    tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)

        with st.expander("Employments"):
            tablist = list()
            if len(getattr(app_details_param, "employments")) == 0:
                st.chat_message("assistant").write("No Employment")
            else:
                for a in getattr(app_details_param, "employments"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(app_details_param, "employments")):
                    for key, value in Employments.openai_schema["parameters"]["properties"].items():
                        elementKey = 'em' + str(i) + key
                        tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)

        with st.expander("Expenses"):
            tablist = list()
            if len(getattr(app_details_param, "expenses")) == 0:
                st.chat_message("assistant").write("No Expenses")
            else:
                for a in getattr(app_details_param, "expenses"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(app_details_param, "expenses")):
                    for key, value in Expenses.openai_schema["parameters"]["properties"].items():
                        elementKey = 'ex' + str(i) + key
                        tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)


def get_Case(prompt: str):
    if prompt:
        # The variable case_details_json now contains the JSON data as a string.

        system_prompt = """Here are the instructions for you:
                                1. All dates should be converted to mm-dd-yyyy format.
                                2. IF any date calculations are needed, use """ + todays_date + """ as the current date.
                                3. All 'name' and 'type' fields should be converted to proper case.
                                4. Convert the user prompt to CaseDetails:
                                """
        if not st.session_state["case_situation"]:
            st.session_state["case_situation"] = "Here are the case details for Case#: " + st.session_state["case_number"] +  '''
            named Example Case for ''' + st.session_state["case_number"] + ":"+'''
                        1.  Reid Smith reid.smith@gmail.com was born on Jan 1 1970 with SSN 123-45-6789
                        2.  Jill smith jill.smith@gmail.com was born on Jan 1 1971 with SSN 234-56-7890.
                        Reid works at Walmart since 1/1/2000 making $200 a week.
                        Jill spent 200 on utilities on the 1st of last month.
                        Reid and Jill are both US citizens and reside in California. Jill is dependent on Reid.
            '''

        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": st.session_state["case_situation"]})
        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                functions=[CaseDetails.openai_schema],
                messages=temp_message,
            )
        case_details = CaseDetails.from_response(response)
        # Display forms or other content based on the response

        msg = response.choices[0].message
        st.session_state.messages.append(msg)

        with st.sidebar:
                st.markdown(
                    """
                    <style>
                        section[data-testid="stSidebar"] { width: 500px !important; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                        )

                # Display the new tab
                display_case_details_in_tab(case_details)


            #case_details_json = {"caseNumber": "12345" , "caseName": "Example Case", "individuals": [
                    # {"firstname": "John", "lastname": "Smith", "email": "john.smith@gmail.com", "dob": "1/1/1970" },
                    # {"firstname": "Jamie","lastname": "Smith","email": "jamie.smith@gmail.com", "dob": "1/1/1971" }],
                # "employments": [ {"individualname": "John Smith","employername": "Walmart", "startdate": "1/1/2001",
                        # "enddate": "", "salary": "200 per week" } ],
                # "expenses": [] }

def display_case_details_in_tab(case_details_param):
    with st.sidebar:

        st.markdown('<p style="font-size: 20px; font-weight:bold;">Data for Case</p>', unsafe_allow_html=True)
        st.chat_message("assistant").write("Case Number: " + getattr(case_details_param, "caseNumber"))
        st.chat_message("assistant").write("Case Name: " + getattr(case_details_param, "caseName"))

        with st.expander("Demographics", expanded=True):
            tablist = list()
            for a in getattr(case_details_param, "individuals"):
                tablist.append(a.firstname)
            tab = st.tabs(tablist)
            for i, ind in enumerate(getattr(case_details_param, "individuals")):
                for key, value in UserDetails.openai_schema["parameters"]["properties"].items():
                    elementKey = 'in' + str(i) + key
                    tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)

        with st.expander("Employments"):
            tablist = list()
            if len(getattr(case_details_param, "employments")) == 0:
                st.chat_message("assistant").write("No Employment")
            else:
                for a in getattr(case_details_param, "employments"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(case_details_param, "employments")):
                    for key, value in Employments.openai_schema["parameters"]["properties"].items():
                        elementKey = 'em' + str(i) + key
                        tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)

        with st.expander("Expenses"):
            tablist = list()
            if len(getattr(case_details_param, "expenses")) == 0:
                st.chat_message("assistant").write("No Expenses")
            else:
                for a in getattr(case_details_param, "expenses"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(case_details_param, "expenses")):
                    for key, value in Expenses.openai_schema["parameters"]["properties"].items():
                        elementKey = 'ex' + str(i) + key
                        tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)


def update_Case(prompt):
    if prompt:

        temp_message = type(st.session_state['messages'])()
        temp_message.append({
                "role": "system",
                "content": "Modify the case details based on the user prompt and then convert it into an OpenAI structure."
            })

        user_prompt = st.session_state["update_scenario"]
        case_details = st.session_state["case_situation"]
        temp_message.append({
                "role": "user",
                "content": f"User prompt: {user_prompt}. Current case details: {case_details}"
            })

        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                functions=[CaseDetails.openai_schema],
                messages=temp_message,
            )

        case_details = CaseDetails.from_response(response)
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        st.session_state["case_situation"] = case_details

        with st.sidebar:
                st.markdown(
                    """
                    <style>
                        section[data-testid="stSidebar"] { width: 500px !important; }
                    </style>
                    """,
                    unsafe_allow_html=True,
                        )

                # Display the new tab
                display_case_details_in_tab(case_details)


def run_Eligibility(prompt: str):

    if prompt:
        system_prompt = """You are a helpful assistant. Please calculate Medi-cal eligibility for the user provided 
        household data and provide the final results"""
        user_prompt = "Case #: " + st.session_state["case_number"] + "named Household for Case " + st.session_state["case_number"] + '''
        . Here are the household details:
                        1.  John smith john.smith@gmail.com was born on Jan 1 1970 with SSN 123-45-6789 
                        2.  Jill smith jill.smith@gmail.com was born on Jan 1 1971 with SSN 234-56-7890. 
                        John works at Walmart since 1/1/2000 making $200 a week. 
                        Jill spent 200 on utilities on the 1st of last month. 
                        John and Jill are both US citizens and reside in California. Jill is dependent on John.
                        All verifications have been provided and are complete.
            '''

        with tab1:
            st.chat_message("assistant").write("Please wait...Running eligibility for fcase :" + st.session_state["case_number"])
        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": user_prompt})
        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=temp_message,
            )
        #case_details = CaseDetails.from_response(response)
        with tab1:
            st.chat_message("assistant").write(response.choices[0].message.content)
            # Display forms or other content based on the response

        msg = response.choices[0].message
        st.session_state.messages.append(msg)



if __name__ == "__main__":
    main()
