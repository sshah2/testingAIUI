import pandas as pd
import openai
import streamlit as st

def read_questions_answers_from_excel(uploaded_file):
    # Read the Excel file using Pandas
    spreadsheet = pd.read_excel(uploaded_file, sheet_name=None)

    # Extract questions and answers from each sheet
    questions = []
    answers = []

    # Define the columns for questions and answers for each sheet
    sheets_columns = {
        'Case Management': ('C', 'G'),
        'Locate': ('C', 'G'),
        'Establishment': ('C', 'G'),
        # Add other sheets and their respective columns here...
    }

    for sheet_name, (question_col, answer_col) in sheets_columns.items():
        if sheet_name in spreadsheet:
            data = spreadsheet[sheet_name]
            questions += data.iloc[:, ord(question_col) - ord('A')].tolist()
            answers += data.iloc[:, ord(answer_col) - ord('A')].tolist()

    return questions, answers


import openai

def generate_answer_with_openai(new_question, questions, answers, model="gpt-3.5-turbo-1106", openai_api_key="your-api-key"):
    # Ensure all questions and answers are strings and filter out NaNs
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    messages += [{"role": "user", "content": f"Q: {str(q)}\nA: {str(a)}"} for q, a in zip(questions, answers) if pd.notna(q) and pd.notna(a)]
    messages.append({"role": "user", "content": f"Q: {new_question}"})

    st.write(messages)
    # Send the messages to OpenAI's chat endpoint
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=1,
        api_key=openai_api_key
    )

    # Extract the answer
    answer = response.choices[0].message["content"]

    return answer

# Streamlit app
def main():
    st.title("Q&A Helper")

    # File uploader
    uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])

    # Process the file if uploaded
    if uploaded_file is not None:
        questions, answers = read_questions_answers_from_excel(uploaded_file)

        # User input for new question
        new_question = st.text_input("Enter your question")

        # Generate and display the answer
        if st.button("Get Answer"):
            answer = generate_answer_with_openai(new_question, questions, answers, model="gpt-3.5-turbo", openai_api_key="***REMOVED***")
            st.text_area("Answer", answer, height=300)

if __name__ == "__main__":
    main()
