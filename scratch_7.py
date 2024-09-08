import openai

messages = []
    #{"role": "system", "content": "You are a knowledgeable COBOL programmer explaining code in business terms."}]
openai.api_key = "***REMOVED***"


def read_cobol_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()


def preprocess_cobol_lines(cobol_lines):
    preprocessed_lines = []
    procedure_division_found = False
    for line in cobol_lines:
        if 'PROCEDURE DIVISION.' in line:
            procedure_division_found = True
        if procedure_division_found:
            if len(line) >= 7 and line[6] != '*':  # Exclude comment lines
                if line[6] == '-':  # Line continuation detected
                    # Append line continuation (excluding first 6 chars) to the last line in preprocessed_lines
                    if preprocessed_lines:
                        preprocessed_lines[-1] = preprocessed_lines[-1].rstrip() + ' ' + line[7:].lstrip()
                else:
                    preprocessed_lines.append(line[6:])  # Strip the first 6 characters
    return preprocessed_lines


def extract_perform_targets(cobol_lines):
    perform_targets = set()
    for line in cobol_lines:
        if line.strip().startswith('PERFORM'):
            tokens = line.strip().split()
            # Handle 'PERFORM ... UNTIL' by taking only the first part as the target
            if len(tokens) > 1 and tokens[1].upper() != 'UNTIL':
                target = tokens[1].split('.')[0]
                perform_targets.add(target)
    return perform_targets


def find_section_or_paragraph_code(cobol_lines, targets):
    sections = {}
    remaining_lines = []
    current_section = None
    current_content = []
    for line in cobol_lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped.split()[0].rstrip('.') in targets:
            if current_section:
                sections[current_section] = current_content
                current_content = []
            current_section = line_stripped.split()[0].rstrip('.')
        elif current_section:
            current_content.append(line)
        else:
            remaining_lines.append(line)

    if current_section:
        sections[current_section] = current_content

    return sections, remaining_lines


def main():
    file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'  # Your COBOL file path
    cobol_lines = read_cobol_file(file_path)
    preprocessed_lines = preprocess_cobol_lines(cobol_lines)
    perform_targets = extract_perform_targets(preprocessed_lines)
    sections, remaining_proc_div = find_section_or_paragraph_code(preprocessed_lines, perform_targets)
    count = 1
    user_prompt = ""
    messages_append = ""
    for section, content in sections.items():
        user_prompt = "".join(content)

        system_prompt = """Summarize in business terms and in less than 5 sentences the provided user prompt. 
        Do not use any technical terms in your explanation - it should be a summary only about what the business user 
        can understand. You summary should start with <Here is what the Function """ + section + "> does:"
        temp_messages = []
        temp_messages.append({"role": "system", "content": system_prompt})
        temp_messages.append({"role": "user", "content": user_prompt})

        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",  # Use the appropriate model
            messages=temp_messages
        )
        messages_append = messages_append + response.choices[0].message['content']
        print(count)
        print("messages append")
        print(messages_append)
        count = count + 1
        #messages.append({"role": "assistant", "content": response.choices[0].message['content']})

        #print("messages")
        #print(messages)

    print("messages append")
    print(messages_append)

    system_prompt = """You are a knowledgeable COBOL programmer explaining code in business terms.
    You will analyze the Procedure Division Code in the provided user prompt and use the specific function
    summaries available in the assistant prompt"""
    user_prompt = "".join(remaining_proc_div)

    temp_messages = []
    temp_messages.append({"role": "system", "content": system_prompt})
    temp_messages.append({"role": "user", "content": user_prompt})
    temp_messages.append({"role": "assistant", "content": messages_append})
    #messages.append({"role": "system", "content": system_prompt})
    #messages.append({"role": "user", "content": user_prompt})

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # Use the appropriate model
        messages=temp_messages
    )

    print("response")
    print(response)

if __name__ == "__main__":
    main()
