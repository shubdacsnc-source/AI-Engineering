from flask import Flask, request, jsonify
from utils.response_modes import ResponseGenerator
from utils.search_utils import DocumentSearch
import json

app = Flask(__name__)

# Initialize components
response_generator = ResponseGenerator()
document_search = DocumentSearch()

@app.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for generating responses
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data['query']
        mode = data.get('mode', 'friendly')  # Default to friendly mode

        response = response_generator.generate_response(query, mode)

        return jsonify({
            'query': query,
            'response': response,
            'mode': mode
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/add_documents', methods=['POST'])
def add_documents():
    """
    Add documents to the knowledge base
    """
    try:
        data = request.get_json()

        if not data or 'documents' not in data:
            return jsonify({'error': 'Documents are required'}), 400

        documents = data['documents']

        # Convert to document objects if needed
        doc_objects = []
        for doc in documents:
            if isinstance(doc, str):
                # Create a simple document object
                doc_obj = type('Document', (), {'page_content': doc})()
                doc_objects.append(doc_obj)
            else:
                doc_objects.append(doc)

        response_generator.add_documents(doc_objects)
        document_search.add_documents(doc_objects)

        return jsonify({
            'message': f'Added {len(doc_objects)} documents to the knowledge base',
            'count': len(doc_objects)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """
    Search for documents
    """
    try:
        data = request.get_json()

        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400

        query = data['query']
        top_k = data.get('top_k', 5)

        results = document_search.search_documents(query, top_k=top_k)

        # Format results
        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                'content': doc.page_content if hasattr(doc, 'page_content') else str(doc),
                'score': float(score)
            })

        return jsonify({
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)