from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import QuizSession, Question, StudentResponse
from concepts.models import Concept, Prerequisite
from diagnostics.engine import DiagnosticEngine
import random

def subject_selection(request):
    return render(request, 'quizzes/subject_selection.html')

def start_quiz(request):
    # Use authenticated user if available
    student_id = request.user.username if request.user.is_authenticated else 'DEMO_STUDENT'
    subject = request.GET.get('subject', 'Mathematics')
    
    quiz_session = QuizSession.objects.create(student_id=student_id, subject=subject)
    
    # We will track answered concepts to avoid asking the exact same question
    request.session['answered_q_ids'] = []
    
    # Start by picking a random foundational question for the subject
    try:
        start_q = Question.objects.filter(subject=subject).first()
        if not start_q:
            start_q = Question.objects.first()
        request.session['next_q_id'] = start_q.question_id
    except:
        pass
        
    return redirect('quizzes:quiz_question', session_id=quiz_session.id)

def get_next_adaptive_question(current_question, is_correct, answered_q_ids, subject='Mathematics'):
    """
    Adaptive logic:
    If correct -> move to a harder question in the same concept, or move to a downstream concept.
    If incorrect -> move to an easier question, or move to a prerequisite concept.
    """
    if is_correct:
        # 1. Try harder question in same concept
        harder_q = Question.objects.filter(
            concept=current_question.concept, 
            difficulty='hard'
        ).exclude(question_id__in=answered_q_ids).first()
        if harder_q: return harder_q
        
        # 2. Try downstream concept
        downstream = Prerequisite.objects.filter(prerequisite_concept=current_question.concept).first()
        if downstream:
            down_q = Question.objects.filter(
                concept=downstream.concept
            ).exclude(question_id__in=answered_q_ids).first()
            if down_q: return down_q
    else:
        # 1. Try easier question in same concept
        easier_q = Question.objects.filter(
            concept=current_question.concept, 
            difficulty='easy'
        ).exclude(question_id__in=answered_q_ids).first()
        if easier_q: return easier_q
        
        # 2. Try prerequisite concept
        prereq = Prerequisite.objects.filter(concept=current_question.concept).first()
        if prereq:
            prereq_q = Question.objects.filter(
                concept=prereq.prerequisite_concept
            ).exclude(question_id__in=answered_q_ids).first()
            if prereq_q: return prereq_q
            
    # Fallback: pick any random unseen question
    unseen = Question.objects.filter(subject=subject).exclude(question_id__in=answered_q_ids)
    if unseen.exists():
        return random.choice(list(unseen))
    return None

def quiz_question(request, session_id):
    quiz_session = get_object_or_404(QuizSession, id=session_id)
    answered_q_ids = request.session.get('answered_q_ids', [])
    
    # We stop after 5 questions for the demo
    if len(answered_q_ids) >= 5:
        quiz_session.completed_at = timezone.now()
        quiz_session.save()
        
        # Give points if user is authenticated
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            profile.points += 50 # completion bonus
            profile.update_streak()
            profile.save()
            
        return redirect('quizzes:diagnostic_report', session_id=quiz_session.id)
        
    next_q_id = request.session.get('next_q_id')
    if not next_q_id:
        # Fallback if somehow lost
        unseen = Question.objects.filter(subject=quiz_session.subject).exclude(question_id__in=answered_q_ids)
        if unseen.exists():
            next_q_id = unseen.first().question_id
        else:
            return redirect('quizzes:diagnostic_report', session_id=quiz_session.id)
            
    question = get_object_or_404(Question, question_id=next_q_id)
    
    if request.method == 'POST':
        answer = request.POST.get('answer', '').strip()
        confidence = request.POST.get('confidence', '')
        is_correct = (answer.lower() == question.correct_answer.lower())
        
        StudentResponse.objects.create(
            session=quiz_session,
            question=question,
            response_text=answer,
            is_correct=is_correct,
            confidence_level=confidence
        )
        
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if is_correct:
                request.user.profile.points += 10
            else:
                # Still reward participation
                request.user.profile.points += 2
            request.user.profile.save()
        
        answered_q_ids.append(question.question_id)
        request.session['answered_q_ids'] = answered_q_ids
        
        # Calculate next question dynamically!
        next_q = get_next_adaptive_question(question, is_correct, answered_q_ids, subject=quiz_session.subject)
        if next_q:
            request.session['next_q_id'] = next_q.question_id
        
        return redirect('quizzes:quiz_question', session_id=quiz_session.id)
        
    return render(request, 'quizzes/question.html', {
        'question': question,
        'current_num': len(answered_q_ids) + 1,
        'total': 5
    })

def diagnostic_report(request, session_id):
    quiz_session = get_object_or_404(QuizSession, id=session_id)
    
    # 1. Overall Performance
    responses = quiz_session.responses.all()
    total_answered = responses.count()
    total_correct = sum(1 for r in responses if r.is_correct)
    total_incorrect = total_answered - total_correct
    percentage = (total_correct / total_answered * 100) if total_answered > 0 else 0
    
    # 2. Topic-wise Performance
    topics = {}
    incorrect_responses = []
    
    for r in responses:
        concept = r.question.concept
        if not r.is_correct:
            incorrect_responses.append(r)
            
        if concept:
            if concept.concept_id not in topics:
                topics[concept.concept_id] = {
                    'concept': concept,
                    'attempted': 0,
                    'correct': 0,
                    'incorrect': 0
                }
            topics[concept.concept_id]['attempted'] += 1
            if r.is_correct:
                topics[concept.concept_id]['correct'] += 1
            else:
                topics[concept.concept_id]['incorrect'] += 1
                
    for t in topics.values():
        t['accuracy'] = (t['correct'] / t['attempted'] * 100) if t['attempted'] > 0 else 0
        
    sorted_topics = sorted(topics.values(), key=lambda x: (x['accuracy'], -x['attempted']))
    
    try:
        engine = DiagnosticEngine()
        result = engine.diagnose(quiz_session)
        
        # Prerequisite Gap Detective
        gap_reports = []
        if request.user.is_authenticated:
            gap_reports = engine.get_gap_detective_data(quiz_session, request.user)
        
        # Update Mastery
        if request.user.is_authenticated and result.candidate_concept:
            from progress.models import ConceptMastery
            mastery, created = ConceptMastery.objects.get_or_create(
                student=request.user, 
                concept=result.candidate_concept
            )
            mastery.status = 'UNMASTERED'
            mastery.score = max(0, mastery.score - 20)
            mastery.save()
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
    
    from diagnostics.misconceptions import MisconceptionDetector
    misconceptions = []
    if request.user.is_authenticated:
        mc = MisconceptionDetector()
        misconceptions = mc.analyze_responses(request.user)
        
    # Prepare Chart.js data for current quiz
    import json
    chart_data = []
    for t in sorted_topics:
        if t['attempted'] == 0:
            color = '#9ca3af'
        elif t['accuracy'] < 50:
            color = '#ef4444'
        elif t['accuracy'] < 75:
            color = '#f97316'
        else:
            color = '#22c55e'
            
        chart_data.append({
            'label': t['concept'].name,
            'accuracy': t['accuracy'],
            'correct': t['correct'],
            'incorrect': t['incorrect'],
            'attempted': t['attempted'],
            'color': color
        })
    
    return render(request, 'quizzes/report.html', {
        'session': quiz_session,
        'result': result.to_dict(),
        'candidate_concept': result.candidate_concept,
        'total_answered': total_answered,
        'total_correct': total_correct,
        'total_incorrect': total_incorrect,
        'percentage': round(percentage),
        'topics': sorted_topics,
        'incorrect_responses': incorrect_responses,
        'misconceptions': misconceptions,
        'chart_data': json.dumps(chart_data),
        'gap_reports': gap_reports
    })
