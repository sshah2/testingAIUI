import json
import re

def read_cobol_file(cobol_file_path):
    with open(cobol_file_path, 'r') as file:
        lines = file.readlines()

    start_index = next((i for i, line in enumerate(lines) if 'PROCEDURE DIVISION.' in line.upper()), None)
    return lines[start_index:] if start_index is not None else []

def read_reserved_words(reserved_words_file_path):
    with open(reserved_words_file_path, 'r') as file:
        return set(word.strip().upper() for word in file)

def find_functions(lines, reserved_words):
    functions = []
    current_statement = ''

    for line in lines:
        line = line.upper()
        if len(line) > 6 and (line[6] == '*' or line[6] == '/'):  # Skip comment lines
            continue

        # Process from the 8th character
        trimmed_line = line[7:].strip()
        current_statement += ' ' + trimmed_line
        if '.' in current_statement:
            words = current_statement.split()
            if words and words[0].split('.')[0] not in reserved_words and words[0].split('.')[0] not in functions:
                functions.append(words[0].split('.')[0])
            current_statement = ''

    return functions


def read_json_file(json_file_path):
    with open(json_file_path, 'r') as file:
        return json.load(file)

def replace_function_with_summary(cobol_lines, json_data, reserved_words):
    modified_cobol_lines = cobol_lines.copy()
    current_function = None
    function_start_index = None
    function_boundaries = []
    accumulated_statement = ""
    rolling_summary = []

    for i, line in enumerate(modified_cobol_lines):
        if len(line) > 6 and (line[6] == '*' or line[6] == '/'):  # Skip comment lines
            continue

        # Accumulate statement considering lines after the 8th character
        processed_line = line[7:].strip()
        accumulated_statement += " " + processed_line

        # Check if the accumulated statement ends with a period
        if accumulated_statement.endswith('.'):
            words = accumulated_statement.split()
            if len(words) == 1:  # Check for a single word statement
                potential_function_name = words[0].rstrip('.').upper()

                if potential_function_name not in reserved_words:
                    if current_function is not None:
                        # End of previous function's code
                        function_boundaries.append((current_function, function_start_index, i))
                    current_function = potential_function_name
                    function_start_index = i + 1  # Start of new function's code

            accumulated_statement = ""  # Reset for next statement

    # Handle the last function
    if current_function is not None and function_start_index is not None:
        function_boundaries.append((current_function, function_start_index, len(modified_cobol_lines) - 1))

    # Replace function code with summary
    for func_name, start_idx, end_idx in function_boundaries:
        summary = next((func['Code Summary'] for func in json_data if func['Function Name'].upper() == func_name), None)
        if summary:
            rolling_summary.append(f"Code summary for {func_name}: {summary}\n")

        #if summary:
        #    replacement_text = f"Code summary for {func_name}: {summary}\n"
            # Replace the entire block with the summary
        #    modified_cobol_lines[start_idx:end_idx + 1] = [replacement_text] + ['\n'] * (end_idx - start_idx)

    return rolling_summary

# Main execution
cobol_file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'
json_file_path = 'C:\\Users\\sashah\\Downloads\\Processed_COBOL_Code.json'
reserved_words_file_path = 'C:\\Users\\sashah\\Downloads\\cobol_reserved_words.txt'

cobol_lines = read_cobol_file(cobol_file_path)
json_data = read_json_file(json_file_path)
reserved_words = read_reserved_words(reserved_words_file_path)

# Replace function code with code summary from JSON
modified_cobol_lines = replace_function_with_summary(cobol_lines, json_data, reserved_words)

# Print the modified COBOL code
print(''.join(modified_cobol_lines))
