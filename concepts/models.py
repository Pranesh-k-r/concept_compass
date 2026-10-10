from django.db import models

class Concept(models.Model):
    concept_id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    grade_band = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.concept_id}: {self.name}"

class Prerequisite(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='prerequisites')
    prerequisite_concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='dependent_concepts')

    class Meta:
        unique_together = ('concept', 'prerequisite_concept')

    def __str__(self):
        return f"{self.prerequisite_concept.concept_id} -> {self.concept.concept_id}"
