from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Conversation, Message
from .service import AILearningAssistant
from quizzes.models import Question, StudentResponse
from progress.models import StudyPlan, StudyTask

@login_required
def chat_interface(request):
    # Get or create the active conversation
    conversation = Conversation.objects.filter(student=request.user).order_by('-updated_at').first()
    
    if not conversation:
        conversation = Conversation.objects.create(
            student=request.user,
            title="Learning Assistant"
        )
        
    if request.method == 'POST':
        # Handle settings update
        subject = request.POST.get('subject')
        grade = request.POST.get('grade')
        language = request.POST.get('language')
        if subject: conversation.subject = subject
        if grade: conversation.grade = grade
        if language: conversation.language = language
        conversation.save()
        return redirect('assistant:chat')

    chat_messages = conversation.messages.all()
    
    # Safe diagnostic: check if key is present (returns True/False, never exposes value)
    import os
    api_key_configured = bool(os.environ.get('AI_PROVIDER_API_KEY'))
    
    return render(request, 'assistant/chat.html', {
        'conversation': conversation,
        'chat_messages': chat_messages,
        'api_key_configured': api_key_configured,
    })

@login_required
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not content or not conversation_id:
            return JsonResponse({'error': 'Missing content or conversation ID'}, status=400)
            
        conversation = get_object_or_404(Conversation, id=conversation_id, student=request.user)
        
        # Prepare history for AI
        history = list(conversation.messages.order_by('-created_at')[:10])
        history.reverse()
        
        ai_messages = []
        for msg in history:
            ai_messages.append({'role': msg.role, 'content': msg.content})
            
        # Append current user message
        ai_messages.append({'role': 'user', 'content': content})
            
        # Get AI response
        ai_service = AILearningAssistant()
        system_prompt = ai_service.construct_system_prompt(
            conversation.subject, 
            conversation.grade, 
            conversation.language
        )
        
        response_text = ai_service.generate_response(system_prompt, ai_messages)
        
        # Save user message now that response succeeded
        Message.objects.create(
            conversation=conversation,
            role='user',
            content=content
        )
        
        # Save assistant message
        assistant_msg = Message.objects.create(
            conversation=conversation,
            role='assistant',
            content=response_text
        )
        
        conversation.updated_at = __import__('django').utils.timezone.now()
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'role': assistant_msg.role,
                'content': assistant_msg.content,
                'created_at': assistant_msg.created_at.isoformat()
            }
        })
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=503)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': 'An unexpected error occurred while processing your request. Please try again later.'}, status=500)

@login_required
def explain_mistake(request):
    """Triggered from diagnostic report. Expects POST with question_id and student_answer"""
    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        student_answer = request.POST.get('student_answer')
        
        question = get_object_or_404(Question, question_id=question_id)
        
        conversation = Conversation.objects.filter(student=request.user).order_by('-updated_at').first()
        if not conversation:
            conversation = Conversation.objects.create(
                student=request.user,
                title="Learning Assistant",
                subject=question.subject
            )
            
        # Add system context message
        context = f"The student answered '{student_answer}' to the following question, but the correct answer is '{question.correct_answer}'. Explain the mistake gently and help them understand the concept.\n\nQuestion: {question.question_text}"
        
        user_content = f"Can you explain why my answer '{student_answer}' was wrong for the question: {question.question_text}?"
        
        ai_service = AILearningAssistant()
        sys_prompt = ai_service.construct_system_prompt(conversation.subject, conversation.grade, conversation.language, context=context)
        
        try:
            resp = ai_service.generate_response(sys_prompt, [{'role': 'user', 'content': f"Can you explain why my answer '{student_answer}' was wrong?"}])
            
            # Save messages only after success
            Message.objects.create(
                conversation=conversation,
                role='user',
                content=user_content
            )
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=resp
            )

        except ValueError as e:
            from django.contrib import messages
            messages.error(request, str(e))
        except Exception as e:
            from django.contrib import messages
            messages.error(request, "An error occurred while connecting to the AI provider.")
            
    return redirect('assistant:chat')

@login_required
def find_gap(request):
    """Triggered from dashboard to diagnose gaps via AI"""
    if request.method == 'POST':
        concept_id = request.POST.get('concept_id')
        subject = request.POST.get('subject', 'Mathematics')
        
        conversation = Conversation.objects.filter(student=request.user).order_by('-updated_at').first()
        if not conversation:
            conversation = Conversation.objects.create(
                student=request.user,
                title="Learning Assistant",
                subject=subject
            )
            
        from concepts.models import Concept, Prerequisite
        concept = get_object_or_404(Concept, concept_id=concept_id)
        
        # Find prerequisites
        prereqs = Prerequisite.objects.filter(concept=concept)
        prereq_names = [p.prerequisite_concept.name for p in prereqs]
        prereq_str = ", ".join(prereq_names) if prereq_names else "None listed"
        
        context = f"The student is struggling with '{concept.name}'. The prerequisite concepts are: {prereq_str}. Ask them a simple question about one of the prerequisites to find their root gap."
        
        user_content = f"I'm struggling with {concept.name}. Can you help me find where my gap is?"
        
        ai_service = AILearningAssistant()
        sys_prompt = ai_service.construct_system_prompt(conversation.subject, conversation.grade, conversation.language, context=context)
        
        try:
            resp = ai_service.generate_response(sys_prompt, [{'role': 'user', 'content': f"Help me find my gap for {concept.name}"}])
            
            Message.objects.create(
                conversation=conversation,
                role='user',
                content=user_content
            )
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=resp
            )
        except ValueError as e:
            from django.contrib import messages
            messages.error(request, str(e))
        except Exception as e:
            from django.contrib import messages
            messages.error(request, "An error occurred while connecting to the AI provider.")
            
    return redirect('assistant:chat')

@login_required
def practice_mode(request):
    """Start an interactive practice session"""
    if request.method == 'POST':
        concept_id = request.POST.get('concept_id')
        
        from concepts.models import Concept
        concept = get_object_or_404(Concept, concept_id=concept_id)
        
        conversation = Conversation.objects.filter(student=request.user).order_by('-updated_at').first()
        if not conversation:
            conversation = Conversation.objects.create(
                student=request.user,
                title="Learning Assistant",
                subject=concept.subject
            )
            
        context = f"You are in 'Practice With Me' mode for {concept.name}. Ask the student ONE question at a time. Do not give the answer yet. Wait for their response."
        
        user_content = f"Let's practice {concept.name} together. Ask me a question."
        
        ai_service = AILearningAssistant()
        sys_prompt = ai_service.construct_system_prompt(conversation.subject, conversation.grade, conversation.language, context=context)
        
        try:
            resp = ai_service.generate_response(sys_prompt, [{'role': 'user', 'content': f"Ask me a question to practice {concept.name}"}])
            
            Message.objects.create(
                conversation=conversation,
                role='user',
                content=user_content
            )
            Message.objects.create(
                conversation=conversation,
                role='assistant',
                content=resp
            )
        except ValueError as e:
            from django.contrib import messages
            messages.error(request, str(e))
        except Exception as e:
            from django.contrib import messages
            messages.error(request, "An error occurred while connecting to the AI provider.")
            
    return redirect('assistant:chat')
