import re
import os
import copy

def create_function_files(processed_functions, function_codes):
    output_directory = "C:\\Users\\sashah\\Desktop\\New Principal\\New Role\\GenAI\\DMV"

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for function in processed_functions:
        function_name, _, all_called_functions, external_calls = function
        file_path = os.path.join(output_directory, f"{function_name}.txt")

        with open(file_path, 'w') as file:
            file.write("Function Code:\n")
            file.write(function_codes.get(function_name, "Code not found") + "\n\n")

            file.write("All Called Functions:\n")
            if all_called_functions:
                file.write('\n'.join(all_called_functions) + "\n\n")
            else:
                file.write("NONE\n\n")

            file.write("External Calls:\n")
            if external_calls:
                file.write('\n'.join(external_calls) + "\n\n")
            else:
                file.write("NONE\n\n")

def extract_function_code_v5(cobol_file, function_names_file):
    # Read the function names file
    with open(function_names_file, 'r') as file:
        functions = file.read().splitlines()

    # Dictionary to store function code
    function_code_dict = {fn: "" for fn in functions}

    # Read the COBOL code file
    with open(cobol_file, 'r') as file:
        cobol_code_lines = file.readlines()

    for i, function_name in enumerate(functions):
        next_function = functions[i + 1] if i + 1 < len(functions) else None
        capturing = False
        for line in cobol_code_lines:
            if re.match(r"^\s*\*", line):  # Skip commented lines
                continue

            # Check for function name followed by a period, ensuring it's not part of a PERFORM or GO TO statement
            if f"{function_name}." in line and not any(kw in line.split(f"{function_name}.")[0].split() for kw in ['PERFORM', 'GO', 'TO']):
                capturing = True
                function_code_dict[function_name] += line
                continue

            if capturing:
                if next_function and f"{next_function}." in line and not any(kw in line.split(f"{next_function}.")[0].split() for kw in ['PERFORM', 'GO', 'TO']):
                    break
                function_code_dict[function_name] += line

    # Debug: Print the extracted code for a specific function (e.g., '6100-FINAL-COUNTS')
    #debug_function = 'PROCEDURE DIVISION'
    #if debug_function in function_code_dict:
    #    print(f"Debug: Extracted code for {debug_function}:\n")
    #    print(function_code_dict[debug_function])

    return function_code_dict

def extract_called_functions_for_co_dependent(co_dependent_functions, function_codes, reserved_words):
    called_functions_dict = {}

    for function_name in co_dependent_functions:
        called_functions = extract_called_functions(function_codes[function_name], reserved_words, function_name)
        called_functions_dict[function_name] = called_functions

    return called_functions_dict

def extract_called_functions(function_code, reserved_words, function_name):
    called_functions = set()

    for line in function_code.splitlines():
        # Only consider code starting from the 8th character
        code_line = line[7:]

        # Check if the line is a comment
        if len(line) >= 7 and line[6] in ['*', '/']:
            continue

        # Split the line into words to check for specific patterns
        words = code_line.strip().split()

        # Check for 'PERFORM <value> TIMES' pattern
        if len(words) == 3 and words[0].upper() == 'PERFORM' and words[2].upper() == 'TIMES':
            continue

        # Check for 'PERFORM <function> <value> TIMES' and similar patterns
        if len(words) > 3 and words[0].upper() == 'PERFORM' and words[-1].upper() == 'TIMES':
            func = words[1]
            if func not in reserved_words and func.upper() != function_name:
                called_functions.add(func.upper())
            continue

        # Regular PERFORM statement
        pattern = r'PERFORM\s+([A-Z0-9-]+)'
        found = re.findall(pattern, code_line, re.IGNORECASE)
        for func in found:
            if func not in reserved_words and not func.isdigit() and func.upper() != function_name:
                called_functions.add(func.upper())

    return list(called_functions)

def extract_external_calls(function_code, reserved_words):
    external_calls = set()

    for line in function_code.splitlines():
        code_line = line[7:]

        if len(line) >= 7 and line[6] in ['*', '/']:
            continue

        pattern = r'CALL\s+[\'"]([A-Z0-9-]+)[\'"]'
        match = re.search(pattern, code_line, re.IGNORECASE)

        if match:
            func = match.group(1)
            if func not in reserved_words:
                external_calls.add(func.upper())

    return list(external_calls)

def read_reserved_words(file_path):
    with open(file_path, 'r') as file:
        words = {line.strip().upper() for line in file.readlines()}
    return words

def process_functions(function_codes, reserved_words):
    processed_functions = []

    for function_name, code in function_codes.items():
        called_functions = extract_called_functions(code, reserved_words, function_name)
        external_calls = extract_external_calls(code, reserved_words)
        processed_functions.append([function_name, called_functions, called_functions, external_calls])

    return processed_functions

def sort_and_flag_functions(processed_functions):
    processed_flags = {func[0]: 'N' for func in processed_functions}
    exceptions = []
    sorted_functions = []

    def all_processed(called_functions):
        return all(processed_flags.get(func, 'N') == 'Y' for func in called_functions)

    while processed_functions:
        progress_made = False

        for function in processed_functions[:]:
            function_name, called_functions, _, _ = function

            if not called_functions or all_processed(called_functions):
                processed_flags[function_name] = 'Y'
                sorted_functions.append(function)
                processed_functions.remove(function)
                progress_made = True
            elif function_name in called_functions:
                exceptions.append(function_name)
                processed_flags[function_name] = 'Y'
                sorted_functions.append(function)
                processed_functions.remove(function)

        if not progress_made:
            for function in processed_functions:
                function_name = function[0]
                if function_name not in exceptions:
                    exceptions.append(function_name)
                processed_flags[function_name] = 'Y'
                sorted_functions.append(function)
            break

    return sorted_functions, exceptions, processed_flags

def main():
    cobol_file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'
    function_names_file_path = 'C:\\Users\\sashah\\Downloads\\function_names.txt'
    reserved_words_file_path = 'C:\\Users\\sashah\\Downloads\\cobol_reserved_words.txt'

    reserved_words = read_reserved_words(reserved_words_file_path)

    function_codes = extract_function_code_v5(cobol_file_path, function_names_file_path)

    processed_functions = process_functions(function_codes, reserved_words)

    # Create a copy of processed_functions
    processed_functions_copy = copy.deepcopy(processed_functions)

    # Use the copy for sorting and flagging
    sorted_functions, exceptions, processed_flags = sort_and_flag_functions(processed_functions_copy)

    # Now use the original processed_functions for creating files
    create_function_files(processed_functions, function_codes)

    for function in sorted_functions:
        function_name, called_functions, all_called_functions, external_calls = function
        print(f"Function Name: {function_name}, Processed: {processed_flags[function_name]}")
        print("Called Functions:", called_functions)
        print("All Called Functions:", all_called_functions)
        print("External Calls:", external_calls)
        print()

    if exceptions:
        print("Exceptions (Co-dependent functions):", exceptions)

    # Assuming the list of co-dependent functions
    #co_dependent_functions = ['0100-MAIN-LOGIC', '0300-PROCESS-RECORD', '0410-READ-RECORD', '0420-PROCESS-RECORD',
    #                          '0425-RETRIEVE-TYPE-LIC', '0430-PROCESS-END-OF-FILE', '0460-READ-VRM-DPP',
    #                          '1000-PROCESS-MSTR', '1050-CHECK-SUBRECORDS', '2400-PROCESS-W-SUBREC', '4010-INVALID-TL',
    #                          '6080-PRINT-BYPASS-RPT']

    # Extract called functions for co-dependent functions
    #called_functions_co_dependent = extract_called_functions_for_co_dependent(co_dependent_functions, function_codes,
    #                                                                          reserved_words)

    # Print the called functions for each co-dependent function
    #for function_name, called_functions in called_functions_co_dependent.items():
    #    print(f"Function Name: {function_name}")
    #    print("Called Functions:", called_functions)
    #    print()

if __name__ == "__main__":
    main()
