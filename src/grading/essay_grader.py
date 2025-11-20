"""
Essay grading assistant using AI
"""
import logging
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from config import settings
from .rubric import GradingRubric, RubricCriterion
from src.vectorstore import VectorStoreManager

logger = logging.getLogger(__name__)


class EssayGrader:
    """
    AI-powered essay grading assistant

    Grades student essays based on rubrics and course materials,
    providing detailed feedback in Professor Brusseau's style.
    """

    GRADING_SYSTEM_PROMPT = """You are Professor James Brusseau grading student work in your ethics course.

Your grading approach:
- Fair, consistent, and constructive
- Focus on helping students improve, not just assigning points
- Provide specific, actionable feedback
- Recognize both strengths and areas for improvement
- Reference course materials and concepts when relevant
- Maintain high academic standards while being encouraging

When grading:
1. Evaluate based on the provided rubric
2. Give specific examples from the student's work
3. Explain why points were awarded or deducted
4. Provide constructive suggestions for improvement
5. Be thorough but concise in your feedback"""

    def __init__(self, course: str = "ai_ethics"):
        """
        Initialize the essay grader

        Args:
            course: Course context (ai_ethics or business_ethics)
        """
        self.course = course
        self.client = Anthropic(api_key=settings.anthropic_api_key)

        # Initialize vector store for course materials
        collection_name = (
            settings.collection_name_ai_ethics if course == "ai_ethics"
            else settings.collection_name_business_ethics
        )
        self.vector_store = VectorStoreManager(collection_name)

        logger.info(f"Initialized EssayGrader for {course}")

    def grade_essay(
        self,
        essay_text: str,
        question_prompt: str,
        assignment_type: str = "essay",
        custom_rubric: Optional[List[RubricCriterion]] = None
    ) -> Dict[str, Any]:
        """
        Grade a student essay

        Args:
            essay_text: The student's essay
            question_prompt: The original assignment question/prompt
            assignment_type: Type of assignment ('essay' or 'short_answer')
            custom_rubric: Optional custom rubric (uses default if not provided)

        Returns:
            Dictionary with grade, feedback, and rubric scores
        """
        try:
            # Get appropriate rubric
            rubric = custom_rubric or GradingRubric.get_rubric(assignment_type)

            # Retrieve relevant course materials
            relevant_materials = self.vector_store.search(
                question_prompt + " " + essay_text[:500],  # Use question and beginning of essay
                n_results=3
            )

            # Format context
            context = self._format_course_context(relevant_materials)

            # Build grading prompt
            grading_prompt = self._build_grading_prompt(
                essay_text,
                question_prompt,
                rubric,
                context
            )

            # Get grading from Claude
            response = self.client.messages.create(
                model=settings.primary_model,
                max_tokens=4096,
                temperature=0.3,  # Lower temperature for more consistent grading
                system=self.GRADING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": grading_prompt}]
            )

            feedback = response.content[0].text

            # Parse the response to extract scores (if structured)
            # For now, return full feedback
            return {
                "essay_text": essay_text,
                "question_prompt": question_prompt,
                "rubric": [
                    {
                        "name": c.name,
                        "description": c.description,
                        "max_points": c.max_points
                    }
                    for c in rubric
                ],
                "total_possible": GradingRubric.calculate_total_points(rubric),
                "feedback": feedback,
                "course_materials_used": len(relevant_materials) > 0
            }

        except Exception as e:
            logger.error(f"Error grading essay: {e}")
            return {
                "error": str(e),
                "feedback": "Unable to grade essay at this time. Please try again."
            }

    def grade_short_answer(
        self,
        answer_text: str,
        question: str,
        model_answer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Grade a short answer response

        Args:
            answer_text: Student's answer
            question: The question asked
            model_answer: Optional model answer for comparison

        Returns:
            Dictionary with grade and feedback
        """
        return self.grade_essay(
            essay_text=answer_text,
            question_prompt=question,
            assignment_type="short_answer"
        )

    def _build_grading_prompt(
        self,
        essay_text: str,
        question_prompt: str,
        rubric: List[RubricCriterion],
        context: str
    ) -> str:
        """Build the grading prompt for Claude"""
        rubric_text = GradingRubric.format_rubric(rubric)

        prompt = f"""Please grade the following student essay according to the rubric below.

ASSIGNMENT PROMPT:
{question_prompt}

GRADING RUBRIC:
{rubric_text}

RELEVANT COURSE MATERIALS:
{context}

STUDENT ESSAY:
{essay_text}

Please provide:
1. A score for each rubric criterion with justification
2. Overall comments on strengths
3. Specific areas for improvement
4. A total score
5. Encouraging closing remarks

Format your response clearly with sections for each rubric criterion."""

        return prompt

    def _format_course_context(self, retrieved_docs: List[Dict[str, Any]]) -> str:
        """Format retrieved course materials"""
        if not retrieved_docs:
            return "No specific course materials retrieved."

        context_parts = []
        for doc in retrieved_docs[:3]:  # Limit to top 3
            source = doc['metadata'].get('filename', 'Course material')
            text = doc['text'][:500]  # Limit length
            context_parts.append(f"[{source}]\n{text}...")

        return "\n\n".join(context_parts)

    def batch_grade(
        self,
        essays: List[Dict[str, str]],
        question_prompt: str,
        assignment_type: str = "essay"
    ) -> List[Dict[str, Any]]:
        """
        Grade multiple essays

        Args:
            essays: List of dicts with 'student_id' and 'essay_text'
            question_prompt: The assignment question
            assignment_type: Type of assignment

        Returns:
            List of grading results
        """
        results = []
        for essay_data in essays:
            result = self.grade_essay(
                essay_text=essay_data['essay_text'],
                question_prompt=question_prompt,
                assignment_type=assignment_type
            )
            result['student_id'] = essay_data.get('student_id', 'unknown')
            results.append(result)

        logger.info(f"Batch graded {len(essays)} essays")
        return results
