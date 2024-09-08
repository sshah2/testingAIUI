import openai
import PyPDF2


def extract_text_from_pdf(pdf_path):
    """Extracts text from each page of the specified PDF."""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = [page.extract_text() for page in reader.pages]
    return "\n".join(text)


def structure_data_with_openai(text, openai_api_key):
    """Uses OpenAI to convert flat text to structured JSON format."""
    openai.api_key = openai_api_key
    print("Here is the PDF output")
    print(text)
    print("Done")
    system_prompt = """For the provided text, I want you to do the following: "
                        1) Only focus on everything under Section 1 
                        2) Within Section 1, each field should be a separate sub-section. I don't want you to 
                        consolidate fields that you think are the same - if they are fields - they need to be included. 
                        Here are the specific columns I need within each of the field sub-section: 
                        {"Field_type" , "Field_label", "Required?", "Picklist_Values", 
                        "Conditional_Display", "Validation"}
                            a) "field_type" - Identify the fields that need to be captured - 
                            could be Header, Text, Radio Button, Check-Box, Date, Picklist
                            b) "Field_label" - Identify label corresponding to the field
                            c) "Required?" - Identify if as a DMV expert, you would say this is a required column or not
                            d) "Picklist_Values" - Identify the picklist value if the field_type is Picklist
                            e) "Conditional_Display" - If you identified that this field should only be displayed based 
                            on some condition of data
                            f) "Validation" - Identify if as a DMV expert, you would add any validations on this field

                        Please make sure you do not miss any fields. The text is {""" + text + "}"

    conversation = [
        {"role": "system", "content": "You are a helpful assistant that will help create a json structure based on the user-provided text."},
        {"role": "user", "content": system_prompt}
    ]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        temperature=0.3,
        messages=conversation,
    )

    return response.choices[0].message.content
    #return ""

def main():
    pdf_path = "C:\\Users\\sashah\\Downloads\\reg343.pdf"
    openai_api_key = "***REMOVED***"

    # Extract text from PDF
    text = extract_text_from_pdf(pdf_path)

    # Get structured JSON from OpenAI
    structured_json = structure_data_with_openai(text, openai_api_key)
    print(structured_json)


if __name__ == "__main__":
    main()
