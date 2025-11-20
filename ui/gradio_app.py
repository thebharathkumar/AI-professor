#!/usr/bin/env python3
"""
Gradio web interface for the Professor Brusseau digital twin
"""
import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import gradio as gr
from config import settings
from src.agents import ProfessorAgent, ConversationManager
from src.grading import EssayGrader
from src.utils.logger import setup_logging

logger = logging.getLogger(__name__)


class ProfessorBrusseauUI:
    """Gradio UI for Professor Brusseau digital twin"""

    def __init__(self):
        self.agents = {
            "ai_ethics": ProfessorAgent(course="ai_ethics"),
            "business_ethics": ProfessorAgent(course="business_ethics")
        }
        self.graders = {
            "ai_ethics": EssayGrader(course="ai_ethics"),
            "business_ethics": EssayGrader(course="business_ethics")
        }
        self.conversations = {}

    def get_conversation(self, student_id: str, course: str) -> ConversationManager:
        """Get or create a conversation manager"""
        key = f"{student_id}_{course}"
        if key not in self.conversations:
            self.conversations[key] = ConversationManager(student_id, course)
        return self.conversations[key]

    def chat_with_professor(
        self,
        message: str,
        history: list,
        course: str,
        student_id: str
    ) -> tuple:
        """
        Handle chat interaction

        Args:
            message: User's message
            history: Chat history
            course: Selected course
            student_id: Student identifier

        Returns:
            Tuple of (updated history, empty string for input box)
        """
        if not message.strip():
            return history, ""

        try:
            # Get conversation manager
            conv_manager = self.get_conversation(student_id, course)

            # Add user message to history
            conv_manager.add_message("user", message)

            # Get agent response
            agent = self.agents[course]
            api_history = conv_manager.get_api_format_history()

            result = agent.generate_response(
                question=message,
                conversation_history=api_history[:-1],  # Exclude the current message
                use_rag=True
            )

            response = result['response']

            # Add assistant response to conversation
            conv_manager.add_message("assistant", response)

            # Update Gradio chat history
            history.append((message, response))

            return history, ""

        except Exception as e:
            logger.error(f"Error in chat: {e}")
            error_msg = "I apologize, but I'm experiencing technical difficulties. Please try again."
            history.append((message, error_msg))
            return history, ""

    def grade_assignment(
        self,
        essay_text: str,
        question_prompt: str,
        assignment_type: str,
        course: str
    ) -> str:
        """
        Grade a student assignment

        Args:
            essay_text: Student's essay
            question_prompt: Assignment prompt
            assignment_type: Type of assignment
            course: Course selection

        Returns:
            Grading feedback
        """
        if not essay_text.strip() or not question_prompt.strip():
            return "Please provide both the assignment prompt and your essay."

        try:
            grader = self.graders[course]

            result = grader.grade_essay(
                essay_text=essay_text,
                question_prompt=question_prompt,
                assignment_type=assignment_type.lower()
            )

            if 'error' in result:
                return f"Error: {result['error']}"

            return result['feedback']

        except Exception as e:
            logger.error(f"Error grading: {e}")
            return f"Error grading assignment: {str(e)}"

    def clear_conversation(self, student_id: str, course: str) -> list:
        """Clear conversation history"""
        key = f"{student_id}_{course}"
        if key in self.conversations:
            self.conversations[key].clear_history()
        return []

    def create_interface(self) -> gr.Blocks:
        """Create the Gradio interface"""

        with gr.Blocks(
            title="Professor Brusseau Digital Twin",
            theme=gr.themes.Soft()
        ) as interface:

            gr.Markdown("""
            # 🎓 Professor James Brusseau - Digital Twin

            Welcome to Professor Brusseau's always-available office hours!

            This AI-powered teaching assistant mimics Professor Brusseau's teaching style
            and expertise in **AI Ethics** and **Business Ethics**.
            """)

            with gr.Tabs():
                # Tab 1: Office Hours (Chat)
                with gr.Tab("📚 Office Hours"):
                    gr.Markdown("""
                    ### Ask Professor Brusseau
                    Ask questions about course materials, concepts, or ethical dilemmas.
                    The professor is available 24/7 to help you learn!
                    """)

                    with gr.Row():
                        with gr.Column(scale=3):
                            course_select = gr.Dropdown(
                                choices=["ai_ethics", "business_ethics"],
                                value="ai_ethics",
                                label="Select Course",
                                info="Choose which course you're asking about"
                            )
                            student_id_input = gr.Textbox(
                                label="Student ID (optional)",
                                placeholder="Enter your student ID or name",
                                value="student_demo"
                            )

                        with gr.Column(scale=2):
                            gr.Markdown("""
                            **Tips for better conversations:**
                            - Be specific in your questions
                            - Reference course materials when relevant
                            - Ask follow-up questions
                            - Explore ethical dilemmas from multiple perspectives
                            """)

                    chatbot = gr.Chatbot(
                        height=500,
                        label="Conversation with Professor Brusseau"
                    )

                    with gr.Row():
                        msg_input = gr.Textbox(
                            label="Your Question",
                            placeholder="Ask Professor Brusseau anything about the course...",
                            lines=3,
                            scale=4
                        )

                    with gr.Row():
                        submit_btn = gr.Button("Ask Question", variant="primary")
                        clear_btn = gr.Button("Clear Conversation")

                    # Chat interaction
                    submit_btn.click(
                        fn=self.chat_with_professor,
                        inputs=[msg_input, chatbot, course_select, student_id_input],
                        outputs=[chatbot, msg_input]
                    )

                    msg_input.submit(
                        fn=self.chat_with_professor,
                        inputs=[msg_input, chatbot, course_select, student_id_input],
                        outputs=[chatbot, msg_input]
                    )

                    clear_btn.click(
                        fn=self.clear_conversation,
                        inputs=[student_id_input, course_select],
                        outputs=[chatbot]
                    )

                # Tab 2: Grading Assistant
                with gr.Tab("📝 Grading Assistant"):
                    gr.Markdown("""
                    ### Essay Grading
                    Submit your essay or short answer for AI-assisted grading and feedback.
                    Receive detailed, constructive feedback in Professor Brusseau's style.
                    """)

                    grading_course = gr.Dropdown(
                        choices=["ai_ethics", "business_ethics"],
                        value="ai_ethics",
                        label="Course"
                    )

                    assignment_type_select = gr.Dropdown(
                        choices=["Essay", "Short_Answer"],
                        value="Essay",
                        label="Assignment Type"
                    )

                    question_input = gr.Textbox(
                        label="Assignment Prompt/Question",
                        placeholder="Enter the assignment question or prompt here...",
                        lines=3
                    )

                    essay_input = gr.Textbox(
                        label="Your Essay/Answer",
                        placeholder="Paste your essay or answer here...",
                        lines=15
                    )

                    grade_btn = gr.Button("Grade Assignment", variant="primary")

                    feedback_output = gr.Textbox(
                        label="Feedback",
                        lines=20,
                        interactive=False
                    )

                    grade_btn.click(
                        fn=self.grade_assignment,
                        inputs=[essay_input, question_input, assignment_type_select, grading_course],
                        outputs=[feedback_output]
                    )

                # Tab 3: About
                with gr.Tab("ℹ️ About"):
                    gr.Markdown("""
                    ## About Professor James Brusseau

                    Professor James Brusseau is a university professor specializing in:
                    - **AI Ethics**: Exploring ethical implications of artificial intelligence
                    - **Business Ethics**: Examining ethical challenges in business contexts

                    ### About This Digital Twin

                    This AI-powered digital twin is designed to:
                    1. Provide 24/7 access to Professor Brusseau's teaching style and expertise
                    2. Answer student questions using course materials and ethical frameworks
                    3. Offer a safe, non-judgmental space for exploring complex topics
                    4. Assist with grading and provide detailed feedback

                    ### How It Works

                    The system uses:
                    - **Retrieval-Augmented Generation (RAG)**: Retrieves relevant course materials
                    - **Large Language Models**: Powers natural conversation
                    - **Vector Databases**: Stores and searches course content efficiently

                    ### Privacy & Academic Integrity

                    - Conversations are stored locally for continuity
                    - Use this tool to enhance learning, not replace it
                    - Always verify important information with official course materials
                    - The grading assistant provides feedback but may not reflect official grades

                    ### Technical Details

                    - Model: Claude Sonnet 4.5
                    - Framework: LangChain with ChromaDB
                    - Interface: Gradio
                    """)

            return interface


def main():
    """Main entry point"""
    setup_logging()

    # Check if API keys are set
    if not settings.anthropic_api_key:
        logger.error("ANTHROPIC_API_KEY not set. Please configure your .env file.")
        print("\n⚠️  ERROR: ANTHROPIC_API_KEY not set!")
        print("Please copy .env.example to .env and add your API key.\n")
        return

    # Create and launch UI
    logger.info("Starting Professor Brusseau Digital Twin UI...")

    ui = ProfessorBrusseauUI()
    interface = ui.create_interface()

    # Launch
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    main()
