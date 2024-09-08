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

    for section, content in sections.items():
        print(f"Function Name: {section}")
        print("".join(content))

        #print("\n")

    print("PROCEDURE DIVISION:")
    print("".join(remaining_proc_div))

if __name__ == "__main__":
    main()
