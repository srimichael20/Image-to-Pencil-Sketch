from flask import Flask, render_template, request, send_file
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads/'
PROCESSED_FOLDER = 'static/processed/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

@app.route('/')
def home():
    return '''
    <!doctype html>
    <title>Image to Pencil Sketch</title>
    <center>
    <h1>Image To Pencil Sketch Project</h1>
    <form method="post" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="Upload">
    </form>
    </center>
    '''

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Convert the image to a pencil sketch
        sketch_path = create_pencil_sketch(filepath, filename)

        return f'''
        <center>
        <h1>Original Image</h1>
        <img src="/{filepath}" width="300">
        <h1>Pencil Sketch</h1>
        <img src="/{sketch_path}" width="300">
        <br>
        <a href="/{sketch_path}" download>Download Pencil Sketch</a>
        </center>
        '''

def create_pencil_sketch(input_path, filename):
    image = cv2.imread(input_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    inverted_image = cv2.bitwise_not(gray_image)
    blurred = cv2.GaussianBlur(inverted_image, (21, 21), sigmaX=0, sigmaY=0)
    inverted_blur = cv2.bitwise_not(blurred)
    sketch = cv2.divide(gray_image, inverted_blur, scale=256.0)

    output_path = os.path.join(app.config['PROCESSED_FOLDER'], f'sketch_{filename}')
    cv2.imwrite(output_path, sketch)
    return output_path

if __name__ == '__main__':
    app.run(debug=True)
