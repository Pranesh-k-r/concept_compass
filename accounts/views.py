from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from quizzes.models import QuizSession, StudentResponse
from concepts.models import Concept
from django.db.models import Count, Q

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Set is_teacher if a special code was provided, etc. (skipping for simplicity)
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def teacher_dashboard(request):
    if not hasattr(request.user, 'profile') or not request.user.profile.is_teacher:
        return redirect('dashboard')
        
    # Gather class analytics from QuizSessions since student_id is a CharField
    from quizzes.models import QuizSession, StudentResponse
    from concepts.models import Concept
    from diagnostics.priority import LearningPriorityEngine
    
    subject = request.GET.get('subject', 'Mathematics')
    
    # Get all distinct student IDs that have taken a quiz for this subject
    student_ids = QuizSession.objects.filter(subject=subject).values_list('student_id', flat=True).distinct()
    
    # Filter out teachers if possible (just filtering out the current user for demo)
    student_ids = [sid for sid in student_ids if sid != request.user.username]
    total_students = len(student_ids)
    
    responses = StudentResponse.objects.filter(session__student_id__in=student_ids, session__subject=subject)
    total_resp = responses.count()
    overall_accuracy = round(responses.filter(is_correct=True).count() / total_resp * 100) if total_resp > 0 else 0
    
    # Class Performance Heatmap (Rows: Students, Cols: Topics)
    engine = LearningPriorityEngine()
    concepts = Concept.objects.filter(subject=subject).order_by('concept_id')
    heatmap = []
    interventions = []
    
    # We need a mock user object for the priority engine since it expects an object with .username
    class MockUser:
        def __init__(self, username):
            self.username = username
            self.is_authenticated = True
            
    for sid in student_ids:
        s_data = {'student': sid, 'topics': {}}
        mock_user = MockUser(sid)
        student_priorities = engine.rank_priorities(mock_user, subject=subject)
        
        # Get active plan for this student
        from progress.models import StudyPlan
        try:
            plan = StudyPlan.objects.get(student__username=sid, status='ACTIVE', subject=subject)
            plan_progress = round(plan.tasks.filter(status='COMPLETED').count() / plan.tasks.count() * 100) if plan.tasks.count() > 0 else 0
        except StudyPlan.DoesNotExist:
            plan_progress = None
            
        s_data['plan_progress'] = plan_progress
        
        for p in student_priorities:
            s_data['topics'][p['concept'].name] = p
            
            if p['rank'] <= 1: # Study First or Study Next (Needs Support)
                interventions.append({
                    'student': sid,
                    'topic': p['concept'].name,
                    'concept_id': p['concept'].concept_id,
                    'accuracy': p['accuracy'],
                    'attempted': p['attempted'],
                    'rank': p['rank'],
                    'plan_progress': plan_progress
                })
                
        heatmap.append(s_data)
        
    return render(request, 'accounts/teacher_dashboard.html', {
        'total_students': total_students,
        'overall_accuracy': overall_accuracy,
        'heatmap': heatmap,
        'concepts': concepts,
        'interventions': interventions,
        'current_subject': subject
    })
