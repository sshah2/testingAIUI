from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1, PDFObjRef
from pdfminer.psparser import PSLiteral, PSKeyword
import io

def get_field_values(field):
    """Extract values from a PDF field dictionary."""
    field_data = {}
    for (k, v) in field.items():
        if isinstance(k, PSKeyword) or isinstance(k, PSLiteral):
            key_name = str(k)
        else:
            key_name = k

        if isinstance(v, PDFObjRef):
            field_data[key_name] = resolve1(v)
        else:
            field_data[key_name] = v

    return field_data

def extract_pdf_fields(file_path):
    """Extract form fields from a PDF."""
    data = {}
    with open(file_path, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)

        if not doc.is_extractable:
            raise ValueError("Document is not extractable")

        fields = resolve1(doc.catalog.get('AcroForm', None)).get('Fields', [])
        for f in fields:
            field = resolve1(f)
            field_name = field.get('T').decode('utf-8') if field.get('T') else None
            field_value = field.get('V')
            field_data = get_field_values(field)

            if field_name:
                data[field_name] = {
                    'value': field_value,
                    'data': field_data
                }

    return data

def print_form_fields(data):
    """Print the form fields and their attributes in a readable format."""
    for name, details in data.items():
        print(f"Field Name: {name}")
        print("Details:")
        for key, value in details['data'].items():
            print(f"  {key}: {value}")
        print("\n")

def main():
    pdf_path = "C:\\Users\\sashah\\Downloads\\reg343.pdf"  # Update this to your PDF file path
    try:
        form_data = extract_pdf_fields(pdf_path)
        print_form_fields(form_data)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
