from concepts.models import Concept
from quizzes.models import StudentResponse

class LearningPriorityEngine:
    def __init__(self, min_evidence=2):
        self.min_evidence = min_evidence

    def rank_priorities(self, student, subject='Mathematics'):
        """
        Analyzes all responses for a student and ranks topics into:
        - 'Focus First'
        - 'Study Next' 
        - 'Review'
        - 'More Evidence Needed'
        """
        # Note: 'student' is a Django User object
        responses = StudentResponse.objects.filter(session__student_id=student.username, session__subject=subject)
        
        # Aggregate stats by concept
        stats = {}
        for r in responses:
            if not r.question.concept: continue
            cid = r.question.concept.concept_id
            if cid not in stats:
                stats[cid] = {'concept': r.question.concept, 'attempted': 0, 'correct': 0, 'incorrect': 0}
            
            stats[cid]['attempted'] += 1
            if r.is_correct:
                stats[cid]['correct'] += 1
            else:
                stats[cid]['incorrect'] += 1
                
        # Calculate scores
        results = []
        for cid, data in stats.items():
            attempted = data['attempted']
            correct = data['correct']
            accuracy = (correct / attempted) * 100
            
            # Determine priority category
            if attempted < self.min_evidence:
                category = 'Take a Few More Questions'
                rank = 3
            elif accuracy < 50:
                category = 'Study First'
                rank = 0
            elif accuracy < 80:
                category = 'Study Next'
                rank = 1
            else:
                category = 'Review and Maintain'
                rank = 2
                
            results.append({
                'concept': data['concept'],
                'attempted': attempted,
                'accuracy': round(accuracy),
                'category': category,
                'rank': rank,
                'reason': f"Accuracy is {round(accuracy)}% across {attempted} questions."
            })
            
        # Sort by rank (0 is highest priority), then accuracy ascending, then attempted descending
        results.sort(key=lambda x: (x['rank'], x['accuracy'], -x['attempted']))
        return results
