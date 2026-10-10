class MisconceptionDetector:
    def __init__(self, min_evidence=2):
        self.min_evidence = min_evidence

    def analyze_responses(self, student):
        from quizzes.models import StudentResponse
        incorrect_responses = StudentResponse.objects.filter(session__student_id=student.username, is_correct=False)
        
        # Track potential misconceptions
        sign_errors = []
        fraction_inversions = []
        
        for r in incorrect_responses:
            ans = r.response_text.strip()
            corr = r.question.correct_answer.strip()
            
            # Detect Sign Error
            if (ans.startswith('-') and ans[1:] == corr) or (corr.startswith('-') and corr[1:] == ans):
                sign_errors.append(r)
                
            # Detect Fraction Inversion
            if '/' in ans and '/' in corr:
                try:
                    a_num, a_den = ans.split('/')
                    c_num, c_den = corr.split('/')
                    if a_num == c_den and a_den == c_num:
                        fraction_inversions.append(r)
                except:
                    pass

        detected = []
        
        if len(sign_errors) > 0:
            if len(sign_errors) >= self.min_evidence:
                detected.append({
                    'name': 'Sign Error with Negative Numbers',
                    'confidence': 'Confirmed',
                    'count': len(sign_errors),
                    'explanation': 'You are consistently confusing positive and negative signs.',
                    'example_r': sign_errors[0]
                })
            else:
                detected.append({
                    'name': 'Possible Sign Error',
                    'confidence': 'Not enough evidence yet',
                    'count': len(sign_errors),
                    'explanation': 'You made a sign error, but we need more evidence to confirm this is a persistent pattern.',
                    'example_r': sign_errors[0]
                })
                
        if len(fraction_inversions) > 0:
            if len(fraction_inversions) >= self.min_evidence:
                detected.append({
                    'name': 'Incorrect Fraction Operation (Inversion)',
                    'confidence': 'Confirmed',
                    'count': len(fraction_inversions),
                    'explanation': 'You are consistently flipping the numerator and denominator in fractions.',
                    'example_r': fraction_inversions[0]
                })
            else:
                detected.append({
                    'name': 'Possible Fraction Inversion',
                    'confidence': 'Not enough evidence yet',
                    'count': len(fraction_inversions),
                    'explanation': 'You flipped a fraction once, but we need more evidence to confirm the pattern.',
                    'example_r': fraction_inversions[0]
                })
                
        return detected
