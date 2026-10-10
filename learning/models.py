from django.db import models
from concepts.models import Concept

class Lesson(models.Model):
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, help_text="Legacy content")
    structured_content = models.JSONField(default=dict, blank=True, help_text="Structured lesson data")
    difficulty = models.CharField(max_length=50, default="Intermediate")
    estimated_time = models.IntegerField(help_text="Estimated time in minutes", default=15)

    def __str__(self):
        return f"{self.concept.name} - {self.title}"
