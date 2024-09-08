from flask import Flask, render_template_string, request
import json
import os
import re
import ast
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'py', 'cbl', 'cob'}
CONFIG_FILE_PATH = r'C:\Users\sashah\PycharmProjects\pythonProject2\config.json'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class FunctionCodeExtractor(ast.NodeVisitor):
    def __init__(self, source_code):
        self.source_code = source_code
        self.functions_code = []
        self.functions_flow = []
        # Use a set to track lines that are part of function definitions
        self.function_lines = set()


    def visit_FunctionDef(self, node):
        # Mark lines belonging to this function, including decorators
        for lineno in range(node.lineno, node.end_lineno + 1):
            self.function_lines.add(lineno)
        # Capture the function's code
        function_code = "\n".join(self.source_code.splitlines()[node.lineno - 1:node.end_lineno])
        self.functions_code.append({
            "Function Name": node.name,
            "Source Code": function_code
        })
        # Continue traversing the AST
        self.generic_visit(node)


def extract_functions_python(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()

    # Parse the source code into an AST and extract functions
    tree = ast.parse(source_code)
    extractor = FunctionCodeExtractor(source_code)
    extractor.visit(tree)

    # Identify top-level code by excluding lines that are part of functions
    top_level_code_lines = [line for i, line in enumerate(source_code.splitlines(), start=1)
                            if i not in extractor.function_lines]

    # Combine top-level lines into a single string
    main_block_code = "\n".join(top_level_code_lines).strip()

    # Optionally, append this main block to the functions_code list or handle separately
    if main_block_code:
        extractor.functions_code.append({
            "Function Name": "MAIN program",
            "Source Code": main_block_code
        })

    return extractor.functions_code


def extract_methods_dotnet(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        source_code = file.read()
    """
    Extracts methods from C# source code using a refined regex.
    This function aims to handle a broader range of C# method syntax.
    """
    methods_code = []
    # Updated regex pattern to more accurately match method headers
    # This pattern looks for optional access modifiers, the optional static keyword, return types, and then the method
    # name followed by parameters.
    method_pattern = re.compile(r'\b(public|private|protected|internal)?\s*(static)?\s+[\w<>]+\s+(\w+)\s*\((.*?)\)\s*{')

    matches = method_pattern.finditer(source_code)

    for match in matches:
        method_start = match.start()
        method_end = match.end()
        brace_count = 1
        i = method_end

        while i < len(source_code) and brace_count > 0:
            if source_code[i] == '{':
                brace_count += 1
            elif source_code[i] == '}':
                brace_count -= 1
            i += 1

        method_body_end = i
        method_code = source_code[method_start:method_body_end].strip()
        method_name = match.group(3)  # Correctly capture the method name

        methods_code.append({
            "Function Name": method_name,
            "Source Code": method_code
        })

    return methods_code


class CodeAnalyzer:
    def __init__(self, file_path, language_config):
        self.file_path = file_path
        self.language_config = json.loads(language_config)
        self.reserved_words = self.read_reserved_words()
        self.code_lines = self.process_code_file()
        self.functions = self.find_functions()

        # Choose the correct method to get function code based on language
        if self.language_config['name'].lower() == 'python':
            self.functions_code = self.get_function_code_python()
        elif self.language_config['name'].lower() == 'cobol':
            self.functions_code = self.get_function_code_cobol()
            self.functions_flow = self.get_function_code_flow()
        elif self.language_config['name'].lower() == '.net':
            self.functions_code = self.get_function_code_dotnet()
        else:
            self.functions_code = []

    def read_code_file(self):
        with open(self.file_path, 'r') as file:
            return file.read()

    def process_code_file(self):
        raw_code = self.read_code_file()
        if start_keyword := self.language_config.get("code_start_keyword"):
            raw_code = raw_code.split(start_keyword, 1)[-1]
        return self.process_multiline_statements(raw_code) if self.language_config.get(
            "is_multiline_statement") else raw_code.splitlines()

    def process_multiline_statements(self, code):
        # Process according to COBOL multi-line statement rules, adaptable for other languages
        processed_lines, current_line = [], ""
        for raw_line in code.splitlines():
            stripped_line = raw_line.rstrip()
            start_pos = 7 - 1
            for marker in self.language_config.get("comment_markers", []):
                start_pos = marker["index"] - 1

            if len(raw_line.rstrip()) <= start_pos:
                continue
            if self.is_comment_line(raw_line):
                stripped_line = stripped_line.replace(".", "")
                current_line += " " + stripped_line + "\n" if current_line else stripped_line + "\n"
                processed_lines.append(current_line)
                current_line = ""
            else:

                current_line += " " + stripped_line + "\n" if current_line else stripped_line + "\n"
                words = stripped_line.strip().upper().split()

                #if '.' in stripped_line or words[0].split('.')[0] in self.reserved_words:
                if words[-1].endswith('.'):

                    processed_lines.append(current_line)
                    current_line = ""

        return processed_lines

    def is_comment_line(self, line):
        for marker in self.language_config.get("comment_markers", []):
            if marker["position"] == "start" and line.lstrip().startswith(marker["symbol"]):
                return True
            elif marker["position"] == "fixed" and len(line) >= marker["index"] and line[marker["index"] - 1] == \
                    marker[
                        "symbol"]:
                return True
        return False

    def read_reserved_words(self):
        reserved_words_file = self.language_config.get("reserved_words_file")
        if reserved_words_file:
            with open(reserved_words_file, 'r') as file:
                return set(word.strip() for word in file)

    def find_functions(self):
        method_name = f"find_functions_{self.language_config['name']}"
        return getattr(self, method_name, self.find_functions_generic)()

    def find_functions_generic(self):
        # Generic function finding logic (simplified example)
        functions = []
        for line in self.code_lines:
            if not self.is_comment_line(line):
                functions.extend(re.findall(self.language_config["function_declaration_pattern"], line))
        return functions

    def find_functions_cobol(self):
        functions = []
        count = 1
        for line in self.code_lines:
            if self.is_comment_line(line):
                continue
            start_pos = 7
            for marker in self.language_config.get("comment_markers", []):
                start_pos = marker["index"]

            trimmed_line = line[start_pos:].strip().upper()
            words = trimmed_line.split()
            if "MOVE-ATEKEY" in trimmed_line:
                print("line")
                print(line)
                print("start_pos")
                print(start_pos)
                print("trimmed_line")
                print(trimmed_line)
                print("trimmed_line-1")
                print(line[start_pos:])
                print("word_without_dot")
                print(words[-1][:-1])
            # Check if there is only one word in the line and it ends with "."
            if len(words) == 1 and words[-1].endswith('.'):
                # Remove the trailing "." before checking against reserved words
                word_without_dot = words[-1][:-1]
                if word_without_dot not in self.reserved_words:
                    functions.append(words[-1])
        return functions

    def get_function_code_cobol(self):
        functions_code = []
        current_function = None
        current_code = ''
        start_pos = 7
        for marker in self.language_config.get("comment_markers", []):
            start_pos = marker["index"]
        for line in self.code_lines:
            if self.is_comment_line(line):  # comment lines
                if current_code:
                    current_code += line.rstrip() + '\r\n'  # Keep the original line format
                continue

            trimmed_line = line[start_pos:].upper().strip()
            if any(func == trimmed_line for func in self.functions):
                if current_function:
                    functions_code.append({
                        "Function Name": current_function,
                        "Source Code": current_code.strip(),
                    })
                #current_function = line.strip()[:-1]
                current_function = trimmed_line.strip()[:-1]
                current_code = ''
            else:
                current_code += line.rstrip() + '\r\n'  # Keep the original line format
                # Pass current_function as an argument

        if current_function:
            functions_code.append({
                "Function Name": current_function,
                "Source Code": current_code.strip(),
            })
            current_code = ''

        return functions_code

    def get_function_code_flow(self):
        functions_flow = []
        current_function = None
        current_code_flow = ''
        start_pos = 7
        for marker in self.language_config.get("comment_markers", []):
            start_pos = marker["index"]

        raw_code = ""
        with open(self.file_path, 'r') as file:
            raw_code = file.read()

        if start_keyword := self.language_config.get("code_start_keyword"):
            raw_code = raw_code.split(start_keyword, 1)[-1]

        raw_code = raw_code.splitlines()

        for line in raw_code:
            if self.is_comment_line(line):  # comment lines
                #if current_code_flow:
                #    current_code_flow += line.rstrip() + '\r\n'  # Keep the original line format
                continue

            trimmed_line = line[start_pos:].upper().strip()
            if any(func == trimmed_line for func in self.functions):
                if current_function and current_code_flow:
                    if not current_code_flow:
                        current_code_flow = "<NONE>"
                    functions_flow.append({
                        "Function Name": current_function,
                        "Code Flow": current_code_flow.strip(),
                    })
                current_function = trimmed_line.strip()[:-1]
                current_code_flow = ''
            else:
                if "PERFORM " in trimmed_line or "CALL " in trimmed_line or "GO TO " in trimmed_line:
                    current_code_flow += trimmed_line.rstrip() + '\r\n'  # Keep the original line format

        if current_function and current_code_flow:
            if not current_code_flow:
                current_code_flow = "<NONE>"
            functions_flow.append({
                "Function Name": current_function,
                "Code Flow": current_code_flow.strip(),
            })
            current_code_flow = ''

        return functions_flow

    # Python-specific function finder
    def find_functions_python(self):
        # Find functions in Python code using the pattern from the configuration
        function_pattern = self.language_config.get("function_declaration_pattern")
        if not function_pattern:
            return []  # Return an empty list if the pattern is not defined
        functions = []
        for line in self.code_lines:
            matches = re.findall(function_pattern, line)
            functions.extend(matches)
        return functions

    def get_function_code_python(self):
        return extract_functions_python(self.file_path)

    def get_function_code_dotnet(self):
        return extract_methods_dotnet(self.file_path)

    pass

@app.route('/', methods=['GET', 'POST'])
def form():
    message = ""
    functions_list = []
    functions_code = []
    functions_flow = []
    if request.method == 'POST':
        file = request.files['fileUpload']
        file_path_input = request.form.get('filePath')  # Manually entered file path
        file_type = request.form.get('fileType').lower()

        # If a file is uploaded
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_file_path)  # Save the uploaded file

            # Use the manually entered path if provided, else use the upload path
            if file_path_input:
                full_file_path = os.path.join(file_path_input, filename)

            # Load the language configuration
            with open(CONFIG_FILE_PATH, 'r') as config_file:
                config = json.load(config_file)
            language_config = json.dumps(config.get(file_type))

            if language_config:
                # Initialize and use the CodeAnalyzer
                analyzer = CodeAnalyzer(full_file_path, language_config)
                functions_list = analyzer.functions  # Get function names
                functions_code = analyzer.functions_code  # Get code for functions
                functions_flow = analyzer.functions_flow  # Get code for functions
                message = f"Functions and code found in {filename}:"
            else:
                message = "Language configuration not found."
        else:
            message = "Invalid file type or no file selected."

    # HTML form with CSS styling, including file path input
    HTML_FORM = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Convert Code to Design</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container, .output { background-color: #f2f2f2; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            input, select, button { margin-top: 10px; padding: 8px; border-radius: 5px; border: 1px solid #ccc; }
            button { background-color: #4CAF50; color: white; cursor: pointer; }
            button:hover { background-color: #45a049; }
            .output { font-weight: bold; }
            ul { list-style-type: none; padding: 0; }
            li { margin: 5px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Convert Code to Design</h2>
            <form method="post" enctype="multipart/form-data">
                <div>
                    <label>File path (optional):</label>
                    <input type="text" name="filePath" placeholder="Manually enter file path">
                </div>
                <div>
                    <label>Select file:</label>
                    <input type="file" name="fileUpload">
                </div>
                <div>
                    <label>Choose the file type:</label>
                    <select name="fileType">
                        <option value="Python">Python</option>
                        <option value="COBOL">COBOL</option>
                        <option value=".NET">.NET</option>
                    </select>
                </div>
                <div>
                    <button type="submit">Analyze</button>
                </div>
            </form>
        </div>
        <div class="output">
            <h3>{{ message }}</h3>
            {% if functions_flow %}
                <ul>
                {% for func in functions_flow %}
                    <li>
                        <strong>Function Name:</strong> {{ func["Function Name"] }}
                        <br>
                        <strong>Code Flow:</strong>
                        <pre>{{ func["Code Flow"] }}</pre>
                    </li>
                {% endfor %}
                </ul>
            {% else %}
                <label>Nothing found</label>
            {% endif %}
        </div>
    </body>
    </html>
    '''
    return render_template_string(HTML_FORM, message=message, functions_list=functions_list,
                                  functions_code=functions_code, functions_flow=functions_flow)


if __name__ == '__main__':
    app.run(debug=True)
