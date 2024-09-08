from flask import Flask, render_template, request, redirect, url_for
import openai
import os
import json
from pydantic import BaseModel, Field, field_validator
from typing import List
from instructor import OpenAISchema
from datetime import date, datetime

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/")
def index():
    # The homepage will display options to perform actions similar to Streamlit sidebar
    return render_template('index.html')

@app.route("/apply-program", methods=['GET', 'POST'])
def apply_program():
    if request.method == 'POST':
        # Extract data from form submission
        data = request.form
        # Here you would call the OpenAI API with the data
        # and implement your business logic
        return redirect(url_for('results'))
    return render_template('apply_program.html')

@app.route("/get-case", methods=['GET', 'POST'])
def get_case():
    if request.method == 'POST':
        # Extract data from form and handle the action
        return redirect(url_for('results'))
    return render_template('get_case.html')

@app.route("/results")
def results():
    # This function would display results of an action
    return render_template('results.html')

if __name__ == '__main__':
    app.run(debug=True)
```

**templates/index.html**: Home page template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Service Application</title>
</head>
<body>
    <h1>State of Wellbeing's Self-Service Application</h1>
    <p>Welcome to the State of Wellbeing's Self-Service Application. Choose an action:</p>
    <ul>
        <li><a href="{{ url_for('apply_program') }}">Apply for a Program</a></li>
        <li><a href="{{ url_for('get_case') }}">Get Case Details</a></li>
        <!-- Add more actions as necessary -->
    </ul>
</body>
</html>
```

h**templates/apply_program.html**: Apply for a Program template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Apply for a Program</title>
</head>
<body>
    <h1>Apply for a Program</h1>
    <form method="post" action="{{ url_for('apply_program') }}">
        <!-- Add form inputs as necessary -->
        <input type="text" name="program_name" placeholder="Program Name" required>
        <input type="submit" value="Apply">
    </form>
</body>
</html>
```

**templates/get_case.html**: Get Case template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Get Case</title>
</head>
<body>
    <h1>Get Case Details</h1>
    <form method="post" action="{{ url_for('get_case') }}">
        <!-- Add form inputs as necessary -->
        <input type="text" name="case_id" placeholder="Case ID" required>
        <input type="submit" value="Get Case">
    </form>
</body>
</html>
```

**templates/results.html**: Results template

```html
<!DOCTYPE html>
<html>
<head>
    <title>Results</title>
</head>
<body>
    <h1>Results</h1>
    <!-- Display results here -->
</body>
</html>
```

Run the application by setting the environment variables `FLASK_APP=app.py` and optionally `FLASK_ENV=development` for development, then execute the command `flask run` in your terminal.