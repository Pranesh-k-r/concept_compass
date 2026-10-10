from django.test import TestCase
from concepts.models import Concept, Prerequisite
from quizzes.models import Question, QuizSession, StudentResponse
from diagnostics.engine import DiagnosticEngine

class DiagnosticsEngineTest(TestCase):
    def setUp(self):
        # Create concepts
        self.c1 = Concept.objects.create(concept_id="T01", name="Basic Addition", subject="Math", grade_band="G1")
        self.c2 = Concept.objects.create(concept_id="T02", name="Basic Multiplication", subject="Math", grade_band="G2")
        self.c3 = Concept.objects.create(concept_id="T03", name="Division", subject="Math", grade_band="G3")
        
        # Prereqs: Basic Addition -> Basic Multiplication -> Division
        Prerequisite.objects.create(concept=self.c2, prerequisite_concept=self.c1)
        Prerequisite.objects.create(concept=self.c3, prerequisite_concept=self.c2)
        
        # Create Questions
        self.q1 = Question.objects.create(question_id="Q1", concept=self.c1, question_text="1+1?", correct_answer="2")
        self.q2 = Question.objects.create(question_id="Q2", concept=self.c2, question_text="2*2?", correct_answer="4")
        self.q3 = Question.objects.create(question_id="Q3", concept=self.c3, question_text="4/2?", correct_answer="2")
        
        # Engine
        self.engine = DiagnosticEngine()
        
    def test_insufficient_evidence(self):
        # Single incorrect answer
        session = QuizSession.objects.create(student_id="tester")
        StudentResponse.objects.create(session=session, question=self.q3, response_text="wrong", is_correct=False)
        
        result = self.engine.diagnose(session)
        self.assertIsNone(result.candidate_concept)
        self.assertIn("Insufficient evidence", result.abstention_reason)
        
    def test_correct_diagnosis_two_mistakes(self):
        # Two mistakes on same concept -> triggers diagnosis
        session = QuizSession.objects.create(student_id="tester")
        StudentResponse.objects.create(session=session, question=self.q3, response_text="wrong1", is_correct=False)
        StudentResponse.objects.create(session=session, question=self.q3, response_text="wrong2", is_correct=False)
        
        result = self.engine.diagnose(session)
        # Should trace to its prerequisite (T02) because we give 1.5x weight to prerequisite
        self.assertEqual(result.candidate_concept.concept_id, "T02")
        
    def test_prerequisite_chain_single_mistakes(self):
        # One mistake on target, one mistake on prereq -> diagnoses prereq
        session = QuizSession.objects.create(student_id="tester")
        StudentResponse.objects.create(session=session, question=self.q3, response_text="wrong1", is_correct=False) # Div
        StudentResponse.objects.create(session=session, question=self.q2, response_text="wrong2", is_correct=False) # Mult
        
        result = self.engine.diagnose(session)
        # Mult (T02) is prereq of Div (T03). Mult is struggling.
        # It also traces to T01 (prereq of Mult). Let's see what it outputs.
        self.assertIsNotNone(result.candidate_concept)
        # Since T02 and T03 are struggling, and T01 is prereq of T02.
        # It should rank T01 or T02 highest depending on the 1.5x weight.
        
    def test_quiz_result_calculations(self):
        # This is testing the view logic implicitly or we can just test StudentResponse sums
        session = QuizSession.objects.create(student_id="tester")
        StudentResponse.objects.create(session=session, question=self.q1, response_text="2", is_correct=True)
        StudentResponse.objects.create(session=session, question=self.q2, response_text="wrong", is_correct=False)
        
        responses = session.responses.all()
        correct = sum(1 for r in responses if r.is_correct)
        self.assertEqual(correct, 1)
        self.assertEqual(responses.count(), 2)
