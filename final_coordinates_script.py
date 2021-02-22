
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfform
from reportlab.lib.colors import magenta, pink, blue, green
from pdfrw.errors import PdfParseError
from pdfrw import PdfReader, PdfWriter, PageMerge

from PyPDF2 import PdfFileMerger, PdfFileWriter, PdfFileReader

import json


def json_record():
    file = open('json_record')
    return json.loads(file.read())


def canvas_coordinates(*args):
    """
    top : x,
    left : y,
    bottom:width,
    right : height 
    for the reportlab x and y coordinates formula are :-
    y = (height-bottom)*72/dpi
    x = left * 72/dpi
    """
    dpi = 200
    height, bottom, left = args
    y = (height-bottom)*72/dpi
    x = left * 72/dpi
    return (x, y)


def add_field_type_key(page_cordinates):
    image_type = ['SIGNATURE', 'SEAL']
    text_type = ['DATE', 'INITIAL']
    for key in page_cordinates.keys():
        if key.find(image_type[0]) != -1 or key.find(image_type[1]) != -1:
            page_cordinates[key]['field_type'] = 'image'
        elif key.find(text_type[0]) != -1 or key.find(text_type[1]) != -1:
            page_cordinates[key]['field_type'] = 'text'

    return page_cordinates


def create_simple_form(page_cordinates, page_name, page_height):
    """   
    canvas_coordinates(height,bottom,left)
    """
    pdf = canvas.Canvas(page_name)
    page_cordinates = add_field_type_key(page_cordinates)
    for key in page_cordinates.keys():
        if page_cordinates[key]['field_type'] == 'image':
            x, y = canvas_coordinates(page_height,
                                      page_cordinates[key]['bottom'],
                                      page_cordinates[key]['left'])
            pdf.drawImage("image1.png", x, y, 20, 35)

        elif page_cordinates[key]['field_type'] == 'text':
            x, y = canvas_coordinates(page_height,
                                      page_cordinates[key]['bottom'],
                                      page_cordinates[key]['left'])
            today = date.today()
            pdf.drawString(x, y, str(today))
    pdf.save()

def canvas_pdf_merger():
    pdf = PdfFileReader('actual_pdf.pdf')
    pdf_merger = PdfFileMerger()
    for x in range(len(pdf.pages)):
        output = PdfFileWriter()
        output.addPage(pdf.getPage(x))
        output_file = f'split_pdfs/document_{x}.pdf'
        print(f'output_file-> {output_file}')
        with open(output_file, "wb") as output_stream:
            output.write(output_stream)
        print(f'x----{x}')
        try:
            writer_output = PdfWriter()
            split_pdf = PdfReader(f'split_pdfs/document_{x}.pdf')
            canvas_pdf = PdfReader(f'canvas_pdfs/canvas_page_{x}')
            canvas_pdf_page = canvas_pdf.pages[0]
            for y in range(len(split_pdf.pages)):
                merger = PageMerge(split_pdf.pages[y])
                merger.add(canvas_pdf_page).render()
            writer_output.write(
                f'merged_pdfs/canvas_merged_pfd_{x}', split_pdf)
            pdf_merger.append(f'merged_pdfs/canvas_merged_pfd_{x}')
        except PdfParseError:
            pdf_merger.append(f'split_pdfs/document_{x}.pdf')
    pdf_merger.write('result_1.pdf')
    pdf_merger.close()


def pdf_coodinates_plotting():
    json_data = json_record()['extraction']['area_detection']['documents']
    for x in range(len(json_data.keys())):
        page_data = json_data[f'document_{x}']['Pages']
        for y in range(len(page_data)):
            page_height = page_data[f'page_{x}']['pageHeight']
            if page_data[f'page_{x}'].get('fields'):
                create_simple_form(
                    page_cordinates=page_data[f'page_{x}']['fields'], page_name=f'canvas_pdfs/canvas_page_{x}', page_height=page_height)

    canvas_pdf_merger()


if __name__ == '__main__':
    pdf_coodinates_plotting()
