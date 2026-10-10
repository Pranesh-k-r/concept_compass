import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from concepts.models import Concept, Prerequisite
from quizzes.models import Question

print(f"English Concepts: {Concept.objects.filter(subject='English').count()}")
print(f"English Questions: {Question.objects.filter(subject='English').count()}")

# Create English Concepts
c1, _ = Concept.objects.get_or_create(concept_id='ENG01', defaults={'name': 'Grammar Basics', 'subject': 'English', 'grade_band': '7-8'})
c2, _ = Concept.objects.get_or_create(concept_id='ENG02', defaults={'name': 'Sentence Formation', 'subject': 'English', 'grade_band': '7-8'})
c3, _ = Concept.objects.get_or_create(concept_id='ENG03', defaults={'name': 'Vocabulary in Context', 'subject': 'English', 'grade_band': '7-8'})
c4, _ = Concept.objects.get_or_create(concept_id='ENG04', defaults={'name': 'Reading Comprehension', 'subject': 'English', 'grade_band': '7-8'})

# Create Prerequisite links for English (Grammar -> Sentence Formation)
Prerequisite.objects.get_or_create(concept=c2, prerequisite_concept=c1)

# Create English Questions
Question.objects.get_or_create(
    question_id='EQ001',
    defaults={
        'question_tag': 'Grammar: Tenses',
        'concept': c1,
        'question_text': 'Choose the correct form of the verb: She (go) to the market yesterday.',
        'correct_answer': 'went',
        'common_distractor': 'goes',
        'difficulty': 'easy',
        'subject': 'English',
        'grade_band': '7-8'
    }
)

Question.objects.get_or_create(
    question_id='EQ002',
    defaults={
        'question_tag': 'Sentence Formation',
        'concept': c2,
        'question_text': 'Rearrange the words: blue / is / sky / the',
        'correct_answer': 'the sky is blue',
        'common_distractor': 'sky the is blue',
        'difficulty': 'medium',
        'subject': 'English',
        'grade_band': '7-8'
    }
)

Question.objects.get_or_create(
    question_id='EQ003',
    defaults={
        'question_tag': 'Vocabulary: Synonyms',
        'concept': c3,
        'question_text': 'What is a synonym for happy?',
        'correct_answer': 'joyful',
        'common_distractor': 'sad',
        'difficulty': 'easy',
        'subject': 'English',
        'grade_band': '7-8'
    }
)

Question.objects.get_or_create(
    question_id='EQ004',
    defaults={
        'question_tag': 'Reading Comprehension',
        'concept': c4,
        'question_text': 'Read this sentence: "The quick brown fox jumps over the lazy dog." What animal jumps?',
        'correct_answer': 'fox',
        'common_distractor': 'dog',
        'difficulty': 'medium',
        'subject': 'English',
        'grade_band': '7-8'
    }
)
Question.objects.get_or_create(
    question_id='EQ005',
    defaults={
        'question_tag': 'Grammar: Prepositions',
        'concept': c1,
        'question_text': 'The book is ___ the table.',
        'correct_answer': 'on',
        'common_distractor': 'in',
        'difficulty': 'easy',
        'subject': 'English',
        'grade_band': '7-8'
    }
)

print("Added English concepts and questions.")
