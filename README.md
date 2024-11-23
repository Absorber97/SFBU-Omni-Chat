# SFBU Omni Assistant

An AI-powered chatbot application for San Francisco Bay University that processes institutional documents, fine-tunes OpenAI models, and provides intelligent responses about university information.

## 🌟 Features

### 📚 Document Processing
- PDF document processing with smart text extraction
- URL content extraction with context preservation
- Automatic text chunking and formatting
- Intelligent Q&A pair generation using OpenAI
- Duplicate content detection
- Real-time processing logs

### 🤖 AI Model Fine-tuning
- OpenAI GPT model fine-tuning
- Training progress tracking
- Model version management
- Source tracking with metadata
- Fine-tuning status monitoring

### 💬 Interactive Chat Interface
- Real-time AI responses
- Conversation history management
- Multiple fine-tuned model support
- Context-aware responses
- User-friendly interface

## 🚀 Prerequisites

- Python 3.8+
- OpenAI API key
- spaCy model: `en_core_web_sm`
- Internet connection for URL processing
- Sufficient disk space for training data

## 📦 Installation

1. Clone the repository:
```bash
git clone [repo-url]
cd sfbu-omni-chat
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key
```

5. Create required directories:
```bash
mkdir -p assets/images logs training_data
```

6. Add SFBU assets:
   - Place `SFBU.jpeg` in `assets/images/`

## 🎮 Usage

1. Start the application:
```bash
python app.py
```

2. Access the web interface at `http://localhost:7860`

3. Use the different tabs:
   - **Data Processing**: Upload PDFs or enter URLs
     - View real-time processing logs
     - See training data previews
     - Track processed sources
   
   - **Fine-tuning**: Train custom models
     - Select training files
     - Monitor training progress
     - View available models
   
   - **Chat**: Interact with the AI
     - Select models
     - View chat history
     - Get real-time responses

## 📁 Project Structure

```
sfbu-omni-chat/
├── app.py                 # Main entry point
├── core/                  # Core application logic
│   ├── app.py            # Main application class
│   └── handlers/         # Request handlers
├── data_processor/       # Data processing modules
│   ├── extractors/       # PDF and URL processors
│   ├── formatters/       # Data formatting
│   ├── fine_tuning/      # Model training
│   └── source_tracker.py # Source management
├── utils/                # Utility functions
│   ├── interface_creator.py  # UI components
│   ├── logging_handler.py    # Logging utilities
│   └── preview_handler.py    # Data preview
├── chat_interface/       # Chat functionality
├── assets/              # Static assets
├── logs/                # Application logs
└── training_data/       # Processed data
```

## 🛠️ Development

- Uses modern Python features and type hints
- Follows modular design principles
- Implements proper error handling
- Includes real-time logging
- Maintains clean code structure

### Key Dependencies

- `openai`: OpenAI API client (v1.0+)
- `gradio`: Web interface framework
- `PyPDF2`: PDF processing
- `spacy`: NLP processing
- `beautifulsoup4`: Web scraping
- `python-dotenv`: Environment management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is proprietary and confidential. All rights reserved by San Francisco Bay University.

## 🙏 Acknowledgments

- Guided by Prof. Henry Chang
- Powered by San Francisco Bay University
- Built with OpenAI's GPT technology

## 💡 Support

For support, please contact:
- SFBU IT Department
- Project maintainers through GitHub issues

---
© 2024 San Francisco Bay University. All rights reserved.