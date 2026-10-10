from django.test import TestCase
from django.urls import reverse
from concepts.models import Concept
from learning.models import Lesson
from learning.solver import SafeMathSolver

class SolverTests(TestCase):
    def setUp(self):
        self.solver = SafeMathSolver()

    def test_solve_arithmetic(self):
        res = self.solver.solve("5+3*2")
        self.assertIn("steps", res)
        self.assertEqual(len(res["steps"]), 5) # Expression, Calc *, New expr, Calc +, New expr
        
    def test_solve_equation_ax_b(self):
        res = self.solver.solve("3x=15")
        self.assertIn("steps", res)
        self.assertIn("x = 5", res["steps"][-1])
        
    def test_solve_equation_x_a_b(self):
        res = self.solver.solve("x+5=12")
        self.assertIn("steps", res)
        self.assertIn("x = 7", res["steps"][-1])
        
    def test_unsupported_equation(self):
        res = self.solver.solve("x^2=4")
        self.assertIn("error", res)
        
    def test_invalid_chars(self):
        res = self.solver.solve("import os; os.system('ls')")
        self.assertIn("error", res)

class LessonTests(TestCase):
    def setUp(self):
        self.concept = Concept.objects.create(concept_id="C_TEST", name="Test Concept", subject="Math", grade_band="G1")
        self.lesson = Lesson.objects.create(concept=self.concept, structured_content={"explanation": "Test explanation"})

    def test_lesson_view(self):
        url = reverse('learning:lesson', args=['C_TEST'])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test explanation")
