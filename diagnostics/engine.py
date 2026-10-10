from collections import defaultdict
from concepts.models import Concept, Prerequisite
from quizzes.models import StudentResponse

class DiagnosticResult:
    def __init__(self, candidate_concept=None, confidence="low", evidence=None, prerequisites=None, alternative_concepts=None, abstention_reason=None):
        self.candidate_concept = candidate_concept
        self.confidence = confidence # "low", "medium", "high"
        self.evidence = evidence or []
        self.prerequisites = prerequisites or []
        self.alternative_concepts = alternative_concepts or []
        self.abstention_reason = abstention_reason

    def to_dict(self):
        return {
            "candidate_concept_id": self.candidate_concept.concept_id if self.candidate_concept else None,
            "candidate_concept_name": self.candidate_concept.name if self.candidate_concept else None,
            "confidence": self.confidence,
            "evidence_count": len(self.evidence),
            "abstention_reason": self.abstention_reason,
        }

class DiagnosticEngine:
    """
    Deterministic diagnostic engine for identifying prerequisite concept gaps.
    """
    
    # Thresholds
    MIN_INCORRECT_FOR_DIAGNOSIS = 2
    
    def diagnose(self, session_or_responses):
        """
        Takes a QuizSession or a list of responses and returns a DiagnosticResult.
        """
        if hasattr(session_or_responses, 'responses'):
            responses = session_or_responses.responses.all()
        else:
            responses = session_or_responses
            
        if not responses:
            return DiagnosticResult(abstention_reason="No responses available in this session.")
        
        # 1. Summarize evidence
        concept_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0, "questions": []})
        
        for r in responses:
            concept = r.question.concept
            stats = concept_stats[concept.concept_id]
            stats["questions"].append(r)
            if r.is_correct:
                stats["correct"] += 1
            else:
                stats["incorrect"] += 1
                
        # 2. Identify candidate gaps based on recurring incorrect responses or chains
        struggling_concepts = []
        for cid, stats in concept_stats.items():
            if stats["incorrect"] >= self.MIN_INCORRECT_FOR_DIAGNOSIS:
                struggling_concepts.append(Concept.objects.get(concept_id=cid))
            elif stats["incorrect"] == 1:
                # If they only have 1 mistake here, check if they also have a mistake in its prerequisite
                # or if it's a prerequisite to something else they failed
                concept = Concept.objects.get(concept_id=cid)
                prereqs = Prerequisite.objects.filter(concept=concept)
                for p in prereqs:
                    p_id = p.prerequisite_concept.concept_id
                    if p_id in concept_stats and concept_stats[p_id]["incorrect"] >= 1:
                        # Found a chain of mistakes! (e.g., failed both A and its prereq B)
                        struggling_concepts.append(concept)
                        struggling_concepts.append(p.prerequisite_concept)
                        break
                        
        struggling_concepts = list(set(struggling_concepts)) # remove duplicates
                
        if not struggling_concepts:
            # Check if there is only 1 isolated mistake
            total_incorrect = sum(s["incorrect"] for s in concept_stats.values())
            if total_incorrect == 0:
                return DiagnosticResult(abstention_reason="No incorrect responses found. Student seems to have mastered the concepts.")
            else:
                return DiagnosticResult(abstention_reason="Insufficient evidence. Only isolated mistake(s) found without a clear prerequisite pattern. Avoiding premature diagnosis.")
            
        # 3. Consider prerequisite relationships
        # Score candidates
        candidate_scores = defaultdict(float)
        for concept in struggling_concepts:
            # Base score for struggling on this concept
            candidate_scores[concept] += concept_stats[concept.concept_id]["incorrect"]
            
            # Prerequisite logic: if they struggle on A, the gap might be its prereq.
            prereqs = Prerequisite.objects.filter(concept=concept)
            for p in prereqs:
                prereq_concept = p.prerequisite_concept
                # We give a high weight to the prerequisite as the candidate gap
                candidate_scores[prereq_concept] += concept_stats[concept.concept_id]["incorrect"] * 1.5

        if not candidate_scores:
            return DiagnosticResult(abstention_reason="Insufficient evidence to rank candidates.")

        # 4. Rank candidates
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        top_candidate, top_score = sorted_candidates[0]
        
        # 5. Handle ties
        alternative_concepts = []
        if len(sorted_candidates) > 1:
            if sorted_candidates[1][1] == top_score:
                # Tie found
                alternative_concepts = [c[0] for c in sorted_candidates[1:] if c[1] == top_score]
        
        # Determine confidence
        confidence = "low"
        if top_score >= self.MIN_INCORRECT_FOR_DIAGNOSIS * 1.5:
            confidence = "medium"
        if top_score >= self.MIN_INCORRECT_FOR_DIAGNOSIS * 2.5:
            confidence = "high"
            
        # Gather evidence to return
        evidence = []
        for cid, stats in concept_stats.items():
            if stats["incorrect"] > 0:
                evidence.append(f"{stats['incorrect']} incorrect response(s) on {Concept.objects.get(concept_id=cid).name}")
                
        prereq_links = []
        for p in Prerequisite.objects.filter(concept=top_candidate):
            prereq_links.append(p.prerequisite_concept.name)

        return DiagnosticResult(
            candidate_concept=top_candidate,
            confidence=confidence,
            evidence=evidence,
            prerequisites=prereq_links,
            alternative_concepts=alternative_concepts
        )

    def get_gap_detective_data(self, session_or_responses, student):
        """
        Builds a comprehensive prerequisite path for each weak topic in the session.
        """
        if hasattr(session_or_responses, 'responses'):
            responses = session_or_responses.responses.all()
        else:
            responses = session_or_responses
            
        if not responses:
            return []
            
        # Identify weak topics from current session
        concept_stats = defaultdict(lambda: {"correct": 0, "incorrect": 0})
        for r in responses:
            concept_stats[r.question.concept]["attempted"] = concept_stats[r.question.concept].get("attempted", 0) + 1
            if r.is_correct:
                concept_stats[r.question.concept]["correct"] += 1
            else:
                concept_stats[r.question.concept]["incorrect"] += 1
                
        weak_topics = []
        for concept, stats in concept_stats.items():
            acc = (stats["correct"] / stats["attempted"]) * 100
            if acc < 70 or stats["incorrect"] >= self.MIN_INCORRECT_FOR_DIAGNOSIS:
                weak_topics.append({'concept': concept, 'stats': stats, 'acc': acc})
                
        # Build path for each weak topic
        gap_reports = []
        from quizzes.models import StudentResponse
        
        for wt in weak_topics:
            target = wt['concept']
            
            # Find immediate prerequisite
            prereq = Prerequisite.objects.filter(concept=target).first()
            if not prereq:
                continue
                
            p_concept = prereq.prerequisite_concept
            
            # Find grand-prerequisite to build a path A -> B -> Target
            grand_prereq = Prerequisite.objects.filter(concept=p_concept).first()
            
            path = []
            if grand_prereq:
                gp_concept = grand_prereq.prerequisite_concept
                path.append(self._evaluate_concept_for_path(gp_concept, student))
                
            path.append(self._evaluate_concept_for_path(p_concept, student))
            
            # Add target
            path.append({
                'concept': target,
                'status': 'weak',
                'label': 'Target'
            })
            
            # Find earliest weak/unassessed node in path
            earliest_gap = None
            for node in path[:-1]:
                if node['status'] in ['weak', 'unassessed']:
                    earliest_gap = node
                    break
                    
            gap_reports.append({
                'target': target,
                'target_stats': wt['stats'],
                'path': path,
                'earliest_gap': earliest_gap
            })
            
        return gap_reports

    def _evaluate_concept_for_path(self, concept, student):
        from quizzes.models import StudentResponse
        hist = StudentResponse.objects.filter(session__student_id=student.username, question__concept=concept)
        if not hist.exists():
            return {'concept': concept, 'status': 'unassessed', 'label': 'Not assessed yet'}
            
        corr = hist.filter(is_correct=True).count()
        total = hist.count()
        acc = (corr / total) * 100
        
        if acc >= 75:
            status = 'mastered'
            label = 'Demonstrated understanding'
        elif acc >= 50:
            status = 'developing'
            label = 'Developing'
        else:
            status = 'weak'
            label = 'Possible gap (repeated errors)'
            
        return {'concept': concept, 'status': status, 'label': label, 'acc': round(acc)}
