# Professor Brusseau Digital Twin 🎓

An agentic AI system that mimics Professor James Brusseau's teaching style and expertise in AI Ethics and Business Ethics. This digital twin provides 24/7 office hours, answers student questions, and assists with grading assignments.

## 🌟 Overview

This project creates a digital twin of Professor James Brusseau that:
- Answers student questions in his unique teaching style
- Provides always-available office hours
- Grades essays and provides detailed feedback
- Uses course materials through Retrieval-Augmented Generation (RAG)
- Maintains conversational context across interactions

## 🎯 Key Features

### 1. Always-Available Office Hours
- 24/7 access to Professor Brusseau's teaching expertise
- Conversational interface for exploring complex topics
- Context-aware responses using RAG
- Non-intimidating environment for asking questions

### 2. Grading Assistant
- Automated essay grading with detailed feedback
- Rubric-based evaluation
- Constructive, actionable suggestions
- Maintains Professor Brusseau's grading style

### 3. Course Coverage
- **AI Ethics**: Ethical implications of artificial intelligence
- **Business Ethics**: Ethical challenges in business contexts

## 📋 Prerequisites

- Python 3.9 or higher
- API keys:
  - Anthropic API key (for Claude)
  - OpenAI API key (for embeddings)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AI-professor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# Required:
# - ANTHROPIC_API_KEY
# - OPENAI_API_KEY
```

### 3. Prepare Course Materials

Organize your course materials in the following structure:

```
data/raw/
├── ai_ethics/
│   ├── textbook.pdf
│   ├── lecture_slides.pptx
│   ├── transcript_lecture1.txt
│   └── ...
└── business_ethics/
    ├── brusseau_business_ethics.pdf
    ├── lecture_transcripts/
    └── ...
```

### 4. Ingest Course Materials

```bash
python scripts/ingest_data.py
```

This will:
- Process all documents (PDFs, DOCX, PPTX, TXT)
- Generate embeddings
- Store in vector database for retrieval

### 5. Launch the Interface

```bash
python ui/gradio_app.py
```

Access the interface at: `http://localhost:7860`

## 📚 Project Structure

```
AI-professor/
├── config/                  # Configuration management
│   ├── settings.py         # Settings and environment variables
│   └── __init__.py
├── src/
│   ├── agents/             # Conversational agents
│   │   ├── professor_agent.py      # Main Professor Brusseau agent
│   │   └── conversation_manager.py # Conversation state management
│   ├── processors/         # Document processing
│   │   ├── document_processor.py   # PDF, DOCX, PPTX processing
│   │   ├── video_processor.py      # Video transcript processing
│   │   └── text_processor.py       # Text cleaning utilities
│   ├── vectorstore/        # Vector database management
│   │   ├── embeddings.py           # Embedding generation
│   │   └── vector_store_manager.py # ChromaDB operations
│   ├── grading/            # Grading system
│   │   ├── essay_grader.py         # Essay grading logic
│   │   └── rubric.py              # Grading rubrics
│   └── utils/              # Utilities
│       └── logger.py               # Logging configuration
├── scripts/
│   └── ingest_data.py      # Data ingestion script
├── ui/
│   └── gradio_app.py       # Gradio web interface
├── data/
│   ├── raw/                # Raw course materials
│   ├── processed/          # Processed documents
│   └── embeddings/         # Vector database storage
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
└── README.md              # This file
```

## 🔧 Usage

### Office Hours Mode

Ask questions about course materials:

```python
from src.agents import ProfessorAgent

# Initialize for AI Ethics
agent = ProfessorAgent(course="ai_ethics")

# Ask a question
result = agent.generate_response(
    question="Can you explain the trolley problem and its relevance to AI?",
    use_rag=True
)

print(result['response'])
```

### Grading Mode

Grade student essays:

```python
from src.grading import EssayGrader

# Initialize grader
grader = EssayGrader(course="ai_ethics")

# Grade an essay
result = grader.grade_essay(
    essay_text="[Student's essay text]",
    question_prompt="Discuss the ethical implications of AI bias.",
    assignment_type="essay"
)

print(result['feedback'])
```

### Conversation Management

Maintain conversation context:

```python
from src.agents import ProfessorAgent, ConversationManager

agent = ProfessorAgent(course="ai_ethics")
conversation = ConversationManager(student_id="student123")

# First question
result = agent.generate_response(
    question="What is utilitarianism?",
    conversation_history=conversation.get_api_format_history()
)
conversation.add_message("user", "What is utilitarianism?")
conversation.add_message("assistant", result['response'])

# Follow-up question (maintains context)
result = agent.generate_response(
    question="How does it apply to self-driving cars?",
    conversation_history=conversation.get_api_format_history()
)
```

## 🎨 Customization

### Modifying Teaching Style

Edit the system prompt in `src/agents/professor_agent.py`:

```python
SYSTEM_PROMPT = """You are Professor James Brusseau...
[Customize the personality and teaching approach here]
"""
```

### Custom Grading Rubrics

Create custom rubrics in `src/grading/rubric.py`:

```python
CUSTOM_RUBRIC = [
    RubricCriterion(
        name="Custom Criterion",
        description="Description of what to evaluate",
        max_points=25.0
    ),
    # Add more criteria...
]
```

### Adjusting RAG Parameters

Modify retrieval settings in `config/settings.py`:

```python
top_k_results: int = 5          # Number of documents to retrieve
similarity_threshold: float = 0.7  # Relevance threshold
temperature: float = 0.7        # LLM temperature
```

## 🏗️ Architecture

### System Components

1. **Document Processing Pipeline**
   - Extracts text from various formats
   - Chunks documents for optimal retrieval
   - Processes video transcripts

2. **Vector Store (RAG)**
   - Generates embeddings using OpenAI
   - Stores in ChromaDB
   - Enables semantic search

3. **Conversational Agent**
   - Uses Claude for generation
   - Retrieves relevant context
   - Maintains conversation history

4. **Grading System**
   - Rubric-based evaluation
   - Provides detailed feedback
   - References course materials

### Data Flow

```
Student Question
    ↓
Query Vector Store (Retrieve relevant course materials)
    ↓
Combine Question + Context + Conversation History
    ↓
Generate Response with Claude
    ↓
Return to Student
```

## 📊 Milestones

### ✅ Initial Milestone: Always-Available Office Hours
- RAG-based question answering
- Conversational interface
- Course material integration
- Professor Brusseau's teaching style

### ✅ Secondary Milestone: Grading Assistant
- Essay grading with rubrics
- Detailed feedback generation
- Batch grading support

### 🔜 Future Milestone: Full Autonomy
- Oral exam capabilities
- Voice interaction
- Visual avatar
- Complete course automation

## 🧪 Testing

Run tests (when implemented):

```bash
pytest tests/
```

## 📝 Adding New Course Materials

1. Place files in appropriate directory:
   ```bash
   data/raw/ai_ethics/new_material.pdf
   ```

2. Run ingestion:
   ```bash
   python scripts/ingest_data.py
   ```

3. Materials are now available for RAG retrieval

## 🔐 Security & Privacy

- API keys stored in `.env` (never commit to git)
- Conversation data stored locally
- No external data transmission except API calls
- Students control their data

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional document format support
- Voice interface integration
- Enhanced grading rubrics
- Performance optimizations
- Multi-language support

## 👤 About Professor James Brusseau

Professor James Brusseau specializes in AI Ethics and Business Ethics, bringing theoretical frameworks to practical, real-world applications. His teaching emphasizes:
- Critical thinking
- Multiple perspectives
- Real-world case studies
- Accessible explanations
- Ethical reasoning development

## 🙏 Acknowledgments

- Anthropic Claude API for conversational AI
- OpenAI for embeddings
- ChromaDB for vector storage
- Gradio for the web interface

---

Built with ❤️ to enhance education and make Professor Brusseau's expertise available 24/7