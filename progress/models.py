from django.db import models
from concepts.models import Concept
from django.contrib.auth.models import User

class ConceptMastery(models.Model):
    MASTERY_CHOICES = [
        ('MASTERED', 'Mastered'),
        ('UNMASTERED', 'Unmastered'),
        ('UNCERTAIN', 'Uncertain'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mastery_records')
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=MASTERY_CHOICES, default='UNCERTAIN')
    score = models.FloatField(default=50.0) # 0 to 100
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'concept')
        
    def __str__(self):
        return f"{self.student.username} - {self.concept.name}: {self.status}"

class StudyPlan(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ARCHIVED', 'Archived'),
    ]
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='study_plans')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    daily_time_budget = models.IntegerField(default=15) # minutes
    subject = models.CharField(max_length=100, default='Mathematics')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

class StudyTask(models.Model):
    TASK_TYPES = [
        ('LEARN', 'Learn'),
        ('PRACTICE', 'Practice'),
        ('DIAGNOSTIC', 'Diagnostic Check'),
        ('VERIFICATION', 'Verification'),
    ]
    STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]
    plan = models.ForeignKey(StudyPlan, on_delete=models.CASCADE, related_name='tasks')
    concept = models.ForeignKey(Concept, on_delete=models.CASCADE)
    task_type = models.CharField(max_length=20, choices=TASK_TYPES)
    sequence = models.IntegerField(default=1)
    estimated_duration = models.IntegerField(default=5) # minutes
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='NOT_STARTED')
    completed_at = models.DateTimeField(null=True, blank=True)
    explanation = models.TextField(blank=True, null=True)
