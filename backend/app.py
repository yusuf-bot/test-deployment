from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import os
import tempfile
from typing import List, Dict, Any

app = Flask(__name__)
CORS(app)

def process_uploaded_file(file_info: Dict[str, Any]) -> str:
    """Process uploaded file and return its content summary"""
    try:
        # Decode base64 content
        file_content = base64.b64decode(file_info['content'])
        file_name = file_info['name']
        file_type = file_info['type']
        
        # Handle different file types
        if file_type.startswith('text/') or file_name.endswith(('.txt', '.py', '.js', '.html', '.css', '.md', '.json')):
            # Text files
            try:
                content = file_content.decode('utf-8')
                return f"📄 **{file_name}** (Text file, {len(content)} characters):\n```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```"
            except UnicodeDecodeError:
                return f"📄 **{file_name}** (Binary file, {len(file_content)} bytes) - Cannot preview binary content"
        
        elif file_name.endswith('.csv'):
            # CSV files
            try:
                content = file_content.decode('utf-8')
                lines = content.split('\n')[:10]  # First 10 lines
                preview = '\n'.join(lines)
                return f"📊 **{file_name}** (CSV file, {len(content)} characters):\n```csv\n{preview}{'...' if len(lines) > 10 else ''}\n```"
            except UnicodeDecodeError:
                return f"📊 **{file_name}** (CSV file, {len(file_content)} bytes) - Cannot decode file"
        
        else:
            # Other file types
            return f"📎 **{file_name}** ({file_type}, {len(file_content)} bytes) - File uploaded successfully but cannot preview this file type"
    
    except Exception as e:
        return f"❌ Error processing file {file_info.get('name', 'unknown')}: {str(e)}"

def generate_response(message: str, files: List[Dict] = None) -> str:
    """Generate chatbot response based on message and files"""
    
    # Process uploaded files
    file_summaries = []
    if files:
        for file_info in files:
            summary = process_uploaded_file(file_info)
            file_summaries.append(summary)
    
    # Simple response generation (you can replace this with your AI model)
    response_parts = []
    
    if file_summaries:
        response_parts.append("I've received and analyzed your uploaded files:\n")
        response_parts.extend(file_summaries)
        response_parts.append(f"\n**Your question:** {message}\n")
        response_parts.append("**My response:** Based on the files you've uploaded, I can help you analyze the content. ")
    
    # Basic responses based on message content
    message_lower = message.lower()
    
    if "hello" in message_lower or "hi" in message_lower:
        response_parts.append("Hello! How can I help you today?")
    elif "how are you" in message_lower:
        response_parts.append("I'm doing well, thank you for asking! I'm here to help you with your questions and analyze any files you upload.")
    elif "file" in message_lower and not files:
        response_parts.append("I'd be happy to help with files! You can upload documents, code files, CSVs, and more using the file upload feature.")
    elif "analyze" in message_lower or "data" in message_lower:
        if files:
            response_parts.append("I can see you've uploaded files for analysis. I can help you understand the content, extract insights, or answer specific questions about the data.")
        else:
            response_parts.append("I can help analyze data and files. Please upload the files you'd like me to examine!")
    elif "code" in message_lower:
        if files:
            response_parts.append("I can help review your code, suggest improvements, debug issues, or explain how it works.")
        else:
            response_parts.append("I can help with coding questions, review code, and provide programming assistance. Feel free to upload your code files!")
    else:
        if files:
            response_parts.append(f"Thank you for your question: '{message}'. I've also processed the files you uploaded above.")
        else:
            response_parts.append(f"You asked: '{message}'. This is a simple demo response. You can also upload files for me to analyze!")
    
    return "\n".join(response_parts)

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "chatbot-backend",
        "features": ["text_chat", "file_upload", "file_analysis"]
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint with file support"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        message = data.get('message', '')
        files = data.get('files', [])
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
        
        # Generate response
        reply = generate_response(message, files)
        
        return jsonify({
            "reply": reply,
            "files_processed": len(files),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}",
            "status": "error"
        }), 500

@app.route('/upload', methods=['POST'])
def upload_endpoint():
    """Dedicated file upload endpoint (optional)"""
    try:
        data = request.get_json()
        files = data.get('files', [])
        
        if not files:
            return jsonify({"error": "No files provided"}), 400
        
        summaries = []
        for file_info in files:
            summary = process_uploaded_file(file_info)
            summaries.append(summary)
        
        return jsonify({
            "message": "Files processed successfully",
            "files_processed": len(files),
            "summaries": summaries,
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"Upload error: {str(e)}",
            "status": "error"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)