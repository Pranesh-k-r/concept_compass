from django.shortcuts import render, redirect, get_object_or_404
from concepts.models import Concept
from quizzes.models import Question
import random

def targeted_lesson(request, concept_id):
    concept = get_object_or_404(Concept, concept_id=concept_id)
    
    from .models import Lesson
    from progress.models import ConceptMastery
    from concepts.models import Prerequisite
    
    db_lesson = Lesson.objects.filter(concept=concept).first()
    
    prereq_gaps = []
    if request.user.is_authenticated:
        prereqs = Prerequisite.objects.filter(concept=concept)
        for p in prereqs:
            mastery = ConceptMastery.objects.filter(student=request.user, concept=p.prerequisite_concept).first()
            if mastery:
                if mastery.status == 'UNMASTERED' or mastery.score < 40:
                    prereq_gaps.append({
                        'concept': p.prerequisite_concept,
                        'status': 'confirmed'
                    })
                elif mastery.status == 'UNCERTAIN':
                    prereq_gaps.append({
                        'concept': p.prerequisite_concept,
                        'status': 'suspected'
                    })
    
    # Concept Explorer: Related Concepts
    prerequisites = [p.prerequisite_concept for p in Prerequisite.objects.filter(concept=concept)]
    next_steps = [p.concept for p in Prerequisite.objects.filter(prerequisite_concept=concept)]
    
    structured_data = db_lesson.structured_content if (db_lesson and db_lesson.structured_content) else None
    
    # Mark LEARN task as completed if it exists
    if request.user.is_authenticated:
        from progress.models import StudyTask
        active_task = StudyTask.objects.filter(
            plan__student=request.user,
            concept=concept,
            task_type='LEARN',
            status__in=['NOT_STARTED', 'IN_PROGRESS']
        ).first()
        if active_task:
            active_task.status = 'COMPLETED'
            from django.utils import timezone
            active_task.completed_at = timezone.now()
            active_task.save()
            
    return render(request, 'learning/lesson.html', {
        'concept': concept,
        'db_lesson': db_lesson,
        'structured_data': structured_data,
        'prereq_gaps': prereq_gaps,
        'prerequisites': prerequisites,
        'next_steps': next_steps
    })

from django.http import JsonResponse
import json
from .solver import SafeMathSolver

def api_solve_problem(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            expression = data.get('expression', '')
            solver = SafeMathSolver()
            result = solver.solve(expression)
            return JsonResponse(result)
        except Exception as e:
            return JsonResponse({'error': 'Invalid request.'}, status=400)
    return JsonResponse({'error': 'Only POST allowed.'}, status=405)

def practice(request, concept_id):
    concept = get_object_or_404(Concept, concept_id=concept_id)
    # Pick a random question for this concept
    questions = list(Question.objects.filter(concept=concept))
    
    if not questions:
        # Fallback if no questions
        return render(request, 'learning/practice.html', {
            'concept': concept,
            'error': 'No practice questions available for this concept.'
        })
        
    question = random.choice(questions)
    
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        is_correct = (answer.lower() == request.POST.get('correct_answer', '').lower())
        
        if request.user.is_authenticated and is_correct:
            from progress.models import StudyTask
            active_task = StudyTask.objects.filter(
                plan__student=request.user,
                concept=concept,
                task_type='PRACTICE',
                status__in=['NOT_STARTED', 'IN_PROGRESS']
            ).first()
            if active_task:
                active_task.status = 'COMPLETED'
                from django.utils import timezone
                active_task.completed_at = timezone.now()
                active_task.save()
        
        return render(request, 'learning/practice_result.html', {
            'concept': concept,
            'question': question,
            'is_correct': is_correct,
            'submitted_answer': answer
        })

    # Prepare options
    options = []
    if question.common_distractor:
        options = [question.correct_answer, question.common_distractor]
        random.shuffle(options)

    return render(request, 'learning/practice.html', {
        'concept': concept,
        'question': question,
        'options': options
    })

def verify(request, concept_id):
    concept = get_object_or_404(Concept, concept_id=concept_id)
    questions = list(Question.objects.filter(concept=concept))
    
    if not questions:
        return redirect('dashboard')
        
    question = random.choice(questions)
    
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        is_correct = (answer.lower() == request.POST.get('correct_answer', '').lower())
        
        # Update Mastery if authenticated
        if request.user.is_authenticated:
            from progress.models import ConceptMastery
            mastery, created = ConceptMastery.objects.get_or_create(
                student=request.user, 
                concept=concept
            )
            if is_correct:
                mastery.status = 'MASTERED'
                mastery.score = min(100, mastery.score + 30)
            else:
                mastery.status = 'UNMASTERED'
                mastery.score = max(0, mastery.score - 10)
            mastery.save()
            
            # Award points on success
            if is_correct and hasattr(request.user, 'profile'):
                request.user.profile.points += 20
                request.user.profile.save()
        
        return render(request, 'learning/verify_result.html', {
            'concept': concept,
            'is_correct': is_correct
        })

    return render(request, 'learning/verify.html', {
        'concept': concept,
        'question': question
    })
