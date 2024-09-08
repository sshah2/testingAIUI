import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
from tkcalendar import DateEntry
import us  # Requires installing the `us` package for getting US states

# Load the data from the Excel file
file_path = r'C:\Users\sashah\Desktop\SSP Structure.xlsx'
data = pd.read_excel(file_path, sheet_name='Metadata')

# Define picklist values
PICKLIST_VALUES = {
    "APPTYPE": ["Regular", "Mail-In", "Fax", "Other"],
    "GENDER": ["Male", "Female", "Unknown"],
    "STATE": [state.name for state in us.states.STATES],
    "PAYFREQ": ["Daily", "Weekly", "Monthly"]
}

# Dynamically create the parent-child map based on metadata
parent_child_map = {key: [] for key in data['Section Key'].unique() if pd.notna(key)}


# Function to dynamically generate a section key based on available fields
def generate_section_key(fields, section_data):
    key_fields = section_data[section_data['Mandatory?'] == 'Y']['Field Name'].values
    valid_keys = [fields[field_name]['entry'].get() for field_name in key_fields if
                  field_name in fields and fields[field_name]['entry'].get()]

    print(f"Key Fields: {key_fields}")
    print(f"Valid Keys: {valid_keys}")

    generated_id = ', '.join(valid_keys)
    return generated_id if generated_id else 'Unknown'


# Function to validate and submit the form
def submit_form(fields, section_key, section_data, root, repeating_fields=None, parent_id=None):
    if repeating_fields is None:
        repeating_fields = []

    # Initialize generated_id
    generated_id = None

    # Process non-repeating fields
    entry_values = {}
    for field_name, field_value in fields.items():
        entry_value = field_value.get('entry').get()
        entry_values[field_name] = entry_value
        if field_value.get('mandatory') and not entry_value:
            messagebox.showerror("Validation Error", f"The field '{field_name}' is mandatory.")
            return

        validation = field_value.get('validation')
        if validation == 'NO_SPL_CHAR' and any(char in entry_value for char in '$%$%'):
            messagebox.showerror("Validation Error", f"{field_name}: {field_value.get('validation_msg')}")
            return

    # For repeating fields, dynamically generate a Section Key based on available fields
    if isinstance(repeating_fields, ttk.Treeview):
        for item in repeating_fields.get_children():
            values = repeating_fields.item(item, 'values')
            if len(values) > 0:
                generated_id = ', '.join(str(v) for v in values if v)
                if not generated_id:
                    messagebox.showerror("Validation Error",
                                         "All required fields must be filled to generate the Section Key.")
                    return
                print(f"Generated Section Key ({section_key}): {generated_id}")
                parent_child_map[section_key].append(generated_id)
    else:
        # Handle non-repeating sections: dynamically generate an ID
        generated_id = generate_section_key(fields, section_data)
        if generated_id == 'Unknown':
            messagebox.showerror("Validation Error", "All required fields must be filled to generate the Section Key.")
            return
        print(f"Generated Section Key ({section_key}): {generated_id}")
        parent_child_map[section_key].append(generated_id)

    # Debug: Print entry values and parent-child map after submission
    print(f"Submitted values: {entry_values}")
    print(f"Current parent-child map: {parent_child_map}")

    messagebox.showinfo("Form Submitted", f"Form submitted with {section_key}")

    # Close the current window and move to the next screen
    try:
        root.destroy()
    except tk.TclError:
        pass  # Handle the case where the window has already been closed


# Function to add a row in the Treeview for repeating fields
def add_tree_row(tree, columns):
    values = []
    for col in columns:
        if col['type'] == 'Picklist':
            value = col['variable'].get()
        elif col['type'] == 'Date':
            value = col['entry'].get()
        else:
            value = col['entry'].get()
        values.append(value)
    tree.insert("", "end", values=values)
    for col in columns:
        if col['type'] in ['Char', 'Date']:
            col['entry'].delete(0, tk.END)


# Function to create a form based on a section and its fields
def create_form(section_data, root, parent_id=None, parent_info=None):
    fields = {}
    section_key = section_data.iloc[0]['Section Key']

    if parent_info:
        tk.Label(root, text=f"Capturing data for: {parent_info}", font=("Helvetica", 12, "bold")).pack(pady=10)

    if section_data.iloc[0]['Single/Repeating'] == 'Repeating':
        columns = []
        valid_section_data = section_data.dropna(subset=['Field Label'])  # Remove NaN Field Labels
        field_labels = valid_section_data['Field Label'].tolist()

        tree = ttk.Treeview(root, columns=field_labels, show="headings", height=10)
        for index, label in enumerate(field_labels):
            tree.heading(index, text=label)
            tree.column(index, anchor="center")
        tree.pack(fill="both", expand=True)

        input_frame = tk.Frame(root)
        input_frame.pack(fill="x")

        for index, row in valid_section_data.iterrows():
            field_type = row['Field Type']
            picklist_name = row['Picklist Name']  # Get the Picklist Name from the appropriate column
            mandatory = row['Mandatory?'] == 'Y'  # Check if the field is mandatory

            if field_type == 'Picklist':
                options = PICKLIST_VALUES.get(picklist_name, ["No Options Available"])

                variable = tk.StringVar(input_frame)
                variable.set(options[0])  # Set first option
                entry = tk.OptionMenu(input_frame, variable, *options)
                entry.config(bg="white")  # Set background color to white
                entry.grid(row=0, column=index, padx=5, pady=5)
                columns.append({'entry': variable, 'variable': variable, 'type': 'Picklist'})
            elif field_type == 'Date':
                entry = DateEntry(input_frame, width=12, background='darkblue', foreground='white', borderwidth=2)
                entry.grid(row=0, column=index, padx=5, pady=5)
                columns.append({'entry': entry, 'type': 'Date'})
            else:
                entry = tk.Entry(input_frame)
                entry.grid(row=0, column=index, padx=5, pady=5)
                columns.append({'entry': entry, 'type': 'Char'})

        tk.Button(input_frame, text="Add Row", command=lambda: add_tree_row(tree, columns)).grid(row=0,
                                                                                                 column=len(columns),
                                                                                                 padx=5, pady=5)
        repeating_fields = tree
    else:
        for index, row in section_data.iterrows():
            field_label = row['Field Label']
            field_name = row['Field Name']
            picklist_name = row['Picklist Name']  # Get the Picklist Name from the appropriate column
            field_type = row['Field Type']
            mandatory = row['Mandatory?'] == 'Y'  # Check if the field is mandatory

            if pd.notna(field_label) and pd.notna(field_name):
                frame = tk.Frame(root)
                frame.pack(fill="x")

                # Add red asterisk (*) for mandatory fields
                if mandatory:
                    label_frame = tk.Frame(frame)
                    label_frame.pack(side="left")
                    tk.Label(label_frame, text="*", fg="red").pack(side="left")
                    tk.Label(label_frame, text=field_label, width=20, anchor="w").pack(side="left")
                else:
                    tk.Label(frame, text=field_label, width=20, anchor="w").pack(side="left")

                if field_type == 'Picklist':
                    options = PICKLIST_VALUES.get(picklist_name, ["No Options Available"])

                    variable = tk.StringVar(frame)
                    variable.set(options[0])  # Set first option
                    entry = tk.OptionMenu(frame, variable, *options)
                    entry.config(bg="white")  # Set background color to white
                    entry.pack(side="left", fill="x", expand=True)
                    fields[field_name] = {
                        'entry': variable,
                        'mandatory': mandatory,
                        'validation': row['Field Validation'],
                        'validation_msg': row['Validation Message']
                    }
                elif field_type == 'Date':
                    entry = DateEntry(frame, width=20, background='darkblue', foreground='white', borderwidth=2)
                    entry.pack(side="left", fill="x", expand=True)
                    fields[field_name] = {
                        'entry': entry,
                        'mandatory': mandatory,
                        'validation': row['Field Validation'],
                        'validation_msg': row['Validation Message']
                    }
                else:
                    entry = tk.Entry(frame)
                    entry.pack(side="left", fill="x", expand=True)
                    fields[field_name] = {
                        'entry': entry,
                        'mandatory': mandatory,
                        'validation': row['Field Validation'],
                        'validation_msg': row['Validation Message']
                    }

        repeating_fields = None

    tk.Button(root, text="Submit",
              command=lambda: submit_form(fields, section_key, section_data, root, repeating_fields, parent_id)).pack()


# Function to display the forms for each screen, considering parent-child relationships
def display_forms(data):
    screens = []
    current_screen_data = []

    for index, row in data.iterrows():
        if pd.notna(row['Screen']) and pd.notna(row['Section']):
            if current_screen_data:
                screens.append(pd.DataFrame(current_screen_data))
                current_screen_data = []
        current_screen_data.append(row)

    # Don't forget to append the last screen
    if current_screen_data:
        screens.append(pd.DataFrame(current_screen_data))

    for screen_data in screens:
        screen_name = screen_data.iloc[0]['Screen']
        section_key = screen_data.iloc[0]['Section Key']
        parent_id_field = screen_data.iloc[0]['Parent ID Field']

        # Determine parent-child relationships
        if parent_id_field != 'N/A' and pd.notna(parent_id_field):
            # Display a dropdown to select the parent ID
            root = tk.Tk()
            root.title(f"Select {parent_id_field}")
            selected_parent_id = tk.StringVar(root)

            parent_options = parent_child_map.get(parent_id_field, [])
            print(f"Parent options available for {parent_id_field}: {parent_options}")
            if not parent_options:
                parent_options = ["No Options Available"]
            selected_parent_id.set(parent_options[0])  # Ensure a default value is set
            tk.OptionMenu(root, selected_parent_id, *parent_options).pack()
            tk.Button(root, text="Continue", command=root.quit).pack()
            root.mainloop()
            parent_id = selected_parent_id.get()
            parent_info = parent_id
            try:
                root.destroy()
            except tk.TclError:
                pass  # Handle the case where the window has already been closed
        else:
            parent_id = None
            parent_info = None

        root = tk.Tk()
        root.title(f"Form - {screen_name}")
        create_form(screen_data, root, parent_id, parent_info)
        root.mainloop()


# Run the application
display_forms(data)
