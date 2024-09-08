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

tab1, tab2, tab3 = st.tabs(["Action", "Insights", "Policy References"])

with tab1:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("""
            <div class="card">
                <h3>State of Wellbeing</h3>
                <p>The State of Wellbeing's self-service application revolutionizes the way households apply for and manage their benefits online. With a user-friendly interface, the platform seamlessly integrates the application processes for key assistance programs including TANF, SNAP, and Medicaid.</p>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
            <div class="card">
                <img src="https://peak.my.site.com/peak/resource/1701925644000/landingPageAssets/LandingPage/PageBannerIlustration/Illustration.svg" alt="Landing" style="width: 100%;">
            </div>
        """, unsafe_allow_html=True)

# Content for Tab 2
with tab3:
    st.write("We will list specific policy references here")
    # Will add more widgets and content here


class UserDetails(OpenAISchema):
    """Model for user details."""
    firstname: str = Field(..., description="First Name")
    lastname: str = Field(..., description="Last Name")
    dob: str = Field(..., description="Date of birth or when the person was born")
    ssn: str = Field(..., description="SSN of the individual")
    email: str = Field(..., description="Email")
    maritalstatus : str = Field(..., description="Marital Status")
    isapplicant: str = Field(..., description="Is this individual the applicant?")
    applicantrelationship : str = Field(..., description="Relationship to Applicant")
    citizenshipstatus : str = Field(..., description="Citizenship Status")
    residencystatus: str = Field(..., description="Residency Status")
    physicaladdress: str = Field(..., description="Physical Address")
    mailingaddress: str = Field(..., description="Mailing Address")
    ethnicity: str = Field(..., description="Ethnicity")
    race: str = Field(..., description="Race")
    typeofresidence: str = Field(..., description="Type of Residence e.g., own, rent, homeless, living with relatives etc.")
    livingarrangements: str = Field(..., description="Living Arrangements")
    currentcoverage: str = Field(..., description="Current Health Coverage: details of any existing health insurance.")
    healthcareneeds: str = Field(..., description="Healthcare Needs: specific healthcare needs or disabilities")
    specialcirumstances: str = Field(..., description="Special Circumstances: such as recent unemployment, homelessness, or domestic violence.")
    taxfilingstatus: str = Field(..., description="Tax Filing Status")
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
    employeraddress: str = Field(..., description="Employer Address")
    startdate: str = Field(..., description="Employment Start Date")
    enddate: str = Field(..., description="Employment End Date")
    salary: str = Field(..., description="Salary")
    workschedule: str = Field(..., description="Work Schedule")
    allverified: str = Field(..., description="Is all data verified?")


class Education(OpenAISchema):
    """Employment Details"""
    individualname: str = Field(..., description="Individual Name")
    startdate: str = Field(..., description="Education Start Date")
    enddate: str = Field(..., description="Education End Date")
    educationlevel: str = Field(..., description="Education Level")
    allverified: str = Field(..., description="Is all data verified?")


class Resources(OpenAISchema):
    """Expense Details"""
    individualname: str = Field(..., description="Individual Name")
    resourcename: str = Field(..., description="Resource Name")
    resourcetype: str = Field(..., description="Resource Type - e.g. Real Estate, Vehicles, Bank Accounts etc.")
    acquireddate: str = Field(..., description="Resource acquired Date")
    ownershippercent: str = Field(..., description="Ownership %")
    resourcefmv: str = Field(..., description="FMV of the resource")


class Expenses(OpenAISchema):
    """Expense Details"""
    individualname: str = Field(..., description="Individual Name")
    expensetype: str = Field(..., description="Expense Type")
    expensedate: str = Field(..., description="Expense Date")
    expenseamount: str = Field(..., description="Expense Amount")


class CaseDetails(OpenAISchema):
    """App Details"""
    caseNumber: str
    caseName: str
    programsappliedfor: str
    individuals: List[UserDetails]
    employments: List[Employments]
    education: List[Education]
    resources: List[Resources]
    expenses: List[Expenses]


def apply_program():
    return {
        "name": "applyProgram",
        "parameters": {
            "type": "object",
            "properties": {
                "programsappliedfor": {"type": "string"},
                "case_situation": {"type": "string"}
            },
            "required": ["programsappliedfor", "case_situation"],
        },
        "description": """This function helps an applicant for an application for specific program(s) and the specific 
        user-provided household situation. The only program(s) that can be applied for are TANF, SNAP or Medicaid.
        You should not proceed if the program(s) or the specific household situation has not been provided"""
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
        st.markdown("""
            <style>
                section[data-testid="stSidebar"] { width: 500px !important; }
                [data-testid=stSidebar] { background-color: #d1d8e1; }
            </style>
            """, unsafe_allow_html=True, )

        # Create two columns
        col1, col2 = st.columns([1, 2])

        with col1:
            # Display the image in the middle column
            st.image("../../Downloads/WBicon.png", width=125)
        with col2:
            st.write("")
            st.write("")
            st.title("Self-Service Application")

        text = "Welcome to the **State of Wellbeing's** *Self-Service Application*. This interface allows you to perform the following self-service actions:"
        st.markdown(text)

        # Defining available functions for Case management
        list_items = """
            - Apply for Program
            - Get my Case details
            - Case Actions
                - Update case (Report Changes)
                - Run Eligibility
                - Get Verification Checklist
            """

        # Display the list in Streamlit
        st.markdown(list_items)

    if "messages" not in st.session_state:
        content_string = "How can I assist you?"
        st.session_state["messages"] = [{"role": "assistant", "content": content_string}]
        # Initialize state variables if they don't exist
        st.session_state["case_number"] = ""
        st.session_state["apply_program"] = ""
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
    prompt = st.chat_input()
    if prompt:
        # Process the chat input here
        prompt = prompt.replace("$", "\$")
        prompt = prompt.replace("%", "\%")
        prompt = prompt.replace("=", "\=")

        with tab1:
            st.chat_message("user").write(prompt)
        arguments_array = []
        return_value = getFunctionCall(prompt, arguments_array)
        if return_value == "applyProgram":
            #st.chat_message("user").write("Reached Here")
            st.session_state["apply_program"] = arguments_array[0]
            st.session_state["case_situation"] = arguments_array[1]
            #st.chat_message("user").write(arguments_array)
            apply_Program(prompt)
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
    based on the user prompt. The available functions are 'apply_program()', 'get_case()', 'run_eligibility()'
    , 'update_case()' and 'get_vcl()'"""

    #st.session_state.messages.append({"role": "user", "content": prompt})
    temp_message = st.session_state.messages
    temp_message.append({"role": "system", "content": system_prompt})
    temp_message.append({"role": "user", "content": prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        functions=[apply_program(), get_case(), update_case(), run_eligibility(), get_vcl()],
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

        if function_call.name == "applyProgram":
            return "applyProgram"
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


def apply_Program(prompt: str):

    if prompt:
        program_applied_for = st.session_state["apply_program"]

        system_prompt = "You are a case worker for Human Services Programs conducting an interview for " + program_applied_for + """ 
                            All dates should be converted to mm-dd-yyyy format. 
                            IF any date calculations are needed, use""" + todays_date + """" as the current date.
                            All names should be converted to proper case.
                            All 'name' and 'type' fields should be converted to proper case.
                            You should not make up any data for any of the fields that is not provided."""

        st.session_state["case_number"] = "NEW123"
        st.session_state["case_situation"] = "Here are the case details for Case#: " + st.session_state["case_number"] + '''
                    named NEW CASE for ''' + st.session_state["case_number"] + " applying for " + st.session_state["apply_program"] + ":" + st.session_state["case_situation"]
        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": st.session_state["case_situation"]})

        with tab1:
            st.chat_message("assistant").write("Please wait...Processing your case...")

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            functions=[CaseDetails.openai_schema],
            temperature=0,
            messages=temp_message,
        )
        with tab1:
            st.chat_message("assistant").write("Processing complete")

        if response.choices[0].finish_reason == "function_call":
            case_details = CaseDetails.from_response(response)

            msg = response.choices[0].message
            st.session_state.messages.append(msg)

            # Display the new tab
            display_case_details_in_tab(case_details)
            display_insights("for the applying household. Make sure that you do not use any technical jargon in your response.")
        else:
            if response.choices[0].message.content:
                with tab1:
                    st.chat_message("assistant").write(response.choices[0].message.content)


def get_Case(prompt: str):
    if prompt:

        system_prompt = """Here are the instructions for you:
                                1. All dates should be converted to mm-dd-yyyy format.
                                2. IF any date calculations are needed, use """ + todays_date + """ as the current date.
                                3. All 'name' and 'type' fields should be converted to proper case.
                                4. Convert the user prompt to CaseDetails:
                                """
        if not st.session_state["case_situation"]:
            st.session_state["case_situation"] = "Here are the case details for Case#: " + st.session_state["case_number"] +  '''
            named Example Case for ''' + st.session_state["case_number"] + " and applying for TANF:"+'''
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

        msg = response.choices[0].message
        st.session_state.messages.append(msg)

        # Display the new tab
        display_case_details_in_tab(case_details)


def display_case_details_in_tab(case_details_param):
    with st.sidebar:

        st.markdown('<p style="font-size: 20px; font-weight:bold;">Data for Case</p>', unsafe_allow_html=True)
        st.chat_message("assistant").write("Case Number: " + getattr(case_details_param, "caseNumber"))
        st.chat_message("assistant").write("Case Name: " + getattr(case_details_param, "caseName"))
        st.chat_message("assistant").write("Program(s) Applied For: " + getattr(case_details_param, "programsappliedfor"))

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

        with st.expander("Education"):
            tablist = list()
            if len(getattr(case_details_param, "education")) == 0:
                st.chat_message("assistant").write("No Education")
            else:
                for a in getattr(case_details_param, "education"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(case_details_param, "education")):
                    for key, value in Education.openai_schema["parameters"]["properties"].items():
                        elementKey = 'ei' + str(i) + key
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

        with st.expander("Resources"):
            tablist = list()
            if len(getattr(case_details_param, "resources")) == 0:
                st.chat_message("assistant").write("No Resources")
            else:
                for a in getattr(case_details_param, "resources"):
                    tablist.append(a.individualname)
                tab = st.tabs(tablist)
                for i, ind in enumerate(getattr(case_details_param, "resources")):
                    for key, value in Resources.openai_schema["parameters"]["properties"].items():
                        elementKey = 're' + str(i) + key
                        tab[i].text_input(value["description"], getattr(ind, key), key=elementKey)

def update_Case(prompt):
    if prompt:

        temp_message = type(st.session_state['messages'])()
        temp_message.append({
                "role": "system",
                "content": """Modify the case details based on the user prompt and then convert it into an OpenAI structure.
                        All dates should be converted to mm - dd - yyyy format. IF any date calculations are needed, use
                        """ + todays_date + """" as the current date. All names should be converted to proper case.
                        All 'name' and 'type' fields should be converted to proper case.
                        You should not make up any data for any of the fields that is not provided."""
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
        system_prompt = "You are a helpful assistant. Please calculate " + st.session_state["apply_program"] + """
        eligibility for the user provided household data and provide the final results. Use California state policies 
        as your policy input, but do not use any reference to California in your response, instead replace the state's 
        name with Wellbeing. Also, do not tell the client that you don't have current policies - use it from the point 
        you have it"""
        user_prompt = st.session_state["case_situation"]

        with tab1:
            st.chat_message("assistant").write("Please wait...Running eligibility for case :" + st.session_state["case_number"])
        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": user_prompt})
        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=temp_message,
            )
        msg = response.choices[0].message
        st.session_state.messages.append(msg)
        with tab1:
            st.chat_message("assistant").write("Processing complete")
            formatted_response = response.choices[0].message.content.replace("$", "\$")
            formatted_response = formatted_response.replace("%", "\%")
            formatted_response = formatted_response.replace("=", "\=")
            st.chat_message("assistant").write(formatted_response)

        system_prompt = """Here are the instructions for you:
                                1. All dates should be converted to mm-dd-yyyy format.
                                2. IF any date calculations are needed, use """ + todays_date + """ as the current date.
                                3. All 'name' and 'type' fields should be converted to proper case.
                                4. Convert the user prompt to CaseDetails:
                                """

        temp_message = type(st.session_state['messages'])()
        temp_message.append({"role": "system", "content": system_prompt})
        temp_message.append({"role": "user", "content": st.session_state["case_situation"]})

        response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                functions=[CaseDetails.openai_schema],
                messages=temp_message,
            )
        case_details = CaseDetails.from_response(response)

        display_case_details_in_tab(case_details)

        display_insights("""of the eligibility results. The insights and next steps should be focused on the household 
                    who is applying for the benefits. Make sure that you do not use any technical jargon in your 
                    response. Use California state policies as your policy input, but do not use any reference to 
                    California in your response, instead replace the state's name with Wellbeing. Also, do not tell 
                    the client that you don't have current policies - use it from the point you have it""")


def display_insights(prompt: str):
    return
    with tab2:
        if prompt:
            system_prompt = "Given the current details, you should provide some actionable insights and next steps " + prompt
            temp_message = st.session_state.messages
            temp_message.append({"role": "system", "content": system_prompt})
            #temp_message.append({"role": "user", "content": user_prompt})
            response = openai.ChatCompletion.create(
                model="gpt-4-1106-preview",
                messages=temp_message,
            )
            formatted_response = response.choices[0].message.content.replace("$", "\$")
            formatted_response = formatted_response.replace("%", "\%")
            formatted_response = formatted_response.replace("=", "\=")
            st.chat_message("assistant").write(formatted_response)


if __name__ == "__main__":
    main()
