# SFBU Omni Chat 🤖

An intelligent chatbot system for San Francisco Bay University, powered by OpenAI's GPT models with RAG (Retrieval Augmented Generation) capabilities. This system provides personalized assistance to students, faculty, and staff while leveraging advanced natural language processing and information retrieval techniques.

Related Project: https://github.com/Absorber97/Omni-Doc-Starter

![Cover](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/Cover.png)

## 🌟 Overview

SFBU Omni Chat serves as a comprehensive knowledge assistant that can:
- Answer questions about SFBU policies, courses, and procedures
- Assist with academic and administrative inquiries
- Provide personalized responses based on user roles
- Learn and adapt from new information through RAG implementation
- Process and understand various document formats

## 📁 Project Structure

```
sfbu-omni-chat/
├── app.py                  # Main application entry point
├── core/                   # Core application logic
│   ├── app.py             # Main application class
│   ├── config.py          # Configuration management
│   └── handlers/          # Request handlers
│       ├── chat.py        # Chat message handling
│       ├── auth.py        # Authentication
│       └── moderation.py  # Content moderation
├── data_processor/        # Data processing modules
│   ├── extractors/        # Content extraction
│   │   ├── pdf.py        # PDF processing
│   │   └── web.py        # Web scraping
│   ├── formatters/        # Data formatting
│   ├── fine_tuning/       # Model training
│   └── source_tracker.py  # Source management
├── utils/                 # Utility functions
│   ├── interface_creator.py  # UI components
│   ├── logging_handler.py   # Logging utilities
│   └── preview_handler.py   # Data preview
├── chat_interface/        # Chat functionality
│   ├── components/        # UI components
│   ├── styles/           # CSS and styling
│   └── handlers/         # Event handlers
├── assets/               # Static assets
│   ├── images/          # Image resources
│   └── templates/       # HTML templates
├── logs/                # Application logs
└── training_data/       # Processed data
```

## 🚀 Features

### Data Processing & Extraction

![Processing](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/Data%20Processing.png)

- **Document Processing**
  - PDF text extraction with layout preservation
  - Table and image detection
  - Metadata extraction and indexing
  - Batch processing for multiple documents
  - OCR capabilities for scanned documents

- **Data Formatting**
  - Structured data conversion
  - Text cleaning and normalization
  - Entity recognition and tagging
  - Custom formatting templates
  - JSON/CSV export capabilities

- **Web Content Processing**
  - Recursive web crawling
  - HTML content extraction
  - Dynamic content handling
  - Automatic content updates
  - Link validation and tracking

### Model Fine-tuning

![Fine-tuning](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/Fine-tuning.png)

- **Training Pipeline**
  - Custom dataset creation and curation
  - Training data validation
  - Hyperparameter optimization
  - Cross-validation support
  - Model performance metrics

- **Fine-tuning Management**
  - Training progress monitoring
  - Model evaluation tools
  - A/B testing capabilities
  - Version control and rollback
  - Model deployment automation

### RAG (Retrieval Augmented Generation)

![RAG](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/RAG%20Setup.png)

- **Vector Database**
  - FAISS-powered similarity search
  - Multiple index management
  - Automatic index updates
  - Query optimization
  - Efficient vector storage

- **Context Enhancement**
  - Dynamic context window sizing
  - Smart chunk management
  - Multi-document context merging
  - Source attribution
  - Relevance scoring

- **Knowledge Integration**
  - Real-time knowledge updates
  - Source verification
  - Fact-checking capabilities
  - Citation management
  - Knowledge graph integration

### Chat Capabilities

![Standard](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/Vanilla%20Chat.png?raw=true)

- **Standard Chat Mode**
  - Natural language understanding
  - Context-aware responses
  - Multi-turn conversations
  - Rich text formatting
  - Code syntax highlighting

![Premium - Discover](https://github.com/Absorber97/SFBU-Omni-Chat/blob/main/assets/github/Discovery%20Mode.png)

- **Premium Chat Features**
  - Advanced query understanding
  - Personalized responses
  - Deep domain expertise
  - Interactive tutorials
  - Priority response handling

- **Chat Interface**
  - Role-based access control
  - Real-time response streaming
  - Message threading
  - History management
  - File sharing capabilities

- **Interaction Modes**
  - Regular conversational mode
  - Discovery mode for exploration
  - Quick reference mode
  - Deep dive analysis
  - Tutorial mode

## 🛠️ Development

### Prerequisites
- Python 3.9+
- OpenAI API key
- FAISS library
- Gradio framework
- Git

### System Requirements
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB+ free space
- **OS**: Linux, macOS, or Windows 10+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/sfbu/sfbu-omni-chat.git
cd sfbu-omni-chat
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
# Create .env file
OPENAI_API_KEY=your_openai_api_key
FAISS_INDEX_PATH=/path/to/index
LOG_LEVEL=INFO
MAX_TOKENS=2048
TEMPERATURE=0.7
```

### Running the Application

Development mode:
```bash
python app.py --dev
```

Production mode:
```bash
python app.py --prod
```

The interface will be available at:
- Development: `http://localhost:7860`
- Production: `http://localhost:8000`

## 📚 Dependencies

### Core Dependencies
- `openai>=1.0.0` - OpenAI API integration
- `faiss-cpu>=1.7.4` - Vector similarity search
- `gradio>=4.0.0` - Web interface framework
- `pytorch>=2.0.0` - Machine learning operations

### Processing Dependencies
- `PyPDF2>=3.0.0` - PDF processing
- `beautifulsoup4>=4.12.0` - Web scraping
- `requests>=2.31.0` - HTTP client
- `numpy>=1.24.0` - Numerical operations

### Security & Logging
- `cryptography>=41.0.0` - Security operations
- `structlog>=23.2.0` - Structured logging
- `urllib3>=2.1.0` - HTTP client
- `python-dotenv>=1.0.0` - Environment management

## 🔒 Security Features

### Authentication & Authorization
- Role-based access control
- JWT token authentication
- Session management
- API key rotation

### Content Security
- Input sanitization
- Content moderation
- Rate limiting
- Request validation

### Data Protection
- Encryption at rest
- Secure API communication
- PII data handling
- Audit logging

## 📈 Performance Optimization

### Caching Strategy
- Response caching
- Index caching
- Static asset caching
- Query result caching

### Resource Management
- Connection pooling
- Memory optimization
- Background task processing
- Load balancing

## 🔍 Monitoring & Logging

### Application Metrics
- Response times
- Error rates
- Resource usage
- User interactions

### Log Management
- Structured logging
- Log rotation
- Error tracking
- Performance monitoring

## 📝 Documentation

Comprehensive documentation is available in the `/docs` directory:

### For Users
- User Guide
- FAQ
- Troubleshooting
- Best Practices

### For Developers
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

### Development Guidelines
- Follow PEP 8 style guide
- Write unit tests
- Update documentation
- Create meaningful commits

## 🐛 Issue Reporting

1. Check existing issues
2. Use issue templates
3. Provide reproduction steps
4. Include system information

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- San Francisco Bay University for support and resources
- Henry Chang for guidance and course materials
- OpenAI for API and model access
- FAISS team for vector similarity implementation
- Gradio team for the UI framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Contact SFBU IT Support
- Check the documentation
- Join our Discord community

## 🔮 Future Roadmap

- Mobile application support
- Multi-language support
- Voice interface integration
- Advanced analytics dashboard
- Integration with SFBU systems
