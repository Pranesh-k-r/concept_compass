from progress.models import StudyPlan, StudyTask
from concepts.models import Concept
from diagnostics.priority import LearningPriorityEngine
from diagnostics.engine import DiagnosticEngine
from quizzes.models import StudentResponse, QuizSession

class StudyPlanner:
    def get_or_create_plan(self, user, time_budget=15, subject='Mathematics'):
        plan, created = StudyPlan.objects.get_or_create(
            student=user, 
            status='ACTIVE', 
            subject=subject,
            defaults={'daily_time_budget': time_budget}
        )
        if created or plan.tasks.filter(status='NOT_STARTED').count() == 0:
            self.generate_tasks(plan, subject)
        return plan

    def update_budget(self, plan, time_budget):
        plan.daily_time_budget = time_budget
        plan.save()

    def mark_complete(self, task_id, user):
        try:
            task = StudyTask.objects.get(id=task_id, plan__student=user)
            task.status = 'COMPLETED'
            from django.utils import timezone
            task.completed_at = timezone.now()
            task.save()
            
            # Check if plan is fully complete
            if not task.plan.tasks.exclude(status='COMPLETED').exists():
                task.plan.status = 'COMPLETED'
                task.plan.save()
        except:
            pass

    def generate_tasks(self, plan, subject='Mathematics'):
        # 1. Clear existing unstarted tasks
        plan.tasks.filter(status='NOT_STARTED').delete()
        
        # 2. Get priorities
        priority_engine = LearningPriorityEngine()
        priorities = priority_engine.rank_priorities(plan.student, subject=subject)
        
        # 3. Get Gap Data and Revision Data
        diagnostic_engine = DiagnosticEngine()
        recent_sessions = QuizSession.objects.filter(student_id=plan.student.username, subject=subject).order_by('-started_at')
        
        gap_reports = []
        if recent_sessions.exists():
            gap_reports = diagnostic_engine.get_gap_detective_data(recent_sessions.first(), plan.student)

        sequence = 1
        
        # 3.5 SMART REVISION REMINDER
        # Find incorrect responses in the past 7 days
        from django.utils import timezone
        import datetime
        seven_days_ago = timezone.now() - datetime.timedelta(days=7)
        incorrect_responses = StudentResponse.objects.filter(
            session__student_id=plan.student.username,
            session__subject=subject,
            is_correct=False,
            created_at__gte=seven_days_ago
        ).select_related('question__concept')
        
        # Track concepts already added for revision to avoid duplicates
        revision_concepts = set()
        
        for r in incorrect_responses:
            concept = r.question.concept
            if concept.concept_id in revision_concepts:
                continue
                
            days_since = (timezone.now() - r.created_at).days
            # Spaced repetition: 1, 3, or 7 days
            if days_since in [1, 3, 7]:
                self._add_task(
                    plan, 
                    concept, 
                    'PRACTICE', 
                    sequence, 
                    5, 
                    'High', 
                    f"Revision: You struggled with this {days_since} day(s) ago. Let's try again!"
                )
                sequence += 1
                revision_concepts.add(concept.concept_id)

        # 4. Create tasks
        for gr in gap_reports:
            # If there's an earliest gap
            if gr.get('earliest_gap'):
                gap = gr['earliest_gap']
                concept = gap['concept']
                if gap['status'] == 'unassessed':
                    self._add_task(plan, concept, 'DIAGNOSTIC', sequence, 5, 'High', f"Checking your understanding of {concept.name}")
                else:
                    self._add_task(plan, concept, 'LEARN', sequence, 10, 'High', f"Revise {concept.name} to fix a foundational gap.")
                    self._add_task(plan, concept, 'PRACTICE', sequence+1, 10, 'High', f"Practise {concept.name}.")
                sequence += 2
                
            # Then practice the target
            self._add_task(plan, gr['target'], 'LEARN', sequence, 10, 'Medium', f"Review {gr['target'].name} after addressing foundations.")
            sequence += 1
            
        # Add basic priorities if no gaps or just to fill out schedule
        for p in priorities[:4]:
            concept = p['concept']
            if p['category'] in ['Study First', 'Study Next']:
                self._add_task(plan, concept, 'LEARN', sequence, 10, 'Medium', p['reason'])
                self._add_task(plan, concept, 'PRACTICE', sequence+1, 10, 'Medium', "Practise what you learned.")
                sequence += 2
            else:
                self._add_task(plan, concept, 'PRACTICE', sequence, 10, 'Low', p['reason'])
                sequence += 1

    def _add_task(self, plan, concept, task_type, sequence, duration, priority, explanation):
        # Prevent exact duplicates that are incomplete
        if StudyTask.objects.filter(plan=plan, concept=concept, task_type=task_type, status__in=['NOT_STARTED', 'IN_PROGRESS']).exists():
            return
            
        StudyTask.objects.create(
            plan=plan,
            concept=concept,
            task_type=task_type,
            sequence=sequence,
            estimated_duration=duration,
            priority=priority,
            explanation=explanation
        )
