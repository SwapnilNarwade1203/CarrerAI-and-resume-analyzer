import json
from django.core.management.base import BaseCommand, CommandError
from analyzer.models import Skill, SkillTestQuestion


class Command(BaseCommand):
    help = 'Import skill test questions from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='skill_questions_generated.json', help='Path to JSON file')
        parser.add_argument('--generate', action='store_true', help='Generate default questions for all skills')

    def handle(self, *args, **options):
        if options['generate']:
            self._generate_questions()
            return

        try:
            with open(options['file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"File not found: {options['file']}")

        created_count = 0
        for skill_name, questions in data.items():
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            for q in questions:
                _, created = SkillTestQuestion.objects.get_or_create(
                    skill=skill,
                    question=q['question'],
                    defaults={
                        'option_a': q.get('option_a', ''),
                        'option_b': q.get('option_b', ''),
                        'option_c': q.get('option_c', ''),
                        'option_d': q.get('option_d', ''),
                        'correct_option': q.get('correct_option', 'A'),
                        'explanation': q.get('explanation', ''),
                    }
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Imported {created_count} questions'))

    def _generate_questions(self):
        """Generate built-in questions for key skills."""
        BUILTIN_QUESTIONS = {
            'Python': [
                {'question': 'Which of the following is used to define a function in Python?', 'option_a': 'function', 'option_b': 'def', 'option_c': 'func', 'option_d': 'define', 'correct_option': 'B', 'explanation': 'The `def` keyword is used to define a function in Python.'},
                {'question': 'What does the `len()` function do?', 'option_a': 'Returns the length of an object', 'option_b': 'Deletes an object', 'option_c': 'Creates a list', 'option_d': 'Converts to integer', 'correct_option': 'A', 'explanation': '`len()` returns the number of items in an object.'},
                {'question': 'Which data type is immutable in Python?', 'option_a': 'List', 'option_b': 'Dictionary', 'option_c': 'Tuple', 'option_d': 'Set', 'correct_option': 'C', 'explanation': 'Tuples are immutable — once created, they cannot be changed.'},
                {'question': 'What is the output of `print(2 ** 3)`?', 'option_a': '6', 'option_b': '8', 'option_c': '9', 'option_d': '5', 'correct_option': 'B', 'explanation': '** is the exponentiation operator. 2**3 = 8.'},
                {'question': 'What does `range(5)` generate?', 'option_a': '1 to 5', 'option_b': '0 to 4', 'option_c': '0 to 5', 'option_d': '1 to 4', 'correct_option': 'B', 'explanation': '`range(5)` generates numbers from 0 to 4 (5 exclusive).'},
                {'question': 'Which module is used for regular expressions in Python?', 'option_a': 'regex', 'option_b': 'regexp', 'option_c': 're', 'option_d': 'rx', 'correct_option': 'C', 'explanation': 'The `re` module provides regular expression operations.'},
                {'question': 'What is a list comprehension?', 'option_a': 'A way to compress lists', 'option_b': 'A concise way to create lists', 'option_c': 'A list sorting method', 'option_d': 'A list deletion method', 'correct_option': 'B', 'explanation': 'List comprehensions offer a concise way to create lists: [x for x in iterable].'},
                {'question': 'What does `*args` do in a function definition?', 'option_a': 'Multiplication', 'option_b': 'Passes keyword arguments', 'option_c': 'Accepts variable number of positional arguments', 'option_d': 'Returns a tuple', 'correct_option': 'C', 'explanation': '*args allows a function to accept any number of positional arguments.'},
                {'question': 'Which statement is used to handle exceptions?', 'option_a': 'catch', 'option_b': 'try/except', 'option_c': 'error/handle', 'option_d': 'if/else', 'correct_option': 'B', 'explanation': 'Python uses try/except blocks for exception handling.'},
                {'question': 'What is a decorator in Python?', 'option_a': 'A function that decorates strings', 'option_b': 'A design pattern for UIs', 'option_c': 'A function that wraps another function', 'option_d': 'A class modifier', 'correct_option': 'C', 'explanation': 'Decorators are functions that modify the behavior of other functions.'},
            ],
            'Django': [
                {'question': 'What command is used to create a new Django project?', 'option_a': 'django create project', 'option_b': 'django-admin startproject', 'option_c': 'python new project', 'option_d': 'manage.py createproject', 'correct_option': 'B', 'explanation': '`django-admin startproject` creates a new Django project.'},
                {'question': 'What does ORM stand for in Django?', 'option_a': 'Object Relational Mapper', 'option_b': 'Object Record Manager', 'option_c': 'Online Resource Manager', 'option_d': 'Object Response Model', 'correct_option': 'A', 'explanation': 'ORM (Object Relational Mapper) maps database tables to Python objects.'},
                {'question': 'Which file defines URL patterns in Django?', 'option_a': 'settings.py', 'option_b': 'views.py', 'option_c': 'urls.py', 'option_d': 'models.py', 'correct_option': 'C', 'explanation': 'urls.py defines the URL routing patterns for a Django app.'},
                {'question': 'What does `{% csrf_token %}` do in a Django form?', 'option_a': 'Adds styling', 'option_b': 'Protects against Cross-Site Request Forgery attacks', 'option_c': 'Validates form inputs', 'option_d': 'Submits the form', 'correct_option': 'B', 'explanation': 'CSRF token prevents cross-site request forgery attacks.'},
                {'question': 'What is the purpose of Django migrations?', 'option_a': 'To move files between servers', 'option_b': 'To propagate model changes to the database', 'option_c': 'To transfer user data', 'option_d': 'To cache static files', 'correct_option': 'B', 'explanation': 'Migrations apply model changes to the database schema.'},
                {'question': 'Which decorator restricts a view to logged-in users?', 'option_a': '@staff_required', 'option_b': '@auth_required', 'option_c': '@login_required', 'option_d': '@user_required', 'correct_option': 'C', 'explanation': '`@login_required` redirects unauthenticated users to the login page.'},
                {'question': 'What is the Django template tag for loops?', 'option_a': '{% loop %}', 'option_b': '{% for %} {% endfor %}', 'option_c': '{# for #}', 'option_d': '{{ for }}', 'correct_option': 'B', 'explanation': 'Django uses {% for item in list %} {% endfor %} for loops in templates.'},
                {'question': 'How do you define a many-to-many relationship in Django?', 'option_a': 'ForeignKey', 'option_b': 'OneToOneField', 'option_c': 'ManyToManyField', 'option_d': 'MultipleField', 'correct_option': 'C', 'explanation': 'ManyToManyField creates a many-to-many relationship between models.'},
                {'question': 'What command runs the Django development server?', 'option_a': 'python manage.py serve', 'option_b': 'python manage.py start', 'option_c': 'python manage.py runserver', 'option_d': 'django start server', 'correct_option': 'C', 'explanation': '`python manage.py runserver` starts the development server on port 8000.'},
                {'question': 'What is Django\'s default database?', 'option_a': 'PostgreSQL', 'option_b': 'MySQL', 'option_c': 'MongoDB', 'option_d': 'SQLite', 'correct_option': 'D', 'explanation': 'Django uses SQLite by default for development.'},
            ],
            'JavaScript': [
                {'question': 'Which keyword declares a block-scoped variable in JavaScript?', 'option_a': 'var', 'option_b': 'let', 'option_c': 'const', 'option_d': 'int', 'correct_option': 'B', 'explanation': '`let` declares a block-scoped variable. `const` is also block-scoped but immutable.'},
                {'question': 'What does `===` mean in JavaScript?', 'option_a': 'Assignment', 'option_b': 'Loose equality', 'option_c': 'Strict equality', 'option_d': 'Greater than or equal', 'correct_option': 'C', 'explanation': '=== checks value AND type equality without type coercion.'},
                {'question': 'What is a Promise in JavaScript?', 'option_a': 'A data type', 'option_b': 'A synchronous function', 'option_c': 'An object representing eventual completion of async operation', 'option_d': 'A loop construct', 'correct_option': 'C', 'explanation': 'A Promise represents the eventual completion or failure of an asynchronous operation.'},
                {'question': 'What does `typeof null` return?', 'option_a': 'null', 'option_b': 'undefined', 'option_c': 'object', 'option_d': 'string', 'correct_option': 'C', 'explanation': 'typeof null returns "object" — a well-known JavaScript bug.'},
                {'question': 'Which method adds an element to the end of an array?', 'option_a': 'append()', 'option_b': 'push()', 'option_c': 'add()', 'option_d': 'insert()', 'correct_option': 'B', 'explanation': 'Array.push() adds one or more elements to the end of an array.'},
                {'question': 'What is event delegation?', 'option_a': 'Removing event listeners', 'option_b': 'Adding events to every child', 'option_c': 'Using a parent element to handle events from children', 'option_d': 'Pausing event propagation', 'correct_option': 'C', 'explanation': 'Event delegation attaches one listener to a parent to handle events for all children.'},
                {'question': 'What is closure in JavaScript?', 'option_a': 'A way to close a browser window', 'option_b': 'A function that retains access to its outer scope', 'option_c': 'Ending a loop', 'option_d': 'A CSS property', 'correct_option': 'B', 'explanation': 'A closure is a function that remembers the variables from its outer scope.'},
                {'question': 'What does `Array.map()` do?', 'option_a': 'Filters elements', 'option_b': 'Creates a new array with results of calling a function on each element', 'option_c': 'Reduces array to a single value', 'option_d': 'Sorts the array', 'correct_option': 'B', 'explanation': 'map() returns a new array where each element is transformed by a function.'},
                {'question': 'What is the purpose of `async/await`?', 'option_a': 'To speed up synchronous code', 'option_b': 'To write asynchronous code in a synchronous style', 'option_c': 'To create web workers', 'option_d': 'To handle CSS animations', 'correct_option': 'B', 'explanation': 'async/await is syntactic sugar over Promises for cleaner async code.'},
                {'question': 'What is `undefined` in JavaScript?', 'option_a': 'An error type', 'option_b': 'A declared variable with no value assigned', 'option_c': 'Null value', 'option_d': 'An empty string', 'correct_option': 'B', 'explanation': 'undefined means a variable is declared but has not been assigned a value.'},
            ],
            'SQL': [
                {'question': 'Which SQL clause is used to filter rows?', 'option_a': 'GROUP BY', 'option_b': 'ORDER BY', 'option_c': 'WHERE', 'option_d': 'HAVING', 'correct_option': 'C', 'explanation': 'WHERE filters rows before grouping; HAVING filters after grouping.'},
                {'question': 'What does SELECT DISTINCT do?', 'option_a': 'Orders results', 'option_b': 'Returns unique values only', 'option_c': 'Creates a new table', 'option_d': 'Sums values', 'correct_option': 'B', 'explanation': 'DISTINCT eliminates duplicate rows from the result set.'},
                {'question': 'Which JOIN returns all rows from the left table?', 'option_a': 'INNER JOIN', 'option_b': 'RIGHT JOIN', 'option_c': 'LEFT JOIN', 'option_d': 'CROSS JOIN', 'correct_option': 'C', 'explanation': 'LEFT JOIN returns all rows from the left table plus matching rows from the right.'},
                {'question': 'What is a primary key?', 'option_a': 'The first column', 'option_b': 'A unique identifier for each row', 'option_c': 'The most common value', 'option_d': 'An index on text columns', 'correct_option': 'B', 'explanation': 'A primary key uniquely identifies each record in a table.'},
                {'question': 'What does GROUP BY do?', 'option_a': 'Sorts results', 'option_b': 'Filters results', 'option_c': 'Groups rows sharing a value for aggregate functions', 'option_d': 'Creates sub-queries', 'correct_option': 'C', 'explanation': 'GROUP BY groups rows that have the same values in specified columns.'},
                {'question': 'Which aggregate function returns the total count?', 'option_a': 'SUM()', 'option_b': 'AVG()', 'option_c': 'COUNT()', 'option_d': 'MAX()', 'correct_option': 'C', 'explanation': 'COUNT() returns the number of rows matching the criteria.'},
                {'question': 'What is a foreign key?', 'option_a': 'A key from another database', 'option_b': 'A field that references the primary key of another table', 'option_c': 'A key for encryption', 'option_d': 'An alternative primary key', 'correct_option': 'B', 'explanation': 'Foreign key establishes a relationship between two tables.'},
                {'question': 'What does LIKE \'%python%\' do?', 'option_a': 'Exact match', 'option_b': 'Pattern match with wildcard', 'option_c': 'Case-sensitive search', 'option_d': 'Numeric comparison', 'correct_option': 'B', 'explanation': '% is a wildcard in SQL LIKE patterns matching any sequence of characters.'},
                {'question': 'What is the difference between DELETE and TRUNCATE?', 'option_a': 'No difference', 'option_b': 'DELETE removes specific rows; TRUNCATE removes all rows quickly', 'option_c': 'TRUNCATE can use WHERE', 'option_d': 'DELETE is faster', 'correct_option': 'B', 'explanation': 'DELETE can filter rows with WHERE; TRUNCATE removes all rows and resets auto-increment.'},
                {'question': 'What does a subquery do?', 'option_a': 'Creates a new table', 'option_b': 'A query nested inside another query', 'option_c': 'Optimizes indexes', 'option_d': 'Backs up the database', 'correct_option': 'B', 'explanation': 'A subquery (inner query) is nested inside another SQL query.'},
            ],
            'Machine Learning': [
                {'question': 'Which algorithm is used for classification?', 'option_a': 'Linear Regression', 'option_b': 'K-Means', 'option_c': 'Random Forest', 'option_d': 'PCA', 'correct_option': 'C', 'explanation': 'Random Forest is an ensemble method used for classification (and regression).'},
                {'question': 'What is the purpose of train-test split?', 'option_a': 'To clean data', 'option_b': 'To evaluate model performance on unseen data', 'option_c': 'To normalize features', 'option_d': 'To remove outliers', 'correct_option': 'B', 'explanation': 'Train-test split allows you to evaluate how well a model generalizes to new data.'},
                {'question': 'Which metric is best for imbalanced classification?', 'option_a': 'Accuracy', 'option_b': 'F1 Score', 'option_c': 'Mean Squared Error', 'option_d': 'R²', 'correct_option': 'B', 'explanation': 'F1 score balances precision and recall and is better for imbalanced datasets.'},
                {'question': 'What does PCA stand for?', 'option_a': 'Principal Component Analysis', 'option_b': 'Predictive Clustering Algorithm', 'option_c': 'Probabilistic Classifier Approach', 'option_d': 'Pattern Classification Algorithm', 'correct_option': 'A', 'explanation': 'PCA is a dimensionality reduction technique that finds principal components.'},
                {'question': 'What is gradient descent?', 'option_a': 'A descent in neural network layers', 'option_b': 'An optimization algorithm to minimize the loss function', 'option_c': 'A data preprocessing step', 'option_d': 'A feature selection method', 'correct_option': 'B', 'explanation': 'Gradient descent iteratively adjusts model parameters to minimize loss.'},
                {'question': 'Which of these is an unsupervised learning algorithm?', 'option_a': 'Linear Regression', 'option_b': 'SVM', 'option_c': 'K-Means Clustering', 'option_d': 'Logistic Regression', 'correct_option': 'C', 'explanation': 'K-Means is unsupervised — it finds patterns without labeled data.'},
                {'question': 'What is overfitting?', 'option_a': 'When the model performs well on all data', 'option_b': 'When model memorizes training data but fails on new data', 'option_c': 'When the model is too simple', 'option_d': 'When training takes too long', 'correct_option': 'B', 'explanation': 'Overfitting: high training accuracy but poor generalization to test data.'},
                {'question': 'What is a confusion matrix?', 'option_a': 'A matrix for confused predictions', 'option_b': 'A table showing TP, TN, FP, FN classification results', 'option_c': 'A feature correlation matrix', 'option_d': 'A type of RNN', 'correct_option': 'B', 'explanation': 'Confusion matrix shows model performance: True/False Positives and Negatives.'},
                {'question': 'What is the purpose of regularization?', 'option_a': 'To make training faster', 'option_b': 'To prevent overfitting by penalizing complexity', 'option_c': 'To normalize features', 'option_d': 'To handle missing values', 'correct_option': 'B', 'explanation': 'Regularization (L1/L2) adds a penalty to the loss to prevent overfitting.'},
                {'question': 'What is cross-validation?', 'option_a': 'Validating across multiple databases', 'option_b': 'Technique to evaluate model by splitting data into k folds', 'option_c': 'A type of neural network', 'option_d': 'Cross-checking feature importance', 'correct_option': 'B', 'explanation': 'K-fold cross-validation provides a more reliable model performance estimate.'},
            ],
            'React': [
                {'question': 'What is JSX?', 'option_a': 'A JavaScript extension for databases', 'option_b': 'JavaScript XML — syntax extension for writing HTML in JS', 'option_c': 'A React state manager', 'option_d': 'A testing framework', 'correct_option': 'B', 'explanation': 'JSX lets you write HTML-like syntax inside JavaScript.'},
                {'question': 'What is the purpose of useState?', 'option_a': 'To define static values', 'option_b': 'To manage component state', 'option_c': 'To fetch data from APIs', 'option_d': 'To handle routing', 'correct_option': 'B', 'explanation': 'useState is a Hook that lets functional components manage state.'},
                {'question': 'What is a React component?', 'option_a': 'A CSS class', 'option_b': 'A reusable piece of UI', 'option_c': 'A database model', 'option_d': 'A server-side template', 'correct_option': 'B', 'explanation': 'React components are independent, reusable chunks of UI.'},
                {'question': 'When does useEffect run by default?', 'option_a': 'Only once', 'option_b': 'After every render', 'option_c': 'Before render', 'option_d': 'Never', 'correct_option': 'B', 'explanation': 'useEffect with no dependency array runs after every render.'},
                {'question': 'What are props in React?', 'option_a': 'Internal state of a component', 'option_b': 'Data passed from parent to child component', 'option_c': 'Event handlers', 'option_d': 'CSS properties', 'correct_option': 'B', 'explanation': 'Props (properties) pass data from parent to child components.'},
                {'question': 'What is the virtual DOM?', 'option_a': 'A server-side copy of the DOM', 'option_b': 'A lightweight in-memory representation of the real DOM', 'option_c': 'A CSS rendering engine', 'option_d': 'An alternative to HTML', 'correct_option': 'B', 'explanation': 'React uses a virtual DOM to efficiently update only changed parts of the real DOM.'},
                {'question': 'What is key prop used for in lists?', 'option_a': 'For styling list items', 'option_b': 'Help React identify which items changed', 'option_c': 'To handle click events', 'option_d': 'To set initial state', 'correct_option': 'B', 'explanation': 'Keys help React identify which list items have changed, improving performance.'},
                {'question': 'What does React.Fragment do?', 'option_a': 'Fragments style components', 'option_b': 'Groups multiple elements without adding extra DOM nodes', 'option_c': 'Creates lazy loaded components', 'option_d': 'Handles error boundaries', 'correct_option': 'B', 'explanation': 'React.Fragment lets you group elements without adding extra DOM nodes.'},
                {'question': 'What is Context API used for?', 'option_a': 'API calls', 'option_b': 'Sharing state across components without prop drilling', 'option_c': 'Debugging', 'option_d': 'Database connections', 'correct_option': 'B', 'explanation': 'Context provides a way to share values between components without passing props through every level.'},
                {'question': 'What is the difference between controlled and uncontrolled components?', 'option_a': 'Controlled use CSS; uncontrolled use JS', 'option_b': 'Controlled: form data managed by React state; Uncontrolled: managed by DOM', 'option_c': 'They are the same', 'option_d': 'Uncontrolled use hooks', 'correct_option': 'B', 'explanation': 'Controlled components have form data managed by React state via onChange + value.'},
            ],
        }

        created_count = 0
        for skill_name, questions in BUILTIN_QUESTIONS.items():
            skill, _ = Skill.objects.get_or_create(name=skill_name)
            for q in questions:
                _, created = SkillTestQuestion.objects.get_or_create(
                    skill=skill,
                    question=q['question'],
                    defaults={k: v for k, v in q.items() if k != 'question'}
                )
                if created:
                    created_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Generated {created_count} skill questions'))
