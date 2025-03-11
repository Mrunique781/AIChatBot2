from flask import Flask, render_template, request, jsonify, send_file
import google.generativeai as genai
from docx import Document
from openpyxl import Workbook
import os
from io import BytesIO
import tempfile

app = Flask(__name__)

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyDAWAe3m9ST3cNXYMWz29kLxfjKJo_jJrw"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        prompt = data.get('prompt')
        file_format = data.get('format')

        # Generate content using Gemini
        response = model.generate_content(prompt)
        content = response.text

        if file_format == 'txt':
            # Generate TXT
            output = BytesIO()
            output.write(content.encode('utf-8'))
            output.seek(0)
            return send_file(
                output,
                mimetype='text/plain',
                as_attachment=True,
                download_name='generated.txt'
            )

        elif file_format == 'pdf':
            # Generate PDF using reportlab
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            output = BytesIO()
            c = canvas.Canvas(output, pagesize=letter)
            # Split content into lines to fit on PDF page
            y = 750  # Starting y position
            for line in content.split('\n'):
                if y > 50:  # Check if we need a new page
                    c.drawString(50, y, line)
                    y -= 15
                else:
                    c.showPage()
                    y = 750
            c.save()
            output.seek(0)
            return send_file(
                output,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='generated.pdf'
            )

        elif file_format == 'docx':
            # Generate DOCX
            doc = Document()
            doc.add_paragraph(content)
            output = BytesIO()
            doc.save(output)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name='generated.docx'
            )

        elif file_format == 'xlsx':
            # Generate XLSX
            wb = Workbook()
            ws = wb.active
            # Split content into rows
            for i, line in enumerate(content.split('\n'), 1):
                ws.cell(row=i, column=1, value=line)
            
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='generated.xlsx'
            )

        return jsonify({'error': 'Invalid file format'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)