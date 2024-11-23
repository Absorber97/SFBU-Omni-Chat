# SFBU Omni Chat

SFBU Omni Chat is an intelligent AI assistant specifically designed for San Francisco Bay University (SFBU). It processes university documents, fine-tunes AI models with SFBU-specific knowledge, and provides instant answers about programs, admissions, and more.

## Features

- 📚 **Document Processing**
  - PDF document processing
  - URL content extraction
  - Automatic text chunking and formatting
  - Training data generation

- 🤖 **AI Model Fine-tuning**
  - OpenAI GPT model fine-tuning
  - Progress tracking
  - Model management
  - Source tracking

- 💬 **Interactive Chat Interface**
  - Real-time AI responses
  - Conversation history
  - Multiple fine-tuned model support
  - Copy-paste functionality

## Installation

1. Clone the repository:

```
    bash
    git clone [repo-url]
    cd sfbu-omni-chat
```


2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
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


6. Add SFBU logo:
   - Place `SFBU.jpeg` in `assets/images/`
   - Place `Bayhawk.jpeg` in `assets/images/`

## Usage

1. Start the application:

```bash
python app.py
```


2. Access the web interface at `http://localhost:7860`

3. Use the different tabs:
   - **Data Processing**: Upload PDFs or URLs to process
   - **Fine-tuning**: Train AI models with processed data
   - **Chat**: Interact with the fine-tuned AI assistant

## Project Structure


```

sfbu-omni-chat/
├── app.py # Main application file
├── config.py # Configuration settings
├── requirements.txt # Project dependencies
├── assets/
│ └── images/ # Image assets
├── chat_interface/
│ └── chat_manager.py # Chat functionality
├── data_processor/
│ ├── extractors/ # PDF and URL processors
│ ├── formatters/ # Data formatting
│ ├── fine_tuning/ # Model training
│ └── source_tracker.py # Source management
├── logs/ # Application logs
└── training_data/ # Processed training data

```


## Development

- Python 3.8+ required
- Uses Gradio for the web interface
- OpenAI API for AI model fine-tuning
- Follows PEP 8 style guide

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is proprietary and confidential. All rights reserved by San Francisco Bay University.

## Acknowledgments

- Guided by Prof. Henry Chang
- Powered by San Francisco Bay University
- Built with OpenAI's GPT technology

## Support

For support, please contact [appropriate contact information].

---
Developed for San Francisco Bay University © 2024