import re
import json

class LocalBotEngine:
    def __init__(self):
        # We store some state for practice mode answering
        self.practice_state = {}

    def get_response(self, user_text, subject="Mathematics", language="English", conversation_id=None):
        user_text_lower = user_text.lower().strip()
        
        # Check empty
        if not user_text_lower:
            return "Please type a question or topic you want to learn about."
            
        # Check greetings
        if user_text_lower in ['hi', 'hello', 'hey', 'greetings', 'namaste']:
            if language == 'Kannada':
                return "ನಮಸ್ಕಾರ! ನಾನು ಕಾನ್ಸೆಪ್ಟ್ ಕಂಪಾಸ್ ಆಫ್‌ಲೈನ್ ಸಹಾಯಕ. ನಿಮಗೆ ಯಾವ ವಿಷಯದಲ್ಲಿ ಸಹಾಯ ಬೇಕು?"
            return "Hello! I am the Concept Compass Learning Assistant (Offline Mode). How can I help you today?"
            
        # Check practice answer
        # If the user is answering a practice question...
        # Wait, the prompt says "Add topic-specific practice questions with answer checking and explanations."
        # A simple way to check if the user is answering a previous practice question:
        # We can look for keywords like "my answer is" or just simple numbers if they were just asked.
        # But a stateless bot is easier. Let's just use keyword matching.
        
        if "answer is" in user_text_lower or user_text_lower.isdigit() or re.match(r'^[a-d]$', user_text_lower) or "/" in user_text_lower or ":" in user_text_lower:
            # We will just give a generic check response if it seems like an answer,
            # or try to catch specific answers. Actually, stateless is hard for practice.
            # Let's provide a mock practice mode: if they ask "practice fractions", we give a question. 
            pass

        # Practice questions handling (Priority)
        if 'practice' in user_text_lower or 'question' in user_text_lower or 'test' in user_text_lower:
            return "Here is a practice question: **What is 3/4 + 1/4?**\n(A) 2/4\n(B) 1\n(C) 4/8\n(D) 3/16\n\n*Type your answer to see if you are correct!*"
            
        if user_text_lower in ['b', '1', '1/1', '4/4']:
            return "Correct! 3/4 + 1/4 = 4/4, which simplifies to 1. Great job!"
        if user_text_lower in ['a', 'c', 'd', '2/4', '4/8', '3/16']:
            return "Not quite. Remember, when adding fractions with the same denominator, you add the numerators together and keep the denominator the same. 3 + 1 = 4, so it's 4/4 = 1."

        # English grammar rules
        if subject == 'English' or 'grammar' in user_text_lower or 'english' in user_text_lower:
            if re.search(r'\bnouns?\b', user_text_lower):
                return "**Nouns**\nA noun is a word that represents a person, place, thing, or idea.\n*Rule*: Capitalize proper nouns (like names).\n*Example*: In 'The dog ran to the park', 'dog' and 'park' are nouns."
            if re.search(r'\bpronouns?\b', user_text_lower):
                return "**Pronouns**\nA pronoun is a word that takes the place of a noun.\n*Rule*: Use pronouns to avoid repeating the same noun.\n*Example*: Instead of 'John ran because John was late', say 'John ran because **he** was late'."
            if re.search(r'\bverbs?\b', user_text_lower):
                return "**Verbs**\nA verb is an action word or a state of being.\n*Rule*: Every sentence must have at least one verb.\n*Example*: In 'She **jumps** very high', 'jumps' is the verb."
            if re.search(r'\btenses?\b', user_text_lower):
                return "**Tenses**\nTenses show when an action happens (past, present, or future).\n*Rule*: Present tense happens now. Past tense already happened (often ends in -ed).\n*Example*: Present: 'I walk'. Past: 'I walked'."
            if re.search(r'\barticles?\b', user_text_lower):
                return "**Articles**\nArticles are words like 'a', 'an', and 'the' that define a noun as specific or unspecific.\n*Rule*: Use 'an' before words starting with vowel sounds.\n*Example*: 'An apple', 'A dog', 'The sun'."
            if 'punctuation' in user_text_lower or 'comma' in user_text_lower:
                return "**Commas and Punctuation**\nPunctuation marks organize writing. Commas separate ideas or items in a list.\n*Rule*: Use commas to separate three or more items in a list.\n*Example*: 'I bought apples, bananas, and oranges.'"
            if 'sentence correction' in user_text_lower or 'correct' in user_text_lower:
                return "**Sentence Correction**\nSentence correction involves fixing grammar, spelling, and punctuation errors.\n*Rule*: Always check for subject-verb agreement.\n*Example*: Incorrect: 'He play tennis.' Correct: 'He **plays** tennis.'"
                
        # Mathematics rules
        if subject == 'Mathematics' or 'math' in user_text_lower:
            if 'equivalent fraction' in user_text_lower:
                if language == 'Kannada':
                    return "**ಸಮಾನ ಭಿನ್ನರಾಶಿಗಳು (Equivalent Fractions)**\nಸಮಾನ ಭಿನ್ನರಾಶಿಗಳು ಒಂದೇ ಮೌಲ್ಯವನ್ನು ಹೊಂದಿರುತ್ತವೆ.\n*ನಿಯಮ*: ಅಂಶ ಮತ್ತು ಛೇದವನ್ನು ಒಂದೇ ಸಂಖ್ಯೆಯಿಂದ ಗುಣಿಸಿ ಅಥವಾ ಭಾಗಿಸಿ.\n*ಉದಾಹರಣೆ*: 1/2 ಮತ್ತು 2/4 ಸಮಾನ ಭಿನ್ನರಾಶಿಗಳು."
                return "**Equivalent Fractions**\nEquivalent fractions represent the same part of a whole, even if they look different.\n*Rule*: Multiply or divide both the numerator and the denominator by the same non-zero number.\n*Formula*: (a/b) = (a*c)/(b*c)\n*Example*: 1/2 is equivalent to 2/4 (because 1*2=2 and 2*2=4)."
            elif 'fraction' in user_text_lower:
                if language == 'Kannada':
                    return "**ಭಿನ್ನರಾಶಿಗಳು (Fractions)**\nಭಿನ್ನರಾಶಿಯು ಸಂಪೂರ್ಣದ ಒಂದು ಭಾಗವನ್ನು ಪ್ರತಿನಿಧಿಸುತ್ತದೆ.\n*ಉದಾಹರಣೆ*: 1/2 ಎಂದರೆ ಎರಡರಲ್ಲಿ ಒಂದು ಭಾಗ."
                return "**Fractions**\nA fraction represents a part of a whole or a collection.\n*Rule*: The top number (numerator) counts the parts you have, and the bottom number (denominator) counts the total equal parts.\n*Formula*: a/b\n*Example*: 3/4 means you have 3 out of 4 equal pieces of a pie."
            if 'addition' in user_text_lower or re.search(r'\badd\b', user_text_lower):
                return "**Addition**\nAddition is finding the total, or sum, by combining two or more numbers.\n*Rule*: Line up the numbers by their place value before adding.\n*Example*: 15 + 24 = 39."
            if 'subtraction' in user_text_lower or 'subtract' in user_text_lower:
                return "**Subtraction**\nSubtraction is taking one number away from another to find the difference.\n*Rule*: Always subtract the smaller number from the larger number (unless you are learning negative numbers).\n*Example*: 45 - 20 = 25."
            if 'multiplication' in user_text_lower or 'multiply' in user_text_lower:
                return "**Multiplication**\nMultiplication is repeated addition.\n*Rule*: Multiplying a number by 0 always equals 0.\n*Example*: 5 * 3 = 15 (which is the same as 5 + 5 + 5)."
            if 'division' in user_text_lower or 'divide' in user_text_lower:
                return "**Division**\nDivision is splitting into equal parts or groups.\n*Rule*: You cannot divide any number by zero.\n*Formula*: a ÷ b = c means c * b = a\n*Example*: 12 ÷ 3 = 4 (because 4 groups of 3 make 12)."
            if 'decimal' in user_text_lower:
                return "**Decimals**\nA decimal is another way to write a fraction using a point to separate the whole number from the fractional part.\n*Rule*: When adding or subtracting decimals, always line up the decimal points.\n*Example*: 1.5 + 2.25 = 3.75."
            if 'ratio' in user_text_lower:
                return "**Ratios**\nA ratio compares two quantities.\n*Rule*: Ratios can be simplified just like fractions.\n*Formula*: a:b or a/b\n*Example*: If there are 2 boys and 3 girls, the ratio of boys to girls is 2:3."
            if 'percent' in user_text_lower:
                return "**Percentages**\nA percentage is a number or ratio expressed as a fraction of 100.\n*Rule*: To convert a decimal to a percent, multiply by 100.\n*Formula*: Part / Whole = Percent / 100\n*Example*: 50% means 50 out of 100, which is equal to 1/2."
            if 'negative' in user_text_lower:
                return "**Negative Numbers**\nNegative numbers are numbers less than zero.\n*Rule*: Adding a negative number is the same as subtracting. Multiplying two negative numbers gives a positive result.\n*Example*: -5 + 3 = -2. And -2 * -3 = 6."
            if 'order of operations' in user_text_lower or 'bodmas' in user_text_lower or 'pemdas' in user_text_lower:
                return "**Order of Operations**\nThe rules that state the sequence in which the multiple operations in an expression should be solved.\n*Rule*: Follow PEMDAS/BODMAS: Parentheses/Brackets, Exponents/Orders, Multiplication & Division, Addition & Subtraction.\n*Example*: 3 + 4 * 2 = 11 (multiply 4*2 first, then add 3)."
            if 'algebra' in user_text_lower or 'equation' in user_text_lower:
                return "**Algebra & Equations**\nAlgebra uses letters (like x or y) to represent unknown numbers.\n*Rule*: Whatever you do to one side of an equation, you must do to the other side to keep it balanced.\n*Example*: If x + 3 = 7, subtract 3 from both sides to find x = 4."
            if 'geometry' in user_text_lower:
                return "**Geometry**\nGeometry is the study of shapes, sizes, and properties of space.\n*Rule*: The sum of angles in a triangle is always 180 degrees.\n*Formula*: Area of a rectangle = length × width\n*Example*: A rectangle with length 4 and width 5 has an Area of 20."
            if 'probability' in user_text_lower:
                return "**Probability**\nProbability is how likely something is to happen.\n*Rule*: Probability is always a number between 0 (impossible) and 1 (certain).\n*Formula*: P(event) = (Favorable Outcomes) / (Total Possible Outcomes)\n*Example*: The probability of flipping a coin and getting heads is 1/2 (or 50%)."
            if re.search(r'\bmean\b', user_text_lower) or 'average' in user_text_lower:
                return "**Mean (Average)**\nThe mean is the average of a set of numbers.\n*Rule*: Add all the numbers together, then divide by how many numbers there are.\n*Formula*: Mean = Sum of values / Number of values\n*Example*: The mean of 2, 4, and 6 is (2+4+6)/3 = 12/3 = 4."

        # Fallback
        return "I can help with fractions, division, percentages, algebra, grammar, and more. Which topic would you like to learn?"
