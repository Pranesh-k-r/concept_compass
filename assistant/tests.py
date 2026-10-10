from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from assistant.models import Conversation, Message
from concepts.models import Concept
from quizzes.models import Question

User = get_user_model()

class AILearningAssistantTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='password123')
        self.client = Client()
        self.client.login(username='student1', password='password123')
        
        self.concept = Concept.objects.create(
            concept_id="fractions_add",
            name="Adding Fractions",
            subject="Mathematics",
            grade_band="7-8"
        )
        self.question = Question.objects.create(
            question_id="q1",
            concept=self.concept,
            question_text="What is 1/2 + 1/4?",
            correct_answer="3/4"
        )

    @patch('assistant.views.AILearningAssistant')
    def test_send_message_success(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.return_value = "This is a dynamic mock response."
        
        conversation = Conversation.objects.create(student=self.user)
        
        response = self.client.post(
            reverse('assistant:send_message'),
            data={'content': 'Hello AI', 'conversation_id': conversation.id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['message']['content'], "This is a dynamic mock response.")
        
        # Verify it was saved to the DB
        self.assertEqual(Message.objects.filter(role='user', content='Hello AI').count(), 1)
        self.assertEqual(Message.objects.filter(role='assistant', content='This is a dynamic mock response.').count(), 1)

    @patch('assistant.views.AILearningAssistant')
    def test_send_message_missing_api_key(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.side_effect = ValueError("AI_PROVIDER_API_KEY environment variable is not configured on the server.")
        
        conversation = Conversation.objects.create(student=self.user)
        
        response = self.client.post(
            reverse('assistant:send_message'),
            data={'content': 'Hello AI', 'conversation_id': conversation.id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 503)
        data = response.json()
        self.assertIn("AI_PROVIDER_API_KEY", data['error'])
        
        # Neither user nor assistant message is saved on failure
        self.assertEqual(Message.objects.filter(role='user').count(), 0)
        self.assertEqual(Message.objects.filter(role='assistant').count(), 0)

    @patch('assistant.views.AILearningAssistant')
    def test_send_message_network_failure(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.side_effect = Exception("Network timeout")
        
        conversation = Conversation.objects.create(student=self.user)
        
        response = self.client.post(
            reverse('assistant:send_message'),
            data={'content': 'Hello AI', 'conversation_id': conversation.id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 500)
        data = response.json()
        self.assertIn("unexpected error occurred", data['error'])
        
        # Neither user nor assistant message is saved on failure
        self.assertEqual(Message.objects.filter(role='user').count(), 0)
        self.assertEqual(Message.objects.filter(role='assistant').count(), 0)

    @patch('assistant.views.AILearningAssistant')
    def test_explain_mistake_action(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.return_value = "You added the denominators, which is a common mistake."
        
        response = self.client.post(reverse('assistant:explain_mistake'), {
            'question_id': self.question.question_id,
            'student_answer': '2/6'
        })
        
        self.assertRedirects(response, reverse('assistant:chat'))
        self.assertEqual(Message.objects.filter(role='assistant').count(), 1)
        self.assertIn("You added the denominators", Message.objects.filter(role='assistant').first().content)

    @patch('assistant.views.AILearningAssistant')
    def test_explain_mistake_missing_api_key(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.side_effect = ValueError("API Key missing")
        
        response = self.client.post(reverse('assistant:explain_mistake'), {
            'question_id': self.question.question_id,
            'student_answer': '2/6'
        })
        
        self.assertRedirects(response, reverse('assistant:chat'))
        
        # User message is NOT saved because the API call failed
        self.assertEqual(Message.objects.filter(role='user').count(), 0)
        self.assertEqual(Message.objects.filter(role='assistant').count(), 0)

    @patch('assistant.views.AILearningAssistant')
    def test_find_gap_action(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.return_value = "Let's check your prerequisites."
        
        response = self.client.post(reverse('assistant:find_gap'), {
            'concept_id': self.concept.concept_id,
            'subject': 'Mathematics'
        })
        
        self.assertRedirects(response, reverse('assistant:chat'))
        self.assertEqual(Message.objects.filter(role='assistant').count(), 1)

    @patch('assistant.views.AILearningAssistant')
    def test_practice_mode_action(self, MockAssistant):
        mock_instance = MockAssistant.return_value
        mock_instance.construct_system_prompt.return_value = "System Prompt"
        mock_instance.generate_response.return_value = "Here is a practice question."
        
        response = self.client.post(reverse('assistant:practice_mode'), {
            'concept_id': self.concept.concept_id
        })
        
        self.assertRedirects(response, reverse('assistant:chat'))
        self.assertEqual(Message.objects.filter(role='assistant').count(), 1)

    def test_chat_interface_updates_settings(self):
        Conversation.objects.create(student=self.user, subject="English")
        response = self.client.post(reverse('assistant:chat'), {
            'subject': 'Mathematics',
            'grade': '8',
            'language': 'Kannada'
        })
        self.assertRedirects(response, reverse('assistant:chat'))
        
        conv = Conversation.objects.get(student=self.user)
        self.assertEqual(conv.subject, 'Mathematics')
        self.assertEqual(conv.grade, '8')
        self.assertEqual(conv.language, 'Kannada')

from assistant.local_bot import LocalBotEngine

class LocalBotTests(TestCase):
    def setUp(self):
        self.bot = LocalBotEngine()

    def test_greetings(self):
        resp = self.bot.get_response('hello')
        self.assertIn('Concept Compass Learning Assistant', resp)

    def test_fractions(self):
        resp = self.bot.get_response('tell me about fractions')
        self.assertIn('Fractions', resp)
        self.assertIn('numerator', resp)

    def test_division(self):
        resp = self.bot.get_response('how to divide')
        self.assertIn('Division', resp)
        self.assertIn('groups', resp)

    def test_english_grammar(self):
        resp = self.bot.get_response('what is a noun', subject='English')
        self.assertIn('Nouns', resp)
        self.assertIn('person, place', resp)

    def test_practice_answers(self):
        # Trigger practice
        practice_q = self.bot.get_response('practice fractions')
        self.assertIn('practice question', practice_q.lower())
        
        # Test correct answer
        resp_correct = self.bot.get_response('b')
        self.assertIn('Correct!', resp_correct)
        
        # Test incorrect answer
        resp_incorrect = self.bot.get_response('a')
        self.assertIn('Not quite.', resp_incorrect)

    def test_unknown_questions(self):
        resp = self.bot.get_response('what is the meaning of life?')
        self.assertIn('I can help with fractions, division, percentages', resp)

    def test_repeated_submissions(self):
        resp1 = self.bot.get_response('what is a noun', subject='English')
        resp2 = self.bot.get_response('what is a noun', subject='English')
        self.assertEqual(resp1, resp2)
        
    def test_kannada_translation(self):
        resp = self.bot.get_response('hello', language='Kannada')
        self.assertIn('ನಮಸ್ಕಾರ!', resp)
