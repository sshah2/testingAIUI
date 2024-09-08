import json
import re
from collections import defaultdict

def read_cobol_file(cobol_file_path):
    with open(cobol_file_path, 'r') as file:
        lines = file.readlines()

    start_index = next((i for i, line in enumerate(lines) if 'PROCEDURE DIVISION' in line.upper()), None)
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

def get_function_code(lines, functions, reserved_words):
    function_code_data = []
    current_function = None
    current_code = ''
    current_called_functions = set()
    current_external_functions = set()

    for line in lines:
        if len(line) > 6 and line[6] == '*':  # Skip comment lines
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
            current_code += line.strip() + '\n'  # Keep the original line format
            # Pass current_function as an argument
            called_functions, external_functions = get_called_and_external_functions(trimmed_line, reserved_words, current_function)
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

def get_called_and_external_functions(line, reserved_words, function_name):
    called_functions = set()
    external_functions = set()
    line = line.upper()
    # Splitting the line into words for easier processing
    words = line.strip().split()

    if len(words) > 1 and words[0].upper() == 'PERFORM':
        # Check for 'PERFORM <value> TIMES' pattern
        if words[-1].upper() == 'TIMES':
            # Skip if it's a loop control statement
            if len(words) <= 3 or words[1].upper() in reserved_words or words[1].isdigit():
                pass  # This is a loop control, not a function call
            else:
                # Handle regular 'PERFORM <function>' pattern
                func = words[1]
                if func not in reserved_words and func.upper() != function_name:
                    called_functions.add(func.upper())
        elif 'THRU' in words:
            # Handle 'PERFORM <a> THRU <b>' pattern
            try:
                start_index = words.index('THRU') - 1
                end_index = start_index + 2
                func_start = words[start_index].split('.')[0]  # Remove period if present
                func_end = words[end_index].split('.')[0]  # Remove period if present
                if func_start not in reserved_words and func_start.upper() != function_name:
                    called_functions.add(func_start.upper())
                if func_end not in reserved_words and func_end.upper() != function_name:
                    called_functions.add(func_end.upper())
            except (IndexError, ValueError):
                pass
        else:
            # Handle regular 'PERFORM <function>' pattern
            func = words[1].split('.')[0]  # Remove period if present
            if func not in reserved_words and func.upper() != function_name:
                called_functions.add(func.upper())

    # Check for 'CALL <external_function_name>' pattern
    if 'CALL' in line:
        call_match = re.search(r'CALL\s+([\'"]?[\w-]+[\'"]?)', line, re.IGNORECASE)
        if call_match:
            external_function_name = call_match.group(1).strip('\'"')
            external_function_name = external_function_name.split('.')[0]  # Remove period if present
            if external_function_name not in reserved_words:
                external_functions.add(external_function_name.upper())

    # Check for 'GO TO <para_name>' pattern
    if 'GO TO' in line:
        goto_match = re.search(r'GO\s+TO\s+([\w-]+)', line, re.IGNORECASE)
        if goto_match:
            para_name = goto_match.group(1)
            if para_name not in reserved_words:
                called_functions.add(para_name.upper())

    return called_functions, external_functions

def build_dependency_graph(function_code_data):
    graph = defaultdict(list)
    for data in function_code_data:
        function_name = data["Function Name"]
        called_functions = data["Called Functions"]
        graph[function_name].extend(called_functions)
    return graph

def gather_all_called_functions(func_name, graph, visited=None):
    if visited is None:
        visited = set()
    all_called = set()

    if func_name in graph:
        for called_func in graph[func_name]:
            if called_func not in visited:
                visited.add(called_func)
                all_called.add(called_func)
                all_called.update(gather_all_called_functions(called_func, graph, visited))

    return all_called

def get_function_code_with_all_calls(lines, functions, reserved_words, graph):
    function_code_data = []
    current_function = None
    current_code = ''
    current_called_functions = set()
    current_external_functions = set()

    for line in lines:

        line = line.upper()

        if len(line) > 6 and line[6] == '*':  # Skip comment lines
            continue

        trimmed_line = line[7:].upper()

        if any(func + '.' == trimmed_line.strip() for func in functions):
            if current_function:
                all_called_functions = gather_all_called_functions(current_function, graph)
                function_code_data.append({
                    "Function Name": current_function,
                    "Source Code": current_code.strip(),
                    "Called Functions": list(current_called_functions),
                    "External Functions": list(current_external_functions),
                    "All Called Functions": list(all_called_functions)
                })
                current_code = ''
                current_called_functions = set()
                current_external_functions = set()
            current_function = trimmed_line.strip()[:-1]
        else:
            current_code += line.strip() + '\n'  # Preserve the original line format
            # Correctly pass current_function as an argument
            called_functions, external_functions = get_called_and_external_functions(trimmed_line, reserved_words, current_function)
            current_called_functions.update(called_functions)
            current_external_functions.update(external_functions)

    if current_function:
        all_called_functions = gather_all_called_functions(current_function, graph)
        function_code_data.append({
            "Function Name": current_function,
            "Source Code": current_code.strip(),
            "Called Functions": list(current_called_functions),
            "External Functions": list(current_external_functions),
            "All Called Functions": list(all_called_functions)
        })

    return function_code_data

def sort_functions(json_data):
    # Convert JSON string to Python object
    functions = json.loads(json_data)

    # Helper function to check if all dependencies are processed
    def all_deps_processed(func, processed_set):
        return all(dep in processed_set for dep in func["All Called Functions"])

    processed = set()
    sorted_functions = []
    previous_processed_count = -1

    # Loop until all functions are processed or no progress is made (infinite loop)
    while len(processed) < len(functions) and len(processed) != previous_processed_count:
        previous_processed_count = len(processed)

        for func in functions:
            func_name = func["Function Name"]
            if func_name not in processed:
                # Inside the while loop, before if not func["All Called Functions"] or all_deps_processed(func, processed):

                # Inside the while loop, before if not func["All Called Functions"] or all_deps_processed(func, processed):

                if func_name == "MADE-UP":
                    unprocessed_deps = [dep for dep in func["All Called Functions"] if dep not in processed]
                    all_deps = ", ".join(func["All Called Functions"])
                    processed_deps = ", ".join([dep for dep in func["All Called Functions"] if dep in processed])
                    print(f"Function: {func_name}")
                    print(f"All dependencies: {all_deps}")
                    print(f"Processed dependencies: {processed_deps}")
                    print(f"Unprocessed dependencies: {unprocessed_deps}")

                if not func["All Called Functions"] or all_deps_processed(func, processed):
                    func["processed"] = True
                    processed.add(func_name)
                    sorted_functions.append(func)

    if len(processed) != len(functions):
        unprocessed_functions = [func["Function Name"] for func in functions if func["Function Name"] not in processed]
        if len(processed) != len(functions):
            print("Reached-1")
            unprocessed_functions = [func for func in functions if func["Function Name"] not in processed]
            print("Unprocessed functions and their dependencies:")
            for func in unprocessed_functions:
                print(f"{func['Function Name']}: Dependencies - {func['All Called Functions']}")

            print("Reached-2")
            unprocessed_functions = [func for func in functions if func["Function Name"] not in processed]
            print("Unprocessed functions and their dependencies:")
            for func in unprocessed_functions:
                print(f"{func['Function Name']}: Dependencies - {func['All Called Functions']}")

            raise Exception("Infinite loop detected due to unresolvable dependencies.")

    return json.dumps(sorted_functions, indent=4)

# Main execution
cobol_file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'
reserved_words_file_path = 'C:\\Users\\sashah\\Downloads\\cobol_reserved_words.txt'

cobol_lines = read_cobol_file(cobol_file_path)

reserved_words = read_reserved_words(reserved_words_file_path)
functions = find_functions(cobol_lines, reserved_words)

# Process function code
function_code_data = get_function_code(cobol_lines, functions, reserved_words)
print(function_code_data)
# Build dependency graph
graph = build_dependency_graph(function_code_data)

# Get function code with all called functions
function_code_data_with_all_calls = get_function_code_with_all_calls(cobol_lines, functions, reserved_words, graph)

# Print the extended JSON structure
#extended_json_output = json.dumps(function_code_data_with_all_calls, indent=4)
#print("Extended JSON with All Called Functions:\n", extended_json_output)

# Convert JSON string to dictionary
#e_json_output = json.loads(extended_json_output)

# Initialize an empty set to store unique values
#unique_called_functions = set()

# Iterate over each dictionary in the list
#for item in e_json_output:
    # Check if "All Called Functions" key exists
#    if "All Called Functions" in item:
        # Add all elements from this list to the set (which ensures uniqueness)
#        unique_called_functions.update(item["All Called Functions"])

# Convert the set to a list to get a list of unique values
#unique_called_functions_list = list(unique_called_functions)
#print("Unique Functions:")
#print(unique_called_functions_list)
# unique_called_functions_list now contains all unique values across the "All Called Functions" lists


#sorted_json = sort_functions(extended_json_output)
#print("Sorted JSON with All Called Functions:\n", sorted_json)
