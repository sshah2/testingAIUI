import json
import re
from collections import defaultdict, deque

def read_cobol_file(cobol_file_path):
    with open(cobol_file_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if 'PROCEDURE DIVISION' in line.upper():
            return lines[i:]
    return []

def read_reserved_words(reserved_words_file_path):
    with open(reserved_words_file_path, 'r') as file:
        return set(word.strip().upper() for word in file)

def find_functions(lines, reserved_words):
    functions = []
    current_statement = ''

    for line in lines:
        if len(line) > 6 and (line[6] == '*' or line[6] == '/'):  # Skip comment lines
            continue

        # Add line to current statement, process from 8th character
        current_statement += ' ' + line[7:].strip()
        if '.' in current_statement:
            # Split statement at the period
            potential_func_name, _ = current_statement.split('.', 1)
            # Split at spaces to isolate the first word
            words = potential_func_name.split()
            if words and words[0] not in reserved_words:
                func_name = words[0]
                if func_name not in functions:
                    functions.append(func_name)
            current_statement = ''  # Reset for the next statement

    return functions

def get_called_and_external_functions(line, reserved_words):
    called_functions = set()
    external_functions = set()

    perform_regex = r'PERFORM\s+([\w-]+)(?:\s+THRU\s+([\w-]+))?'
    call_regex = r'CALL\s+([\'"]?[\w-]+[\'"]?)'
    goto_regex = r'GO\s+TO\s+([\w-]+)'

    for match in re.finditer(perform_regex, line, re.IGNORECASE):
        para_name = match.group(1)
        para_name_2 = match.group(2)
        if para_name and para_name.upper() not in reserved_words:
            called_functions.add(para_name)
        if para_name_2 and para_name_2.upper() not in reserved_words:
            called_functions.add(para_name_2)

    for match in re.finditer(call_regex, line, re.IGNORECASE):
        external_function_name = match.group(1)
        if external_function_name and not re.match(r'^[\'"]?TO[\'"]?$', external_function_name, re.IGNORECASE):
            external_functions.add(external_function_name.strip('\'"'))

    for match in re.finditer(goto_regex, line, re.IGNORECASE):
        para_name = match.group(1)
        if para_name and para_name.upper() not in reserved_words:
            called_functions.add(para_name)

    return called_functions, external_functions

def get_function_code(lines, functions, reserved_words):
    function_code_data = []
    current_function = None
    current_code = ''
    current_called_functions = set()
    current_external_functions = set()

    for line in lines:
        if len(line) > 6 and (line[6] == '*' or line[6] == '/'):  # Skip comment lines
            continue

        trimmed_line = line[7:].upper()

        if any(func + '.' == trimmed_line.strip() for func in functions):
            if current_function:
                function_code_data.append({
                    "Function Name": current_function,
                    "Source Code": current_code.strip(),
                    "Called Functions": list(current_called_functions),
                    "External Functions": list(current_external_functions)
                })
                current_code = ''
                current_called_functions = set()
                current_external_functions = set()
            current_function = trimmed_line.strip()[:-1]
        else:
            current_code += trimmed_line.strip() + '\n'
            called_functions, external_functions = get_called_and_external_functions(trimmed_line, reserved_words)
            current_called_functions.update(called_functions)
            current_external_functions.update(external_functions)

    if current_function:
        function_code_data.append({
            "Function Name": current_function,
            "Source Code": current_code.strip(),
            "Called Functions": list(current_called_functions),
            "External Functions": list(current_external_functions)
        })

    return function_code_data

def build_dependency_graph(function_code_data):
    graph = defaultdict(list)
    all_functions = set()

    for data in function_code_data:
        function_name = data["Function Name"]
        all_functions.add(function_name)
        called_functions = set(data["Called Functions"])
        graph[function_name] = called_functions

    return graph, all_functions

def topological_sort(graph, all_functions):
    no_dependency_funcs = [func for func in all_functions if not graph[func]]
    sorted_funcs = []
    processed = set(no_dependency_funcs)

    # Process functions with no dependencies
    for func in no_dependency_funcs:
        processed.add(func)
        sorted_funcs.append(func)

    # Process remaining functions
    for func in all_functions:
        if func not in processed:
            sorted_funcs.append(func)

    return sorted_funcs

def get_sorted_functions(function_code_data):
    graph, functions_with_calls = build_dependency_graph(function_code_data)
    sorted_function_names = topological_sort(graph, functions_with_calls)
    sorted_function_data = []
    for func_name in sorted_function_names:
        for data in function_code_data:
            if data["Function Name"] == func_name:
                sorted_function_data.append(data)
                break
    return sorted_function_data

# Main execution
cobol_file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'
reserved_words_file_path = 'C:\\Users\\sashah\\Downloads\\cobol_reserved_words.txt'

cobol_lines = read_cobol_file(cobol_file_path)
reserved_words = read_reserved_words(reserved_words_file_path)
functions = find_functions(cobol_lines, reserved_words)
function_code_data = get_function_code(cobol_lines, functions, reserved_words)

# Print original JSON structure
original_json_output = json.dumps(function_code_data, indent=4)
#print("Original JSON:\n", original_json_output)

# Print sorted JSON structure
sorted_function_code_data = get_sorted_functions(function_code_data)
sorted_json_output = json.dumps(sorted_function_code_data, indent=4)
print("\nSorted JSON:\n", sorted_json_output)

# Assuming you have already run the code to populate function_code_data and sorted_function_code_data

# Count of original functions
original_function_count = len(function_code_data)

# Count of sorted functions
sorted_function_count = len(sorted_function_code_data)

print("Count of original functions:", original_function_count)
print("Count of sorted functions:", sorted_function_count)

