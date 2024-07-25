from flask import Flask, request, jsonify, render_template
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.urandom(24).hex()

# Configure the Gemini API
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    logger.error("GOOGLE_API_KEY not found in environment variables")
    raise ValueError("GOOGLE_API_KEY is not set")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    logger.info("Gemini API configured successfully")
except Exception as e:
    logger.error(f"Failed to configure Gemini API: {e}")
    raise

def generate_content(prompt):
    """Generate content based on the prompt using Gemini."""
    try:
        response = model.generate_content(prompt)
        result = response.text
        result = result.replace('*', '')  # Remove asterisks if present
    except Exception as e:
        logger.error(f"Failed to generate content: {e}")
        result = f"Content generation failed: {str(e)}"
    return result

def summarize_text(text):
    """Summarize the given text using Gemini."""
    try:
        prompt = f"Please summarize the following text concisely:\n\n{text}"
        response = model.generate_content(prompt)
        summary = response.text
        summary = summary.replace('*', '')  # Remove asterisks if present
    except Exception as e:
        logger.error(f"Failed to summarize text: {e}")
        summary = f"Summarization failed: {str(e)}"
    return summary

@app.route('/')
def index():
    """Render the index HTML template."""
    return render_template('index.html')

@app.route('/generate_content', methods=['POST'])
def generate_content_endpoint():
    """Endpoint to generate content."""
    prompt = request.json.get('prompt')
    if not prompt:
        return jsonify({'error': 'Prompt is required'}), 400
    content = generate_content(prompt)
    return jsonify({'content': content})

@app.route('/summarize', methods=['POST'])
def summarize_endpoint():
    """Endpoint to summarize text."""
    text = request.json.get('text')
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    summary = summarize_text(text)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)