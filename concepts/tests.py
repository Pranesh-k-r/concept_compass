from django.test import TestCase
from concepts.models import Concept, Prerequisite

class ConceptModelTest(TestCase):
    def setUp(self):
        self.c1 = Concept.objects.create(concept_id="C1", name="Basic Math", subject="Math", grade_band="7")
        self.c2 = Concept.objects.create(concept_id="C2", name="Advanced Math", subject="Math", grade_band="7")
        Prerequisite.objects.create(concept=self.c2, prerequisite_concept=self.c1)

    def test_concept_creation(self):
        self.assertEqual(self.c1.name, "Basic Math")
        self.assertEqual(self.c2.name, "Advanced Math")

    def test_prerequisite_relationship(self):
        prereqs = Prerequisite.objects.filter(concept=self.c2)
        self.assertEqual(prereqs.count(), 1)
        self.assertEqual(prereqs.first().prerequisite_concept, self.c1)
