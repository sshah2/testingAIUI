from flask import Flask, render_template_string, request
import json
import re
import os
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


# Placeholder for your CodeAnalyzer class here
class CodeAnalyzer:
    # Your CodeAnalyzer implementation
    pass


@app.route('/', methods=['GET', 'POST'])
def form():
    message = ""
    functions_list = []
    if request.method == 'POST':
        file = request.files['fileUpload']
        file_type = request.form.get('fileType')
        file_path_input = request.form.get('filePath')  # Retrieve manually entered file path
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Placeholder: Load language config and analyze file
            # This is where you would use CodeAnalyzer with file_path and/or file_path_input

            message = f"Functions found in {filename}:"
            # Placeholder: Append function names to functions_list
        else:
            message = "Invalid file type or no file selected."


    # HTML template with CSS and file path input
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
            {{ message }}
            {% if functions_list %}
                <ul>
                {% for func in functions_list %}
                    <li>{{ func }}</li>
                {% endfor %}
                </ul>
            {% endif %}
        </div>
    </body>
    </html>
    '''

    return render_template_string(HTML_FORM, message=message, functions_list=functions_list)


if __name__ == '__main__':
    app.run(debug=True)
