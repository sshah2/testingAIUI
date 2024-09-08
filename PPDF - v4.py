from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1

def get_field_info(field):
    """Extract information from a single field."""
    field_type = None
    field_name = field.get('T').decode('utf-8') if field.get('T') else ''
    field_value = resolve1(field.get('V'))
    field_flags = field.get('Ff', 0)

    # Determine the field type based on flags
    if field_flags & 1 << 17:  # Combo box
        field_type = 'ComboBox'
    elif field_flags & 1 << 18:  # Checkbox
        field_type = 'Checkbox'
    else:
        field_type = 'Text'

    # For checkboxes, gather possible values
    options = []
    if field_type == 'Checkbox':
        if 'Opt' in field:
            options_list = resolve1(field['Opt'])
            if isinstance(options_list, list):
                options = [opt.decode('utf-8') for opt in options_list]

    return {
        'Field Label': field_name,
        'Field Type': field_type,
        'Options': options if options else None  # Only return options if they exist
    }

def extract_pdf_form_fields(file_path):
    """Extract all form fields from a PDF."""
    with open(file_path, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)

        if not doc.is_extractable:
            raise ValueError("Document is not extractable")

        form_fields = resolve1(doc.catalog.get('AcroForm', None)).get('Fields', [])
        return [get_field_info(resolve1(f)) for f in form_fields]

def main():
    pdf_path = "C:\\Users\\sashah\\Downloads\\reg343.pdf"  # Update this path to your PDF file
    try:
        fields_info = extract_pdf_form_fields(pdf_path)
        for field in fields_info:
            print(field)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
