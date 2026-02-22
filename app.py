import os
import shutil
from flask import Flask, request, send_file, jsonify
from spleeter.separator import Separator

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Use 2stems (vocals + accompaniment)
separator = Separator('spleeter:2stems')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    # Run AI Separation
    try:
        separator.separate_to_file(input_path, OUTPUT_FOLDER)
        
        # Spleeter creates a folder named after the file
        folder_name = os.path.splitext(file.filename)[0]
        result_path = os.path.join(OUTPUT_FOLDER, folder_name, "accompaniment.wav")

        if os.path.exists(result_path):
            return send_file(result_path, as_attachment=True)
        return jsonify({"error": "File not found after processing"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup input file to save space
        if os.path.exists(input_path):
            os.remove(input_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
