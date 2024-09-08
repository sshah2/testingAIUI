from argparse import ArgumentParser
import pprint  # This ensures that the pprint module is properly imported
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdftypes import resolve1

def load_form(filename):
    """Load PDF form contents into a nested list of name/value tuples"""
    with open(filename, 'rb') as file:
        parser = PDFParser(file)
        doc = PDFDocument(parser)
        if not doc.is_extractable:
            raise ValueError("Document is not extractable")

        fields = resolve1(doc.catalog.get('AcroForm', None)).get('Fields', [])
        return [load_fields(resolve1(f)) for f in fields]

def load_fields(field):
    """Recursively load form fields"""
    form = field.get('Kids', None)
    if form:
        return [load_fields(resolve1(f)) for f in form]
    else:
        name = field.get('T')
        value = resolve1(field.get('V'))
        return (name.decode('utf-8') if name else '', value)

def main():
    form = load_form("C:\\Users\\sashah\\Downloads\\reg343.pdf")
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(form)

if __name__ == '__main__':
    main()
