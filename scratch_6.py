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
            # Ignore 'PERFORM VARYING', 'PERFORM ... TIMES', 'PERFORM ... UNTIL', and numeric values
            if any(keyword in tokens or keyword.isdigit() for keyword in ["VARYING", "TIMES", "UNTIL"]):
                continue
            if len(tokens) > 1:
                target = tokens[1].split('.')[0]
                if not target.isdigit():
                    perform_targets.add(target)
    return perform_targets

def find_section_or_paragraph_code(cobol_lines, targets):
    sections = {}
    remaining_lines = []
    current_section = None
    current_content = []
    called_sections = set()
    for line in cobol_lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped.split()[0].rstrip('.') in targets:
            if current_section:
                sections[current_section] = (current_content, called_sections)
                current_content = []
                called_sections = set()
            current_section = line_stripped.split()[0].rstrip('.')
        elif current_section:
            current_content.append(line)
            if 'PERFORM' in line:
                tokens = line.strip().split()
                if len(tokens) > 1 and tokens[1].upper() != 'UNTIL':
                    target = tokens[1].split('.')[0]
                    called_sections.add(target)
        else:
            remaining_lines.append(line)

    if current_section:
        sections[current_section] = (current_content, called_sections)

    return sections, remaining_lines

def build_full_dependency_map(sections):
    direct_dependencies = {section: calls for section, (_, calls) in sections.items()}

    def find_all_dependencies(section, origin, all_deps=set()):
        for dep in direct_dependencies.get(section, []):
            if dep != origin and dep not in all_deps:
                all_deps.add(dep)
                find_all_dependencies(dep, origin, all_deps)
        return all_deps

    full_dependencies = {}
    for section in sections:
        full_dependencies[section] = find_all_dependencies(section, section)

    return full_dependencies

def process_sections(sections, full_dependencies):
    processed = []
    to_process = set(sections.keys())
    unresolved = set()  # To keep track of sections with unresolved dependencies

    while to_process:
        progress = False
        for section in list(to_process):
            if full_dependencies[section].issubset(processed):
                print(f"Processing section: {section}")
                processed.append(section)
                to_process.remove(section)
                progress = True
                break
            else:
                unresolved.add(section)

        if not progress:  # If no progress, there might be circular dependencies
            print("Warning: Possible circular dependencies detected among the following sections:")
            print(unresolved)
            processed.extend(unresolved)
            break

    return processed

def main():
    file_path = 'C:\\Users\\sashah\\Downloads\\RP0326.txt'  # Your COBOL file path
    cobol_lines = read_cobol_file(file_path)
    preprocessed_lines = preprocess_cobol_lines(cobol_lines)
    perform_targets = extract_perform_targets(preprocessed_lines)
    sections, remaining_proc_div = find_section_or_paragraph_code(preprocessed_lines, perform_targets)

    full_dependencies = build_full_dependency_map(sections)
    ordered_sections = process_sections(sections, full_dependencies)

    for section in ordered_sections:
        print(f"Function Name: {section}")
        print("".join(sections[section][0]))

    print("PROCEDURE DIVISION:")
    print("".join(remaining_proc_div))

if __name__ == "__main__":
    main()
