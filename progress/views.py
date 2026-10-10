from django.shortcuts import render
from quizzes.models import QuizSession

def landing_page(request):
    return render(request, 'landing.html')

def dashboard(request):
    student_id = request.session.get('student_id', 'DEMO_STUDENT')
    if request.user.is_authenticated:
        student_id = request.user.username
    request.session['student_id'] = student_id
    
    subject = request.GET.get('subject', 'Mathematics')
    recent_sessions = QuizSession.objects.filter(student_id=student_id, subject=subject).order_by('-started_at')[:5]
    
    priorities = []
    if request.user.is_authenticated:
        from diagnostics.priority import LearningPriorityEngine
        engine = LearningPriorityEngine()
        priorities = engine.rank_priorities(request.user, subject=subject)
    
    return render(request, 'dashboard.html', {
        'student_id': student_id,
        'recent_sessions': recent_sessions,
        'priorities': priorities,
        'current_subject': subject
    })

def history(request):
    student_id = request.session.get('student_id', 'DEMO_STUDENT')
    if request.user.is_authenticated:
        student_id = request.user.username
        
    subject = request.GET.get('subject', 'Mathematics')
    all_sessions = QuizSession.objects.filter(student_id=student_id, subject=subject).order_by('-started_at')
    
    total_quizzes = all_sessions.filter(completed_at__isnull=False).count()
    from quizzes.models import StudentResponse
    responses = StudentResponse.objects.filter(session__student_id=student_id, session__subject=subject)
    total_questions = responses.count()
    overall_accuracy = 0
    if total_questions > 0:
        overall_accuracy = round((responses.filter(is_correct=True).count() / total_questions) * 100)
        
    from .models import ConceptMastery
    mastered_count = 0
    if request.user.is_authenticated:
        mastered_count = ConceptMastery.objects.filter(student=request.user, concept__subject=subject, status='MASTERED').count()
        
    from diagnostics.priority import LearningPriorityEngine
    engine = LearningPriorityEngine()
    topics_progress = []
    if request.user.is_authenticated:
        topics_progress = engine.rank_priorities(request.user, subject=subject)
        
    # Prepare Analytics Data
    import json
    from concepts.models import Prerequisite
    
    # Prereq Bar Chart
    prereq_ids = set(Prerequisite.objects.values_list('prerequisite_concept_id', flat=True))
    bar_data = []
    for t in topics_progress:
        if t['concept'].concept_id in prereq_ids and t['rank'] < 3: # Exclude insufficient evidence
            color = '#ef4444' if t['rank'] == 0 else ('#f97316' if t['rank'] == 1 else '#22c55e')
            bar_data.append({
                'label': t['concept'].name,
                'accuracy': t['accuracy'],
                'color': color,
                'attempted': t['attempted']
            })
    bar_data.sort(key=lambda x: x['accuracy'])
    
    # Scatter Plot Data
    all_prereqs = Prerequisite.objects.select_related('prerequisite_concept', 'concept')
    topic_map = {t['concept'].concept_id: t for t in topics_progress}
    scatter_data = []
    heatmap_data = {}
    
    for p in all_prereqs:
        p_id = p.prerequisite_concept.concept_id
        t_id = p.concept.concept_id
        if p_id in topic_map and t_id in topic_map:
            p_metrics = topic_map[p_id]
            t_metrics = topic_map[t_id]
            if p_metrics['rank'] < 3 and t_metrics['rank'] < 3:
                scatter_data.append({
                    'x': p_metrics['accuracy'],
                    'y': t_metrics['accuracy'],
                    'p_name': p.prerequisite_concept.name,
                    't_name': p.concept.name,
                    'p_att': p_metrics['attempted'],
                    't_att': t_metrics['attempted']
                })
                
                # Build heatmap matrix
                if p.prerequisite_concept.name not in heatmap_data:
                    heatmap_data[p.prerequisite_concept.name] = {}
                
                gap_score = max(0, t_metrics['accuracy'] - p_metrics['accuracy'])
                color_class = 'gap-none'
                if p_metrics['rank'] == 0 and t_metrics['rank'] == 0: color_class = 'gap-high'
                elif p_metrics['rank'] <= 1: color_class = 'gap-med'
                
                heatmap_data[p.prerequisite_concept.name][p.concept.name] = {
                    'score': gap_score,
                    'class': color_class,
                    'p_acc': p_metrics['accuracy'],
                    't_acc': t_metrics['accuracy']
                }

    target_names = sorted(list(set(t_id for p_id in heatmap_data.values() for t_id in p_id.keys())))
        
    return render(request, 'progress/history.html', {
        'sessions': all_sessions,
        'total_quizzes': total_quizzes,
        'total_questions': total_questions,
        'overall_accuracy': overall_accuracy,
        'mastered_count': mastered_count,
        'topics_progress': topics_progress,
        'bar_data': json.dumps(bar_data),
        'scatter_data': json.dumps(scatter_data),
        'heatmap_data': heatmap_data,
        'heatmap_targets': target_names
    })

def concept_graph(request):
    from concepts.models import Concept, Prerequisite
    from diagnostics.priority import LearningPriorityEngine
    
    concepts = Concept.objects.all()
    prereqs = Prerequisite.objects.all()
    
    priorities = {}
    if request.user.is_authenticated:
        engine = LearningPriorityEngine()
        results = engine.rank_priorities(request.user)
        for r in results:
            priorities[r['concept'].concept_id] = r
            
    nodes = []
    for c in concepts:
        p_data = priorities.get(c.concept_id, {
            'attempted': 0, 'correct': 0, 'incorrect': 0, 'accuracy': 0, 'category': 'Take a Few More Questions', 'rank': 3, 'reason': 'No evidence available.'
        })
        
        color = '#ffffff' # Default / Insufficient evidence (Gray/White)
        if p_data['rank'] == 0: color = '#fee2e2' # Red - Study First
        elif p_data['rank'] == 1: color = '#ffedd5' # Orange - Study Next
        elif p_data['rank'] == 2: color = '#d1fae5' # Green - Review
        
        nodes.append({
            'id': c.concept_id, 
            'label': c.name,
            'color': {'background': color, 'border': '#4f46e5'},
            'metrics': {
                'attempted': p_data.get('attempted', 0),
                'correct': p_data.get('correct', 0),
                'incorrect': p_data.get('incorrect', 0),
                'accuracy': p_data.get('accuracy', 0),
                'status': p_data.get('category', 'Take a Few More Questions'),
                'reason': p_data.get('reason', 'No evidence available.')
            }
        })
        
    edges = [{'from': p.prerequisite_concept.concept_id, 'to': p.concept.concept_id} for p in prereqs]
    
    import json
    return render(request, 'progress/graph.html', {
        'nodes_json': json.dumps(nodes),
        'edges_json': json.dumps(edges)
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

@login_required
def study_plan(request):
    from diagnostics.study_planner import StudyPlanner
    planner = StudyPlanner()
    
    subject = request.GET.get('subject', 'Mathematics')
    
    if request.method == 'POST':
        budget = request.POST.get('time_budget')
        subject = request.POST.get('subject', 'Mathematics')
        if budget:
            try:
                plan = planner.get_or_create_plan(request.user, int(budget), subject)
                planner.update_budget(plan, int(budget))
            except ValueError:
                pass
        return redirect(f"/progress/plan/?subject={subject}")
        
    plan = planner.get_or_create_plan(request.user, subject=subject)
    tasks = plan.tasks.all().order_by('sequence')
    
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(status='COMPLETED').count()
    progress_percentage = round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0)
    
    return render(request, 'progress/study_plan.html', {
        'plan': plan,
        'tasks': tasks,
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'progress_percentage': progress_percentage,
        'current_subject': subject
    })

@login_required
def mark_task_complete(request, task_id):
    from diagnostics.study_planner import StudyPlanner
    planner = StudyPlanner()
    planner.mark_complete(task_id, request.user)
    return redirect('progress:study_plan')
