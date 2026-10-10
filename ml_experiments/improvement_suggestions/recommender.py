def get_recommendation(concept_id):
    """
    Maps a predicted concept gap to a relevant learning activity.
    In a real app, this would query a database.
    """
    mapping = {
        "C01": {"topic": "Whole Numbers", "activity": "Practice adding and subtracting whole numbers with flashcards."},
        "C02": {"topic": "Fractions", "activity": "Review fraction bars and practice finding common denominators."},
        "C03": {"topic": "Decimals", "activity": "Practice aligning decimal points during addition and subtraction."},
        "C04": {"topic": "Ratios", "activity": "Solve recipe-scaling problems to understand ratio proportions."},
        "C05": {"topic": "Percentages", "activity": "Calculate discounts on shopping items."},
        "C06": {"topic": "Integers", "activity": "Use a number line to visualize negative numbers."},
        "C07": {"topic": "Order of Operations", "activity": "Solve PEMDAS puzzles."},
        "C08": {"topic": "Variables", "activity": "Translate word problems into basic algebraic expressions."},
        "C09": {"topic": "Equations", "activity": "Practice solving one-step equations using the balance method."},
        "C10": {"topic": "Inequalities", "activity": "Graph inequalities on a number line."},
    }
    
    # Fallback for concepts C11-C20
    return mapping.get(concept_id, {
        "topic": f"Advanced Topic ({concept_id})",
        "activity": f"Review the primary lesson for {concept_id} and complete practice set A."
    })

def generate_improvement_report(predicted_gap, input_data, confidence_score=None):
    """
    Generates a readable improvement report.
    """
    # Find evidence (where student struggled the most)
    struggled_concepts = []
    for key, value in input_data.items():
        if key.endswith('_correct') and value != -1.0 and value < 0.5:
            cid = key.split('_')[0]
            struggled_concepts.append(cid)
            
    if not struggled_concepts:
        evidence = "No clear errors found in the recent session. The prediction is based on subtle timing and hint usage patterns."
    else:
        evidence = f"Struggled heavily on queries related to: {', '.join(struggled_concepts)}."

    recommendation = get_recommendation(predicted_gap)
    
    report = f"""
==================================================
      PERSONALIZED IMPROVEMENT SUGGESTION
==================================================

1. 🎯 PREDICTED CONCEPT GAP:
   -> {predicted_gap} - {recommendation['topic']}

2. 📊 EVIDENCE:
   -> {evidence}

3. 📚 RECOMMENDED REVISION TOPIC:
   -> {recommendation['topic']}

4. ✍️ SUGGESTED PRACTICE ACTIVITY:
   -> {recommendation['activity']}

5. ✅ FOLLOW-UP VERIFICATION:
   -> Take the {predicted_gap} mini-quiz to verify mastery after completing the activity.

==================================================
"""
    return report
