import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from concepts.models import Concept
from learning.models import Lesson

lesson_data = {
    'C02': {
        'title': 'Understanding Fractions',
        'difficulty': 'Beginner',
        'estimated_time': 15,
        'structured_content': {
            'explanation': 'A fraction represents a part of a whole or, more generally, any number of equal parts. When spoken in everyday English, a fraction describes how many parts of a certain size there are, for example, one-half, eight-fifths, three-quarters.',
            'key_terms': [
                {'term': 'Numerator', 'definition': 'The top number in a fraction. It shows how many parts we have.'},
                {'term': 'Denominator', 'definition': 'The bottom number in a fraction. It shows how many equal parts the whole is divided into.'},
                {'term': 'Equivalent Fractions', 'definition': 'Fractions which have the same value, even though they may look different (e.g., 1/2 and 2/4).'}
            ],
            'formulas': [
                {'name': 'Adding fractions with the same denominator', 'latex': '\\frac{a}{c} + \\frac{b}{c} = \\frac{a + b}{c}'}
            ],
            'examples': [
                {
                    'question': 'If you eat 3 slices of a pizza that was cut into 8 equal slices, what fraction of the pizza did you eat?',
                    'steps': [
                        'Identify the whole: The pizza is cut into 8 slices, so the denominator is 8.',
                        'Identify the parts: You ate 3 slices, so the numerator is 3.',
                        'Write the fraction: \\(\\frac{3}{8}\\)'
                    ]
                },
                {
                    'question': 'Simplify the fraction \\(\\frac{4}{8}\\)',
                    'steps': [
                        'Find the greatest common divisor (GCD) of 4 and 8, which is 4.',
                        'Divide both the numerator and the denominator by 4.',
                        '\\(\\frac{4 \\div 4}{8 \\div 4} = \\frac{1}{2}\\)'
                    ]
                }
            ],
            'visual_type': 'fraction_bar',
            'common_mistakes': [
                {
                    'mistake': 'Adding both numerators and denominators when adding fractions.',
                    'correction': 'You only add the numerators. The denominator remains the same. Example: \\(\\frac{1}{4} + \\frac{2}{4} = \\frac{3}{4}\\), NOT \\(\\frac{3}{8}\\).'
                }
            ],
            'knowledge_check': {
                'question': 'What is \\(\\frac{2}{5} + \\frac{1}{5}\\)?',
                'options': ['\\(\\frac{3}{10}\\)', '\\(\\frac{3}{5}\\)', '\\(\\frac{2}{25}\\)'],
                'answer': '\\(\\frac{3}{5}\\)',
                'explanation': 'Because the denominators are the same (5), you just add the numerators: 2 + 1 = 3. The answer is \\(\\frac{3}{5}\\).'
            }
        }
    },
    'C03': {
        'title': 'Decimals and Place Value',
        'difficulty': 'Beginner',
        'estimated_time': 10,
        'structured_content': {
            'explanation': 'A decimal is a number that consists of a whole and a fractional part separated by a decimal point. The decimal point is used to separate the integer part from the fractional part.',
            'key_terms': [
                {'term': 'Decimal Point', 'definition': 'A dot separating the whole number part from the fractional part of a number.'},
                {'term': 'Tenths', 'definition': 'The first digit to the right of the decimal point.'},
                {'term': 'Hundredths', 'definition': 'The second digit to the right of the decimal point.'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'Write the fraction \\(\\frac{3}{10}\\) as a decimal.',
                    'steps': [
                        'The fraction \\(\\frac{3}{10}\\) means 3 divided by 10.',
                        'In decimal form, the tenths place is the first digit after the decimal point.',
                        'So, \\(\\frac{3}{10} = 0.3\\)'
                    ]
                }
            ],
            'visual_type': 'decimal_grid',
            'common_mistakes': [
                {
                    'mistake': 'Misaligning decimal points when adding or subtracting.',
                    'correction': 'Always line up the decimal points vertically before adding or subtracting.'
                }
            ],
            'knowledge_check': {
                'question': 'Which is larger: 0.5 or 0.05?',
                'options': ['0.5', '0.05', 'They are equal'],
                'answer': '0.5',
                'explanation': '0.5 represents 5 tenths (\\(\\frac{5}{10}\\)), while 0.05 represents 5 hundredths (\\(\\frac{5}{100}\\)). 0.5 is much larger.'
            }
        }
    },
    'C08': {
        'title': 'Introduction to Algebraic Expressions',
        'difficulty': 'Intermediate',
        'estimated_time': 20,
        'structured_content': {
            'explanation': 'An algebraic expression is a mathematical phrase that can contain ordinary numbers, variables (like x or y), and operators (like add, subtract, multiply, and divide). It does NOT contain an equals sign.',
            'key_terms': [
                {'term': 'Variable', 'definition': 'A letter or symbol used to represent an unknown value (e.g., x, y, a).'},
                {'term': 'Coefficient', 'definition': 'A number multiplied by a variable (e.g., in 3x, 3 is the coefficient).'},
                {'term': 'Constant', 'definition': 'A fixed value, a number on its own (e.g., in x + 5, 5 is the constant).'},
                {'term': 'Term', 'definition': 'Parts of an expression separated by + or - signs.'}
            ],
            'formulas': [
                {'name': 'Distributive Property', 'latex': 'a(b + c) = ab + ac'}
            ],
            'examples': [
                {
                    'question': 'Simplify the expression: \\(3x + 4 + 2x - 1\\)',
                    'steps': [
                        'Group the like terms (terms with the same variable, and constant terms).',
                        'Variable terms: \\(3x + 2x = 5x\\)',
                        'Constant terms: \\(4 - 1 = 3\\)',
                        'Combine them: \\(5x + 3\\)'
                    ]
                }
            ],
            'visual_type': 'algebra_balance',
            'common_mistakes': [
                {
                    'mistake': 'Adding unlike terms, e.g., thinking \\(2x + 3 = 5x\\).',
                    'correction': 'You can only add terms that have the exact same variables. Think of \\(x\\) as "apples". 2 apples + 3 (just a number) does not equal 5 apples.'
                }
            ],
            'knowledge_check': {
                'question': 'What is the coefficient in the expression \\(7y - 4\\)?',
                'options': ['7', '-4', 'y'],
                'answer': '7',
                'explanation': 'The coefficient is the number multiplying the variable. Here, 7 is multiplying y.'
            }
        }
    },
    'ENG01': {
        'title': 'Grammar Basics: Parts of Speech',
        'difficulty': 'Beginner',
        'estimated_time': 15,
        'structured_content': {
            'explanation': 'Parts of speech are the basic categories of words based on their function in a sentence. Understanding them is crucial for constructing clear and grammatically correct sentences.',
            'key_terms': [
                {'term': 'Noun', 'definition': 'A person, place, thing, or idea (e.g., dog, city, happiness).'},
                {'term': 'Verb', 'definition': 'An action or state of being (e.g., run, is, jump).'},
                {'term': 'Adjective', 'definition': 'A word that describes a noun (e.g., blue, quick, happy).'},
                {'term': 'Adverb', 'definition': 'A word that describes a verb, adjective, or another adverb (e.g., quickly, very).'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'Identify the noun, verb, and adjective in this sentence: "The quick brown fox jumps over the lazy dog."',
                    'steps': [
                        'Nouns: fox, dog',
                        'Verbs: jumps',
                        'Adjectives: quick, brown, lazy'
                    ]
                }
            ],
            'visual_type': None,
            'common_mistakes': [
                {
                    'mistake': 'Confusing adjectives and adverbs (e.g., "He runs good" instead of "He runs well").',
                    'correction': '"Good" is an adjective describing a noun. "Well" is an adverb describing the verb "runs".'
                }
            ],
            'knowledge_check': {
                'question': 'In the sentence "She sang beautifully", what part of speech is "beautifully"?',
                'options': ['Noun', 'Verb', 'Adverb', 'Adjective'],
                'answer': 'Adverb',
                'explanation': '"Beautifully" describes HOW she sang (a verb), so it is an adverb.'
            }
        }
    }
}

def seed():
    for cid, data in lesson_data.items():
        try:
            concept = Concept.objects.get(concept_id=cid)
            Lesson.objects.update_or_create(
                concept=concept,
                defaults={
                    'title': data['title'],
                    'difficulty': data['difficulty'],
                    'estimated_time': data['estimated_time'],
                    'structured_content': data['structured_content']
                }
            )
            print(f"Created/updated lesson for {cid}")
        except Concept.DoesNotExist:
            print(f"Concept {cid} not found.")

if __name__ == '__main__':
    seed()
