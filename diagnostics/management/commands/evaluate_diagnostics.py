import os
import pandas as pd
from django.core.management.base import BaseCommand
from django.conf import settings
from concepts.models import Concept
from diagnostics.engine import DiagnosticEngine

class MockQuestion:
    def __init__(self, concept):
        self.concept = concept

class MockResponse:
    def __init__(self, is_correct, concept):
        self.is_correct = is_correct
        self.question = MockQuestion(concept)

class Command(BaseCommand):
    help = 'Evaluate the deterministic diagnostic engine on the synthetic dataset.'

    def handle(self, *args, **options):
        dataset_dir = os.path.join(settings.BASE_DIR, 'Datasets')
        profiles_file = os.path.join(dataset_dir, 'annotated_profiles.csv')
        responses_file = os.path.join(dataset_dir, 'student_responses.csv')

        self.stdout.write("Loading evaluation data (this might take a moment)...")
        df_profiles = pd.read_csv(profiles_file)
        df_responses = pd.read_csv(responses_file)

        engine = DiagnosticEngine()
        
        # Load all concepts into memory for quick lookup
        concept_map = {c.concept_id: c for c in Concept.objects.all()}

        total_evaluated = 0
        correct_predictions = 0
        abstentions = 0
        
        self.stdout.write("Evaluating profiles...")
        
        # To avoid memory and time explosion, evaluate on a sample (e.g., first 500 profiles)
        sample_profiles = df_profiles.head(500)
        
        for _, profile in sample_profiles.iterrows():
            profile_id = profile['profile_id']
            true_label = profile['annotated_root_gap_concept_id']
            
            # Get responses for this profile
            profile_responses = df_responses[df_responses['profile_id'] == profile_id]
            
            mock_responses = []
            for _, row in profile_responses.iterrows():
                cid = row['concept_id']
                if cid in concept_map:
                    mock_responses.append(
                        MockResponse(is_correct=bool(row['is_correct']), concept=concept_map[cid])
                    )
            
            if not mock_responses:
                continue
                
            total_evaluated += 1
            result = engine.diagnose(mock_responses)
            
            if result.abstention_reason:
                abstentions += 1
            elif result.candidate_concept and result.candidate_concept.concept_id == true_label:
                correct_predictions += 1
                
        coverage = total_evaluated - abstentions
        accuracy = (correct_predictions / coverage) * 100 if coverage > 0 else 0
        abstention_rate = (abstentions / total_evaluated) * 100 if total_evaluated > 0 else 0
        
        self.stdout.write(self.style.SUCCESS("--- Offline Evaluation Results ---"))
        self.stdout.write(f"Evaluated Profiles (Sample): {total_evaluated}")
        self.stdout.write(f"Coverage (Made a prediction): {coverage} ({100 - abstention_rate:.1f}%)")
        self.stdout.write(f"Abstentions (Insufficient evidence): {abstentions} ({abstention_rate:.1f}%)")
        self.stdout.write(f"Exact Match Accuracy (on covered): {accuracy:.1f}%")
        self.stdout.write("Note: This is evaluated on synthetic latent mastery labels. Results reflect rule alignment, not real-world validity.")
