import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from concepts.models import Concept, Prerequisite
from quizzes.models import Question

class Command(BaseCommand):
    help = 'Import the synthetic dataset into the database.'

    def handle(self, *args, **options):
        dataset_dir = os.path.join(settings.BASE_DIR, 'Datasets')

        # 1. Import Concepts
        concepts_file = os.path.join(dataset_dir, 'concepts.csv')
        self.stdout.write(f"Importing concepts from {concepts_file}...")
        try:
            df_concepts = pd.read_csv(concepts_file)
            
            # First pass: Create concepts
            for _, row in df_concepts.iterrows():
                Concept.objects.get_or_create(
                    concept_id=row['concept_id'],
                    defaults={
                        'name': row['concept_name'],
                        'subject': row['subject'],
                        'grade_band': row['grade_band']
                    }
                )
            
            # Second pass: Create prerequisite relationships
            for _, row in df_concepts.iterrows():
                if pd.notna(row['prerequisite_concept_id']):
                    concept = Concept.objects.get(concept_id=row['concept_id'])
                    try:
                        prereq = Concept.objects.get(concept_id=row['prerequisite_concept_id'])
                        Prerequisite.objects.get_or_create(concept=concept, prerequisite_concept=prereq)
                    except Concept.DoesNotExist:
                        self.stderr.write(f"Warning: Prerequisite {row['prerequisite_concept_id']} for {row['concept_id']} does not exist.")
            self.stdout.write(self.style.SUCCESS('Successfully imported concepts.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing concepts: {e}"))

        # 2. Import Questions
        questions_file = os.path.join(dataset_dir, 'questions.csv')
        self.stdout.write(f"Importing questions from {questions_file}...")
        try:
            df_questions = pd.read_csv(questions_file)
            for _, row in df_questions.iterrows():
                try:
                    concept = Concept.objects.get(concept_id=row['concept_id'])
                    Question.objects.get_or_create(
                        question_id=row['question_id'],
                        defaults={
                            'question_tag': row['question_tag'],
                            'concept': concept,
                            'question_text': row['question_text'],
                            'correct_answer': row['correct_answer'],
                            'common_distractor': row['common_distractor'] if pd.notna(row['common_distractor']) else '',
                            'difficulty': row['difficulty'],
                            'subject': row['subject'],
                            'grade_band': row['grade_band']
                        }
                    )
                except Concept.DoesNotExist:
                    self.stderr.write(f"Warning: Concept {row['concept_id']} for Question {row['question_id']} does not exist.")
            self.stdout.write(self.style.SUCCESS('Successfully imported questions.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing questions: {e}"))
