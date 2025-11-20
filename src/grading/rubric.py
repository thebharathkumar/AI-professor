"""
Grading rubric definitions for different assignment types
"""
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class RubricCriterion:
    """A single grading criterion"""
    name: str
    description: str
    max_points: float
    weight: float = 1.0


class GradingRubric:
    """Rubric for grading assignments"""

    # Standard ethics essay rubric
    ETHICS_ESSAY_RUBRIC = [
        RubricCriterion(
            name="Thesis and Argument",
            description="Clear thesis statement and coherent argument structure",
            max_points=25.0
        ),
        RubricCriterion(
            name="Ethical Framework Application",
            description="Appropriate use of ethical theories and frameworks (e.g., utilitarianism, deontology, virtue ethics)",
            max_points=25.0
        ),
        RubricCriterion(
            name="Evidence and Examples",
            description="Use of relevant examples, case studies, or evidence to support arguments",
            max_points=20.0
        ),
        RubricCriterion(
            name="Critical Thinking",
            description="Demonstrates critical analysis, considers counterarguments, shows depth of thought",
            max_points=15.0
        ),
        RubricCriterion(
            name="Writing Quality",
            description="Clear writing, proper grammar, logical organization, professional tone",
            max_points=10.0
        ),
        RubricCriterion(
            name="Course Material Integration",
            description="Effective integration of course readings, lectures, and discussions",
            max_points=5.0
        )
    ]

    # Short answer rubric
    SHORT_ANSWER_RUBRIC = [
        RubricCriterion(
            name="Accuracy",
            description="Correctness and accuracy of information",
            max_points=40.0
        ),
        RubricCriterion(
            name="Completeness",
            description="Addresses all parts of the question",
            max_points=30.0
        ),
        RubricCriterion(
            name="Clarity",
            description="Clear and concise expression of ideas",
            max_points=20.0
        ),
        RubricCriterion(
            name="Examples",
            description="Use of relevant examples or applications",
            max_points=10.0
        )
    ]

    @classmethod
    def get_rubric(cls, assignment_type: str) -> List[RubricCriterion]:
        """
        Get the appropriate rubric for an assignment type

        Args:
            assignment_type: Type of assignment ('essay', 'short_answer', etc.)

        Returns:
            List of rubric criteria
        """
        rubrics = {
            'essay': cls.ETHICS_ESSAY_RUBRIC,
            'short_answer': cls.SHORT_ANSWER_RUBRIC
        }
        return rubrics.get(assignment_type, cls.SHORT_ANSWER_RUBRIC)

    @classmethod
    def calculate_total_points(cls, rubric: List[RubricCriterion]) -> float:
        """Calculate total possible points for a rubric"""
        return sum(criterion.max_points * criterion.weight for criterion in rubric)

    @classmethod
    def format_rubric(cls, rubric: List[RubricCriterion]) -> str:
        """Format rubric as a string for display"""
        lines = ["Grading Rubric:", ""]
        for criterion in rubric:
            lines.append(f"- {criterion.name} ({criterion.max_points} points)")
            lines.append(f"  {criterion.description}")
            lines.append("")
        lines.append(f"Total: {cls.calculate_total_points(rubric)} points")
        return "\n".join(lines)
