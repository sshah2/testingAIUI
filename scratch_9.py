import re

def extract_function_code_v5(cobol_file, function_names):
    # Read the COBOL code file
    with open(cobol_file, 'r') as file:
        cobol_code = file.read()

    # Read the function names file
    with open(function_names, 'r') as file:
        functions = file.read().splitlines()

    # Dictionary to store function code
    function_code_dict = {}

    # Start index for the next search
    start_index = 0

    # Iterate through the functions to find and extract their code
    for i in range(len(functions) - 1):
        start_function = functions[i] + '.'
        end_function = functions[i + 1] + '.'

        # Using regex to find the code block between two functions
        pattern = re.escape(start_function) + r'(.*?)' + re.escape(end_function)
        match = re.search(pattern, cobol_code[start_index:], re.DOTALL)

        if match:
            # Extract the code for the current function
            code = match.group(1).strip()
            function_code_dict[functions[i]] = code
            # Update the start index for the next search
            start_index += match.end()

    return function_code_dict

def extract_called_functions(function_code, reserved_words):
    """
    Extract all called functions (PERFORM statements) within a given function's code,
    excluding any that are reserved words or numeric literals.
    """
    # Regular expression pattern to find PERFORM statements
    # This pattern also handles 'PERFORM para_1_name THRU para_2_name' cases
    pattern = r'PERFORM\s+([A-Z0-9-]+)(?:\s+THRU\s+([A-Z0-9-]+))?'
    found = re.findall(pattern, function_code)

    # Flatten the list and remove duplicates, reserved words, and numeric literals
    called_functions = set()
    for funcs in found:
        for func in funcs:
            if func and func not in reserved_words and not func.isdigit():
                called_functions.add(func)

    return list(called_functions)

def read_reserved_words(file_path):
    """
    Read a file containing reserved words and return them as a set.
    """
    with open(file_path, 'r') as file:
        words = {line.strip() for line in file.readlines()}
    return words

def process_functions(function_codes, reserved_words):
    """
    Process each function to find all the called functions within it.
    """
    processed_functions = []

    for function_name, code in function_codes.items():
        called_functions = extract_called_functions(code, reserved_words)
        # For now, we keep the 3rd element the same as the 2nd
        processed_functions.append([function_name, called_functions, called_functions])

    return processed_functions

def main():
    # File paths
    cobol_file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'
    function_names_file_path = 'C:\\Users\\sashah\\Downloads\\function_names.txt'
    reserved_words_file_path = 'C:\\Users\\sashah\\Downloads\\cobol_reserved_words.txt'

    # Read the reserved words
    reserved_words = read_reserved_words(reserved_words_file_path)

    # Extract function codes
    function_codes = extract_function_code_v5(cobol_file_path, function_names_file_path)

    # Process the functions to find called functions
    processed_functions = process_functions(function_codes, reserved_words)

    # Print the results
    for function in processed_functions:
        function_name, called_functions, _ = function
        print(f"Function Name: {function_name}")
        print("Called Functions:", called_functions)
        print()

if __name__ == "__main__":
    main()
