from django.db import models
from concepts.models import Concept

class Question(models.Model):
    question_id = models.CharField(max_length=50, primary_key=True)
    question_tag = models.CharField(max_length=100)
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    correct_answer = models.CharField(max_length=255)
    common_distractor = models.CharField(max_length=255, blank=True, null=True)
    difficulty = models.CharField(max_length=50)
    subject = models.CharField(max_length=100)
    grade_band = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.question_id}: {self.question_tag}"

class QuizSession(models.Model):
    student_id = models.CharField(max_length=50)
    subject = models.CharField(max_length=100, default='Mathematics')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_evaluation = models.BooleanField(default=False)

    def __str__(self):
        return f"Session {self.id} for {self.student_id}"

class StudentResponse(models.Model):
    session = models.ForeignKey(QuizSession, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    response_text = models.CharField(max_length=255)
    is_correct = models.BooleanField()
    time_seconds = models.FloatField(null=True, blank=True)
    hints_used = models.IntegerField(default=0)
    attempt_number = models.IntegerField(default=1)
    confidence_level = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response to {self.question.question_id}: {'Correct' if self.is_correct else 'Incorrect'}"
