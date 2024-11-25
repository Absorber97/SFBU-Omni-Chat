# SFBU Omni Chat 🤖

An intelligent chatbot system for San Francisco Bay University, powered by OpenAI's GPT models with RAG (Retrieval Augmented Generation) capabilities. Features advanced data processing for PDFs and web content, along with model fine-tuning capabilities to enhance domain-specific knowledge.

## 📁 Project Structure

```
sfbu-omni-chat/
├── app.py # Main entry point
├── core/ # Core application logic
│ ├── app.py # Main application class
│ └── handlers/ # Request handlers
├── data_processor/ # Data processing modules
│ ├── extractors/ # PDF and URL processors
│ ├── formatters/ # Data formatting
│ ├── fine_tuning/ # Model training
│ └── source_tracker.py # Source management
├── utils/ # Utility functions
│ ├── interface_creator.py # UI components
│ ├── logging_handler.py # Logging utilities
│ └── preview_handler.py # Data preview
├── chat_interface/ # Chat functionality
├── assets/ # Static assets
├── logs/ # Application logs
└── training_data/ # Processed data
```


## 🚀 Features

- **Document Processing**
  - PDF text extraction with context preservation
  - URL content scraping with recursive crawling
  - Batch processing support
  - Source tracking and management

- **RAG Implementation**
  - FAISS-powered vector similarity search
  - Dynamic context retrieval
  - Multiple index support
  - Real-time index management

- **Chat Interface**
  - Real-time conversation
  - Content moderation
  - Multiple model support
  - Custom styling and avatars

- **Model Management**
  - Fine-tuning capabilities
  - Training progress monitoring
  - Model version control
  - Performance analytics

## 🛠️ Development

### Prerequisites

- Python 3.9+
- OpenAI API key
- FAISS library
- Gradio framework

### Installation

1. Clone the repository:

```
bash
git clone [repository-url] 
cd sfbu-omni-chat
```


2. Create and activate virtual environment:

```
bash
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
```


3. Install dependencies:

```
bash
pip install -r requirements.txt
```


4. Set up environment variables:

```
OPENAI_API_KEY=your_openai_api_key
```


### Running the Application

```
bash
python app.py
```


The interface will be available at `http://localhost:7860`

## 📚 Key Dependencies

- **Core Functionality**
  - `openai>=1.0.0` - OpenAI API integration
  - `faiss-cpu>=1.7.4` - Vector similarity search
  - `gradio>=4.0.0` - Web interface framework

- **Document Processing**
  - `PyPDF2>=3.0.0` - PDF processing
  - `beautifulsoup4>=4.12.0` - Web scraping
  - `requests>=2.31.0` - HTTP client

- **Security & Logging**
  - `cryptography>=41.0.0` - Security operations
  - `structlog>=23.2.0` - Structured logging
  - `urllib3>=2.1.0` - HTTP client

## 🔒 Security Features

- Content moderation using OpenAI's moderation API
- Secure API key management
- Input validation and sanitization
- Rate limiting and request throttling

## 📝 Documentation

Detailed documentation is available in the `/docs` directory:
- API Reference
- Architecture Overview
- Development Guide
- Deployment Instructions

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- San Francisco Bay University for support and resources
- Henry Chang for guidance and course materials
- OpenAI for API and model access
- FAISS team for vector similarity implementation
- Gradio team for the UI framework