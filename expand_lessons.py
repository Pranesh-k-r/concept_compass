import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from concepts.models import Concept
from learning.models import Lesson

extended_data = {
    'C01': {
        'title': 'Division (Whole Numbers)',
        'difficulty': 'Beginner',
        'estimated_time': 15,
        'structured_content': {
            'explanation': 'Division is splitting into equal parts or groups. It is the result of "fair sharing".',
            'key_terms': [
                {'term': 'Dividend', 'definition': 'The amount that you want to divide up.'},
                {'term': 'Divisor', 'definition': 'The number you divide by.'},
                {'term': 'Quotient', 'definition': 'The answer after you divide one number by another.'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'Divide 12 by 3',
                    'steps': [
                        'Imagine 12 items.',
                        'Share them equally into 3 groups.',
                        'Each group gets 4 items, so 12 ÷ 3 = 4.'
                    ]
                }
            ],
            'visual_type': 'division_grouping',
            'visual_text': 'Here are 12 dots divided equally into 3 groups of 4:',
            'common_mistakes': [
                {
                    'mistake': 'Thinking division is commutative (e.g., 12 ÷ 3 is the same as 3 ÷ 12).',
                    'correction': 'Division order matters! 12 ÷ 3 = 4, but 3 ÷ 12 = 0.25.'
                }
            ],
            'knowledge_check': {
                'question': 'What is the quotient of 20 ÷ 5?',
                'options': ['4', '5', '15'],
                'answer': '4',
                'explanation': '20 shared into 5 equal groups gives 4 in each group.'
            }
        }
    },
    'C04': {
        'title': 'Understanding Ratios',
        'difficulty': 'Intermediate',
        'estimated_time': 15,
        'structured_content': {
            'explanation': 'A ratio says how much of one thing there is compared to another thing. Ratios can be written with a colon (3:5), as a fraction (3/5), or with words ("3 to 5").',
            'key_terms': [
                {'term': 'Ratio', 'definition': 'A comparison of two or more quantities.'},
                {'term': 'Equivalent Ratios', 'definition': 'Ratios that make the same comparison (e.g., 1:2 and 2:4).'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'If a recipe needs 3 cups of flour for every 2 cups of sugar, what is the ratio of flour to sugar?',
                    'steps': [
                        'Identify the first quantity (flour) = 3',
                        'Identify the second quantity (sugar) = 2',
                        'Write them separated by a colon: 3:2'
                    ]
                }
            ],
            'visual_type': 'ratio_bars',
            'visual_text': 'The ratio of cats to dogs is 3 to 5 (3:5).',
            'common_mistakes': [
                {
                    'mistake': 'Writing the ratio in the wrong order.',
                    'correction': 'If asked for the ratio of A to B, A must come first. "Boys to Girls" is not the same as "Girls to Boys".'
                }
            ],
            'knowledge_check': {
                'question': 'In a class of 10 boys and 15 girls, what is the ratio of boys to girls in simplest form?',
                'options': ['10:15', '2:3', '3:2'],
                'answer': '2:3',
                'explanation': 'The ratio is 10:15. Divide both numbers by their greatest common divisor (5) to get 2:3.'
            }
        }
    },
    'C05': {
        'title': 'Percentages',
        'difficulty': 'Intermediate',
        'estimated_time': 20,
        'structured_content': {
            'explanation': 'Percent means "per 100". A percentage is a number or ratio expressed as a fraction of 100.',
            'key_terms': [
                {'term': 'Percent', 'definition': 'Parts per one hundred, denoted by the % symbol.'}
            ],
            'formulas': [
                {'name': 'Finding the percentage of a number', 'latex': '\\text{Percentage} = \\frac{\\text{Percent}}{100} \\times \\text{Total}'}
            ],
            'examples': [
                {
                    'question': 'What is 45% of 200?',
                    'steps': [
                        'Convert 45% to a decimal: 0.45 (or \\(\\frac{45}{100}\\))',
                        'Multiply by the total: 0.45 × 200',
                        'The answer is 90.'
                    ]
                }
            ],
            'visual_type': 'percentage_grid',
            'visual_text': 'This grid has 100 cells. 45 are filled, representing 45%.',
            'common_mistakes': [
                {
                    'mistake': 'Forgetting to divide by 100 before multiplying.',
                    'correction': '45% of 200 is not 45 × 200 = 9000. It is \\(0.45 \\times 200 = 90\\).'
                }
            ],
            'knowledge_check': {
                'question': 'What is 20% of 50?',
                'options': ['10', '20', '100'],
                'answer': '10',
                'explanation': '20% is \\(0.20\\). \\(0.20 \\times 50 = 10\\).'
            }
        }
    },
    'C11': {
        'title': 'The Coordinate Plane',
        'difficulty': 'Intermediate',
        'estimated_time': 20,
        'structured_content': {
            'explanation': 'A coordinate plane is a 2D surface formed by two intersecting lines: a horizontal x-axis and a vertical y-axis. It allows us to plot points using (x, y) coordinates.',
            'key_terms': [
                {'term': 'x-axis', 'definition': 'The horizontal number line.'},
                {'term': 'y-axis', 'definition': 'The vertical number line.'},
                {'term': 'Origin', 'definition': 'The point (0, 0) where the axes intersect.'},
                {'term': 'Ordered Pair', 'definition': 'A pair of numbers (x, y) used to locate a point.'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'Plot the point (3, 2).',
                    'steps': [
                        'Start at the origin (0, 0).',
                        'Move 3 units to the right along the x-axis.',
                        'Move 2 units up parallel to the y-axis.',
                        'Mark the point.'
                    ]
                }
            ],
            'visual_type': 'coordinate_plane',
            'visual_text': 'Here is the point (3, 2) plotted on a coordinate plane:',
            'common_mistakes': [
                {
                    'mistake': 'Mixing up the x and y coordinates (plotting (y, x) instead of (x, y)).',
                    'correction': 'Remember: You have to run along the ground (x-axis) before you jump into the air (y-axis).'
                }
            ],
            'knowledge_check': {
                'question': 'Which axis is vertical?',
                'options': ['x-axis', 'y-axis', 'z-axis'],
                'answer': 'y-axis',
                'explanation': 'The y-axis goes up and down (vertical), while the x-axis goes left and right (horizontal).'
            }
        }
    },
    'C14': {
        'title': 'Area and Perimeter',
        'difficulty': 'Intermediate',
        'estimated_time': 25,
        'structured_content': {
            'explanation': 'Perimeter is the distance around the outside of a shape. Area is the amount of space inside the shape.',
            'key_terms': [
                {'term': 'Area', 'definition': 'The space inside a 2D shape, measured in square units.'},
                {'term': 'Perimeter', 'definition': 'The total length of the boundary of a closed figure.'}
            ],
            'formulas': [
                {'name': 'Area of a Rectangle', 'latex': 'A = \\text{length} \\times \\text{width}'},
                {'name': 'Perimeter of a Rectangle', 'latex': 'P = 2 \\times (\\text{length} + \\text{width})'}
            ],
            'examples': [
                {
                    'question': 'Find the area of a rectangle with length 12cm and width 5cm.',
                    'steps': [
                        'Identify the formula for Area: A = l × w',
                        'Substitute the values: A = 12 × 5',
                        'Calculate the result: A = 60 cm²'
                    ]
                }
            ],
            'visual_type': 'geometry_shape',
            'visual_text': 'A rectangle showing length, width, and total area.',
            'common_mistakes': [
                {
                    'mistake': 'Confusing the formulas for area and perimeter.',
                    'correction': 'Perimeter is adding the outside edges (think "fence"). Area is multiplying the dimensions (think "carpet").'
                }
            ],
            'knowledge_check': {
                'question': 'What is the perimeter of a 4m by 6m rectangle?',
                'options': ['24m', '20m', '10m'],
                'answer': '20m',
                'explanation': 'Perimeter = 2 × (4 + 6) = 2 × 10 = 20m.'
            }
        }
    },
    'C07': {
        'title': 'Order of Operations',
        'difficulty': 'Intermediate',
        'estimated_time': 20,
        'structured_content': {
            'explanation': 'The order of operations is a set of rules that tell you which part of a mathematical expression to calculate first.',
            'key_terms': [
                {'term': 'PEMDAS / BODMAS', 'definition': 'An acronym to remember the order: Parentheses, Exponents, Multiplication & Division, Addition & Subtraction.'}
            ],
            'formulas': [],
            'examples': [
                {
                    'question': 'Evaluate: \\(5 + 3 \\times 2\\)',
                    'steps': [
                        'According to PEMDAS, multiplication comes before addition.',
                        'First multiply: \\(3 \\times 2 = 6\\)',
                        'Then add: \\(5 + 6 = 11\\)'
                    ]
                }
            ],
            'visual_type': None,
            'visual_text': '',
            'common_mistakes': [
                {
                    'mistake': 'Always calculating left to right without looking at the operators.',
                    'correction': 'Addition and Subtraction are evaluated last. In \\(5 + 3 \\times 2\\), do NOT do \\(5 + 3 = 8\\) first.'
                }
            ],
            'knowledge_check': {
                'question': 'What is the value of \\(10 - 4 \\div 2\\)?',
                'options': ['3', '8', '12'],
                'answer': '8',
                'explanation': 'Division comes first: \\(4 \\div 2 = 2\\). Then subtraction: \\(10 - 2 = 8\\).'
            }
        }
    }
}

def seed():
    for cid, data in extended_data.items():
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
