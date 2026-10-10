from django.test import TestCase
from django.urls import reverse
from quizzes.models import QuizSession, Question, StudentResponse
from concepts.models import Concept

class DiagnosticReportTests(TestCase):
    def setUp(self):
        self.concept = Concept.objects.create(concept_id="C01", name="Fractions")
        self.q1 = Question.objects.create(question_id="Q01", concept=self.concept, question_text="1/2 + 1/2?", correct_answer="1")
        self.q2 = Question.objects.create(question_id="Q02", concept=self.concept, question_text="1/4 + 1/4?", correct_answer="1/2")
        self.session = QuizSession.objects.create(student_id="test_student")

    def test_all_correct_quiz(self):
        StudentResponse.objects.create(session=self.session, question=self.q1, response_text="1", is_correct=True)
        StudentResponse.objects.create(session=self.session, question=self.q2, response_text="1/2", is_correct=True)
        
        url = reverse('quizzes:diagnostic_report', args=[self.session.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['percentage'], 100)
        self.assertEqual(response.context['total_correct'], 2)
        self.assertEqual(response.context['total_incorrect'], 0)

    def test_all_incorrect_quiz(self):
        StudentResponse.objects.create(session=self.session, question=self.q1, response_text="3", is_correct=False)
        StudentResponse.objects.create(session=self.session, question=self.q2, response_text="4", is_correct=False)
        
        url = reverse('quizzes:diagnostic_report', args=[self.session.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['percentage'], 0)
        self.assertEqual(response.context['total_incorrect'], 2)

    def test_mixed_score_quiz(self):
        StudentResponse.objects.create(session=self.session, question=self.q1, response_text="1", is_correct=True)
        StudentResponse.objects.create(session=self.session, question=self.q2, response_text="4", is_correct=False)
        
        url = reverse('quizzes:diagnostic_report', args=[self.session.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['percentage'], 50)
        self.assertEqual(response.context['total_correct'], 1)
        self.assertEqual(response.context['total_incorrect'], 1)

class PriorityEngineTests(TestCase):
    def setUp(self):
        from django.contrib.auth.models import User
        self.user = User.objects.create_user(username='priority_test')
        self.concept = Concept.objects.create(concept_id="C01", name="Fractions")
        self.q1 = Question.objects.create(question_id="Q01", concept=self.concept, question_text="1/2 + 1/2?", correct_answer="1")
        self.session = QuizSession.objects.create(student_id=self.user.username)
        
    def test_more_evidence_needed(self):
        from diagnostics.priority import LearningPriorityEngine
        StudentResponse.objects.create(session=self.session, question=self.q1, response_text="3", is_correct=False)
        engine = LearningPriorityEngine(min_evidence=2)
        results = engine.rank_priorities(self.user)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category'], 'Take a Few More Questions')
        
    def test_focus_first(self):
        from diagnostics.priority import LearningPriorityEngine
        self.q2 = Question.objects.create(question_id="Q02", concept=self.concept, question_text="1/4 + 1/4?", correct_answer="1/2")
        StudentResponse.objects.create(session=self.session, question=self.q1, response_text="3", is_correct=False)
        StudentResponse.objects.create(session=self.session, question=self.q2, response_text="4", is_correct=False)
        
        engine = LearningPriorityEngine(min_evidence=2)
        results = engine.rank_priorities(self.user)
        self.assertEqual(results[0]['category'], 'Study First')
        self.assertEqual(results[0]['rank'], 0)
