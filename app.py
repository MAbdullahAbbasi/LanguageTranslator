from flask import Flask, request, jsonify, send_from_directory, make_response
from googletrans import Translator
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)
translator = Translator()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

@app.route('/detect-language', methods=['POST'])
def detect_language():
    data = request.get_json()
    text = data.get('text')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        detection = translator.detect(text)
        return jsonify({'language': detection.lang})
    except Exception as e:
        print(f"Error detecting language: {e}")
        return jsonify({'error': 'Failed to detect language'}), 500

@app.route('/convert-language', methods=['POST'])
def convert_language():
    data = request.get_json()
    text = data.get('text')
    target_language = data.get('targetLanguage')

    if not text or not target_language:
        return jsonify({'error': 'Text and target language are required'}), 400

    try:
        translation = translator.translate(text, dest=target_language)
        return jsonify({'translatedText': translation.text})
    except Exception as e:
        print(f"Error translating text: {e}")
        return jsonify({'error': 'Failed to translate text'}), 500

@app.after_request
def apply_headers(response):
    # Security Headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "frame-ancestors 'self'"

    # Remove Deprecated Headers
    response.headers.pop('X-XSS-Protection', None)
    response.headers.pop('Expires', None)
    response.headers.pop('Pragma', None)

    # Cache Control for Static Resources
    if 'Cache-Control' not in response.headers:
        response.cache_control.max_age = 31536000  # 1 year
        response.cache_control.public = True
        response.headers['Cache-Control'] += ', immutable'

    return response

if __name__ == '__main__':
    app.run(debug=True)
