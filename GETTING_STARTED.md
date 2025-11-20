# Getting Started with Professor Brusseau Digital Twin

This guide will walk you through setting up and using the Professor Brusseau Digital Twin system.

## Step-by-Step Setup

### 1. System Requirements

Before starting, ensure you have:
- Python 3.9 or higher installed
- At least 2GB of free disk space
- Internet connection for API calls
- API keys from:
  - [Anthropic](https://console.anthropic.com/) (for Claude)
  - [OpenAI](https://platform.openai.com/) (for embeddings)

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd AI-professor

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your API keys
# Use any text editor, for example:
nano .env
# or
vim .env
```

Add your API keys to the `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

### 4. Prepare Your Course Materials

Create the data directory structure and add your course materials:

```bash
# Create directories for AI Ethics course
mkdir -p data/raw/ai_ethics

# Create directories for Business Ethics course
mkdir -p data/raw/business_ethics
```

Then, add your course materials to the appropriate directories:

**AI Ethics Course Materials:**
- Place PDF textbooks in `data/raw/ai_ethics/`
- Add PowerPoint slides (`.pptx` files)
- Include video transcripts (`.txt` or `.json` files)
- Any other relevant materials (Word docs, Markdown files, etc.)

**Business Ethics Course Materials:**
- Place materials in `data/raw/business_ethics/`
- Same file types as above

**Supported File Formats:**
- PDF (`.pdf`)
- Microsoft Word (`.docx`)
- PowerPoint (`.pptx`)
- Plain text (`.txt`)
- Markdown (`.md`)
- JSON transcripts (`.json`)

### 5. Ingest Course Materials

Process your course materials to create the knowledge base:

```bash
python scripts/ingest_data.py
```

This script will:
1. Scan your data directories
2. Extract text from all supported file formats
3. Split content into chunks
4. Generate embeddings
5. Store everything in a vector database

**Expected output:**
```
=== Professor Brusseau Data Ingestion ===
--- Ingesting AI Ethics Course Materials ---
Processing textbook.pdf...
Processed PDF textbook.pdf: 245 chunks
Processing lecture_slides.pptx...
Processed PPTX lecture_slides.pptx: 89 chunks
...
Adding 334 chunks to vector store...
Data ingestion complete!
Vector store stats: {'name': 'brusseau_ai_ethics', 'document_count': 334}
```

### 6. Launch the Application

Start the Gradio web interface:

```bash
python ui/gradio_app.py
```

You should see output like:
```
Starting Professor Brusseau Digital Twin UI...
Running on local URL:  http://0.0.0.0:7860
```

Open your web browser and navigate to `http://localhost:7860`

## Using the System

### Office Hours Tab

The Office Hours tab is for asking questions and having conversations with Professor Brusseau.

**How to use:**
1. Select your course (AI Ethics or Business Ethics)
2. Optionally enter a student ID
3. Type your question in the text box
4. Click "Ask Question" or press Enter

**Example questions:**
- "Can you explain the trolley problem and how it relates to AI ethics?"
- "What is the difference between deontological and utilitarian ethics?"
- "How should companies balance profit and ethical responsibility?"
- "What are the main ethical concerns around facial recognition technology?"

**Tips:**
- Be specific in your questions
- Reference course materials when relevant
- Ask follow-up questions to dig deeper
- The system maintains conversation context

### Grading Assistant Tab

The Grading Assistant helps grade essays and provides detailed feedback.

**How to use:**
1. Select your course
2. Choose assignment type (Essay or Short Answer)
3. Paste the assignment question/prompt
4. Paste the student's essay or answer
5. Click "Grade Assignment"

**What you'll receive:**
- Score breakdown for each rubric criterion
- Detailed justification for scores
- Strengths identified in the work
- Specific areas for improvement
- Total score
- Encouraging feedback

## Troubleshooting

### Common Issues

**Issue: "ANTHROPIC_API_KEY not set"**
- Solution: Make sure you've created a `.env` file and added your API key
- Check that the key starts with `sk-ant-`

**Issue: "No documents were processed"**
- Solution: Verify that you've placed course materials in `data/raw/ai_ethics/` or `data/raw/business_ethics/`
- Check that your files are in supported formats

**Issue: "Failed to generate embeddings"**
- Solution: Check your OpenAI API key in `.env`
- Verify you have internet connectivity
- Check your OpenAI account has credits/active subscription

**Issue: ChromaDB errors**
- Solution: Delete the embeddings directory and re-run ingestion:
  ```bash
  rm -rf data/embeddings/chroma_db
  python scripts/ingest_data.py
  ```

**Issue: Module import errors**
- Solution: Make sure you've activated your virtual environment:
  ```bash
  source venv/bin/activate  # macOS/Linux
  venv\Scripts\activate     # Windows
  ```

### Getting Help

If you encounter issues:
1. Check the logs for error messages
2. Verify all dependencies are installed: `pip install -r requirements.txt`
3. Ensure your API keys are valid
4. Check that course materials are in the correct directories

## Next Steps

### Customizing the System

1. **Modify teaching style**: Edit `src/agents/professor_agent.py`
2. **Adjust grading rubrics**: Edit `src/grading/rubric.py`
3. **Change RAG parameters**: Edit `config/settings.py`

### Adding More Materials

As you get more course materials:
```bash
# Add new files to the appropriate directory
cp new_materials.pdf data/raw/ai_ethics/

# Re-run ingestion
python scripts/ingest_data.py
```

### Programmatic Usage

You can also use the system in your own Python scripts:

```python
from src.agents import ProfessorAgent

# Create agent
agent = ProfessorAgent(course="ai_ethics")

# Ask question
result = agent.generate_response(
    question="What is consequentialism?",
    use_rag=True
)

print(result['response'])
```

## Best Practices

### For Students:
- Use the system to supplement, not replace, your studies
- Verify important information with official course materials
- Engage with questions thoughtfully
- Use it as a safe space to explore ideas

### For Instructors:
- Regularly update course materials
- Review grading feedback for accuracy
- Use insights to improve teaching
- Monitor for system limitations

### For Developers:
- Keep API keys secure
- Regular backup of conversation data
- Monitor API usage and costs
- Test changes in development environment first

## FAQ

**Q: Does this replace the human professor?**
A: No, this is a supplementary tool to provide 24/7 access to teaching expertise. It's designed to enhance learning, not replace human instruction.

**Q: Is my conversation data private?**
A: Yes, conversations are stored locally on your machine. API calls to Anthropic/OpenAI follow their privacy policies.

**Q: Can I use this for multiple courses?**
A: Yes, the system supports multiple courses. You can add more by creating new collection names in the configuration.

**Q: How accurate is the grading?**
A: The grading assistant provides helpful feedback but should be reviewed by a human instructor for official grades.

**Q: Can I add video lectures directly?**
A: Currently, you need to provide transcripts. Use YouTube's transcript feature or transcription services, then add the text files to the data directory.

## Resources

- Main README: [README.md](README.md)
- Anthropic Claude Docs: https://docs.anthropic.com/
- OpenAI API Docs: https://platform.openai.com/docs
- ChromaDB Docs: https://docs.trychroma.com/

---

Happy learning! 📚
