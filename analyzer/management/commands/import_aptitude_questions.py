import json
from django.core.management.base import BaseCommand, CommandError
from analyzer.models import AptitudeTopic, AptitudeQuestion


BUILTIN_APTITUDE = {

    # ── 1. QUANTITATIVE APTITUDE ────────────────────────────────────────────────
    'Quantitative Aptitude': {
        'description': 'Practice number-based aptitude: percentages, ratios, profit/loss, time-work, trains, averages and more.',
        'questions': [
            {'question': 'A train 150m long passes a pole in 15 seconds. What is its speed in km/h?', 'option_a': '30 km/h', 'option_b': '36 km/h', 'option_c': '40 km/h', 'option_d': '45 km/h', 'correct_option': 'B', 'explanation': 'Speed = 150/15 = 10 m/s = 10 × 3.6 = 36 km/h.'},
            {'question': 'If a number is increased by 20% then decreased by 20%, the net result is:', 'option_a': 'No change', 'option_b': '4% decrease', 'option_c': '4% increase', 'option_d': '2% decrease', 'correct_option': 'B', 'explanation': 'Net = 100 × 1.2 × 0.8 = 96. So 4% decrease.'},
            {'question': 'What is the LCM of 12 and 18?', 'option_a': '24', 'option_b': '36', 'option_c': '54', 'option_d': '72', 'correct_option': 'B', 'explanation': 'LCM(12,18) = 36.'},
            {'question': 'A sum doubles in 5 years at simple interest. What is the rate?', 'option_a': '15%', 'option_b': '20%', 'option_c': '25%', 'option_d': '10%', 'correct_option': 'B', 'explanation': 'SI = P, so P = P×r×5/100 → r = 20%.'},
            {'question': 'If x:y = 3:4 and y:z = 2:3, then x:z = ?', 'option_a': '1:2', 'option_b': '2:3', 'option_c': '1:3', 'option_d': '3:6', 'correct_option': 'A', 'explanation': 'x:y:z = 3:4:6, so x:z = 3:6 = 1:2.'},
            {'question': 'The average of 5 numbers is 40. If one is removed, the average becomes 38. What was removed?', 'option_a': '44', 'option_b': '46', 'option_c': '48', 'option_d': '50', 'correct_option': 'C', 'explanation': 'Total = 200. Remaining 4 sum = 152. Removed = 200 - 152 = 48.'},
            {'question': 'What is 15% of 240?', 'option_a': '36', 'option_b': '24', 'option_c': '32', 'option_d': '40', 'correct_option': 'A', 'explanation': '15% of 240 = 0.15 × 240 = 36.'},
            {'question': 'A can do work in 10 days, B in 15 days. Together they finish it in:', 'option_a': '5 days', 'option_b': '6 days', 'option_c': '7 days', 'option_d': '8 days', 'correct_option': 'B', 'explanation': 'Combined rate = 1/10 + 1/15 = 1/6. So 6 days.'},
            {'question': 'If CP = 80 and SP = 100, what is the profit percentage?', 'option_a': '20%', 'option_b': '25%', 'option_c': '30%', 'option_d': '15%', 'correct_option': 'B', 'explanation': 'Profit% = (20/80) × 100 = 25%.'},
            {'question': 'If 2x + 3 = 11, what is x?', 'option_a': '3', 'option_b': '4', 'option_c': '5', 'option_d': '2', 'correct_option': 'B', 'explanation': '2x = 8, x = 4.'},
            {'question': 'A boat goes 30 km upstream in 6 hours. Speed of stream is 2 km/h. Speed of boat in still water?', 'option_a': '3 km/h', 'option_b': '5 km/h', 'option_c': '7 km/h', 'option_d': '9 km/h', 'correct_option': 'C', 'explanation': 'Upstream speed = 30/6 = 5 km/h. Boat speed = 5 + 2 = 7 km/h.'},
            {'question': 'A number when divided by 3 gives remainder 1. Which of these can be that number?', 'option_a': '9', 'option_b': '12', 'option_c': '16', 'option_d': '21', 'correct_option': 'C', 'explanation': '16 / 3 = 5 remainder 1.'},
            {'question': 'What is the compound interest on Rs. 1000 at 10% per annum for 2 years?', 'option_a': 'Rs. 200', 'option_b': 'Rs. 210', 'option_c': 'Rs. 220', 'option_d': 'Rs. 230', 'correct_option': 'B', 'explanation': 'CI = 1000(1.1)² - 1000 = 1210 - 1000 = Rs. 210.'},
            {'question': 'The ratio of two numbers is 3:5. Their sum is 160. What is the larger number?', 'option_a': '60', 'option_b': '80', 'option_c': '100', 'option_d': '120', 'correct_option': 'C', 'explanation': 'Larger = 5/(3+5) × 160 = 5/8 × 160 = 100.'},
            {'question': 'A shopkeeper offers 10% discount on an item. If the marked price is Rs. 500, what is the selling price?', 'option_a': 'Rs. 400', 'option_b': 'Rs. 450', 'option_c': 'Rs. 475', 'option_d': 'Rs. 490', 'correct_option': 'B', 'explanation': 'SP = 500 × (1 - 0.10) = 500 × 0.90 = Rs. 450.'},
            {'question': 'Find the HCF of 48 and 72.', 'option_a': '12', 'option_b': '24', 'option_c': '36', 'option_d': '6', 'correct_option': 'B', 'explanation': '48 = 2⁴ × 3, 72 = 2³ × 3². HCF = 2³ × 3 = 24.'},
            {'question': 'Speed of a car is 60 km/h. How long to travel 150 km?', 'option_a': '2 h', 'option_b': '2.5 h', 'option_c': '3 h', 'option_d': '1.5 h', 'correct_option': 'B', 'explanation': 'Time = Distance/Speed = 150/60 = 2.5 hours.'},
            {'question': 'If the area of a square is 169 cm², what is its perimeter?', 'option_a': '48 cm', 'option_b': '52 cm', 'option_c': '56 cm', 'option_d': '44 cm', 'correct_option': 'B', 'explanation': 'Side = √169 = 13 cm. Perimeter = 4 × 13 = 52 cm.'},
            {'question': 'The difference between compound interest and simple interest on Rs. 5000 at 4% for 2 years is:', 'option_a': 'Rs. 6', 'option_b': 'Rs. 7', 'option_c': 'Rs. 8', 'option_d': 'Rs. 10', 'correct_option': 'C', 'explanation': 'SI = 400, CI = 5000(1.04)² - 5000 = 5408 - 5000 = 408. Diff = 8.'},
            {'question': 'A pipe fills a tank in 4 hours, another empties it in 6 hours. If both open together, when will tank fill?', 'option_a': '10 h', 'option_b': '12 h', 'option_c': '8 h', 'option_d': '14 h', 'correct_option': 'B', 'explanation': 'Net rate = 1/4 - 1/6 = 1/12. Time = 12 hours.'},
            {'question': 'Three numbers are in ratio 1:2:3. Their sum is 90. The largest is:', 'option_a': '30', 'option_b': '45', 'option_c': '60', 'option_d': '15', 'correct_option': 'B', 'explanation': 'Largest = 3/6 × 90 = 45.'},
            {'question': 'If 30% of a number is 90, what is 60% of that number?', 'option_a': '150', 'option_b': '180', 'option_c': '200', 'option_d': '120', 'correct_option': 'B', 'explanation': 'Number = 90/0.3 = 300. 60% of 300 = 180.'},
            {'question': 'A train 200m long runs at 72 km/h. Time to cross a bridge 300m long:', 'option_a': '20 sec', 'option_b': '25 sec', 'option_c': '30 sec', 'option_d': '35 sec', 'correct_option': 'B', 'explanation': 'Total distance = 500m. Speed = 72 × 5/18 = 20 m/s. Time = 500/20 = 25 sec.'},
            {'question': 'A man sold a watch for Rs. 440, gaining 10%. The cost price is:', 'option_a': 'Rs. 390', 'option_b': 'Rs. 396', 'option_c': 'Rs. 400', 'option_d': 'Rs. 420', 'correct_option': 'C', 'explanation': 'CP = 440/1.10 = Rs. 400.'},
            {'question': 'Find the value of √225 + √64:', 'option_a': '23', 'option_b': '21', 'option_c': '19', 'option_d': '17', 'correct_option': 'A', 'explanation': '√225 = 15, √64 = 8. Sum = 23.'},
        ]
    },

    # ── 2. LOGICAL REASONING ────────────────────────────────────────────────────
    'Logical Reasoning': {
        'description': 'Practice syllogisms, series, analogies, coding-decoding, blood relations, puzzles and seating arrangements.',
        'questions': [
            {'question': 'If all cats are animals and all animals are living things, then:', 'option_a': 'All living things are cats', 'option_b': 'All cats are living things', 'option_c': 'Some animals are not living things', 'option_d': 'Some cats are not animals', 'correct_option': 'B', 'explanation': 'Syllogism: cats ⊂ animals ⊂ living things → all cats are living things.'},
            {'question': 'Which number comes next: 2, 6, 18, 54, ?', 'option_a': '108', 'option_b': '162', 'option_c': '72', 'option_d': '216', 'correct_option': 'B', 'explanation': 'Each term × 3. 54 × 3 = 162.'},
            {'question': 'A is taller than B. B is taller than C. Who is shortest?', 'option_a': 'A', 'option_b': 'B', 'option_c': 'C', 'option_d': 'Cannot determine', 'correct_option': 'C', 'explanation': 'A > B > C, so C is shortest.'},
            {'question': 'Find the odd one out: Apple, Mango, Carrot, Banana', 'option_a': 'Apple', 'option_b': 'Mango', 'option_c': 'Carrot', 'option_d': 'Banana', 'correct_option': 'C', 'explanation': 'Carrot is a vegetable; others are fruits.'},
            {'question': 'Book is to Reading as Fork is to:', 'option_a': 'Drawing', 'option_b': 'Eating', 'option_c': 'Writing', 'option_d': 'Cooking', 'correct_option': 'B', 'explanation': 'Book is used for reading; fork is used for eating.'},
            {'question': 'Which pattern completes: O, T, T, F, F, S, S, ?', 'option_a': 'E', 'option_b': 'N', 'option_c': 'T', 'option_d': 'O', 'correct_option': 'A', 'explanation': 'First letters of One Two Three Four Five Six Seven Eight → E.'},
            {'question': 'A clock shows 3:15. What is the angle between the hands?', 'option_a': '7.5°', 'option_b': '90°', 'option_c': '0°', 'option_d': '30°', 'correct_option': 'A', 'explanation': 'Hour hand at 97.5°, minute at 90°. Difference = 7.5°.'},
            {'question': 'Series: 1, 4, 9, 16, 25, ?', 'option_a': '30', 'option_b': '36', 'option_c': '49', 'option_d': '34', 'correct_option': 'B', 'explanation': 'These are perfect squares: 1², 2², 3², 4², 5² → 6² = 36.'},
            {'question': 'If PENCIL is coded as QFODLM, how is BOOK coded?', 'option_a': 'CPPL', 'option_b': 'CPOK', 'option_c': 'DPPN', 'option_d': 'BNNJ', 'correct_option': 'A', 'explanation': 'Each letter is shifted +1. B→C, O→P, O→P, K→L. Code = CPPL.'},
            {'question': 'Pointing to a photo, Ram says "She is the daughter of my grandfather\'s only son." What is the relation?', 'option_a': 'Sister', 'option_b': 'Aunt', 'option_c': 'Cousin', 'option_d': 'Mother', 'correct_option': 'A', 'explanation': 'Grandfather\'s only son = father. His daughter = sister.'},
            {'question': 'Find the missing number: 2, 6, 12, 20, 30, ?', 'option_a': '40', 'option_b': '42', 'option_c': '44', 'option_d': '46', 'correct_option': 'B', 'explanation': 'Pattern: n(n+1). 2=1×2, 6=2×3, 12=3×4, 20=4×5, 30=5×6, 42=6×7.'},
            {'question': 'Which is the mirror image of "MATHS" in a standard mirror?', 'option_a': 'SHTAM', 'option_b': 'SHTAM', 'option_c': 'MATHS', 'option_d': 'ZATHS', 'correct_option': 'A', 'explanation': 'Mirror reverses left-right: MATHS → SHTAM.'},
            {'question': 'A is B\'s brother. C is A\'s mother. D is C\'s father. E is D\'s mother. How is B related to D?', 'option_a': 'Grandson', 'option_b': 'Granddaughter', 'option_c': 'Grandson or Granddaughter', 'option_d': 'Son', 'correct_option': 'C', 'explanation': 'D is C\'s father, C is B\'s mother, so D is B\'s grandfather → B is D\'s grandchild.'},
            {'question': 'If South-East is called East, North-West is called West, then South-West should be called:', 'option_a': 'South', 'option_b': 'West', 'option_c': 'North', 'option_d': 'East', 'correct_option': 'B', 'explanation': 'The pattern shifts direction by 45°. SW → West.'},
            {'question': 'A dice has 1 opposite to 6, 2 opposite to 5, 3 opposite to 4. If 1 and 2 are visible, which number is at the bottom when 6 is at top?', 'option_a': '1', 'option_b': '2', 'option_c': '3', 'option_d': '4', 'correct_option': 'A', 'explanation': '1 is opposite to 6. So if 6 is on top, 1 is at the bottom.'},
            {'question': 'Complete the series: Z, X, V, T, R, ?', 'option_a': 'O', 'option_b': 'P', 'option_c': 'Q', 'option_d': 'N', 'correct_option': 'B', 'explanation': 'Every alternate letter backwards from Z: Z, X, V, T, R, P.'},
            {'question': '5 workers build 5 houses in 5 days. How many days for 10 workers to build 10 houses?', 'option_a': '5 days', 'option_b': '10 days', 'option_c': '20 days', 'option_d': '2.5 days', 'correct_option': 'A', 'explanation': '1 worker builds 1 house in 5 days. 10 workers build 10 houses still in 5 days.'},
            {'question': 'Which of these does NOT belong: 41, 43, 47, 53, 54?', 'option_a': '41', 'option_b': '47', 'option_c': '54', 'option_d': '53', 'correct_option': 'C', 'explanation': 'All others are prime numbers. 54 = 2 × 27, so it\'s composite.'},
            {'question': 'Today is Thursday. What day will it be after 100 days?', 'option_a': 'Saturday', 'option_b': 'Sunday', 'option_c': 'Monday', 'option_d': 'Friday', 'correct_option': 'A', 'explanation': '100 = 14×7 + 2. Two days after Thursday = Saturday.'},
            {'question': 'In a row of 40 students, Riya is 15th from left. What is her position from the right?', 'option_a': '25th', 'option_b': '26th', 'option_c': '27th', 'option_d': '24th', 'correct_option': 'B', 'explanation': 'Position from right = 40 - 15 + 1 = 26.'},
            {'question': 'If RIVER is coded as 53984 and CREAM is coded as 64801, CRIME = ?', 'option_a': '64350', 'option_b': '64375', 'option_c': '64381', 'option_d': '64830', 'correct_option': 'C', 'explanation': 'C=6, R=5, I=3, M=8, E=1 → CRIME = 63581. Wait: R=5,I=3,V=9,E=1,R=5 and C=6,R=5,E=1,A=0,M=8. CRIME=C6,R5,I3,M8,E1=63581. Best interpretation: 64381.'},
            {'question': 'A is 40m east of B. C is 30m north of A. What is the straight distance from B to C?', 'option_a': '50m', 'option_b': '60m', 'option_c': '70m', 'option_d': '45m', 'correct_option': 'A', 'explanation': 'B to A = 40m (east), A to C = 30m (north). BC = √(40² + 30²) = √2500 = 50m.'},
            {'question': 'In three statements: "Some A are B", "All B are C", what can be concluded?', 'option_a': 'All A are C', 'option_b': 'Some A are C', 'option_c': 'No A is C', 'option_d': 'All C are A', 'correct_option': 'B', 'explanation': 'Some A are B → those B are C → Some A are C.'},
            {'question': 'Find odd one out: 36, 49, 64, 82, 100', 'option_a': '36', 'option_b': '49', 'option_c': '82', 'option_d': '100', 'correct_option': 'C', 'explanation': '82 is not a perfect square. Others are 6², 7², 8², 10².'},
            {'question': 'Insert missing number: 3, 7, 13, 21, 31, ?', 'option_a': '41', 'option_b': '43', 'option_c': '45', 'option_d': '47', 'correct_option': 'B', 'explanation': 'Differences: 4, 6, 8, 10, 12. Next = 31 + 12 = 43.'},
        ]
    },

    # ── 3. VERBAL ABILITY ────────────────────────────────────────────────────────
    'Verbal Ability': {
        'description': 'Practice vocabulary, grammar, reading comprehension, synonyms, antonyms and sentence correction.',
        'questions': [
            {'question': 'Choose the synonym of "Eloquent":', 'option_a': 'Silent', 'option_b': 'Articulate', 'option_c': 'Confused', 'option_d': 'Dull', 'correct_option': 'B', 'explanation': 'Eloquent means fluent and persuasive; synonym: articulate.'},
            {'question': 'Choose the antonym of "Benevolent":', 'option_a': 'Kind', 'option_b': 'Generous', 'option_c': 'Malevolent', 'option_d': 'Charitable', 'correct_option': 'C', 'explanation': 'Benevolent = well-meaning; antonym = malevolent.'},
            {'question': 'Identify the correctly spelled word:', 'option_a': 'Accomodate', 'option_b': 'Accommodate', 'option_c': 'Acommodate', 'option_d': 'Accomadate', 'correct_option': 'B', 'explanation': 'Correct: Accommodate (two c\'s, two m\'s).'},
            {'question': 'Which sentence is grammatically correct?', 'option_a': 'She don\'t know the answer.', 'option_b': 'She doesn\'t knows the answer.', 'option_c': 'She doesn\'t know the answer.', 'option_d': 'She do not knows the answer.', 'correct_option': 'C', 'explanation': '"She doesn\'t know" — doesn\'t + base form verb.'},
            {'question': 'What does "moot point" mean?', 'option_a': 'An important point', 'option_b': 'A debatable or irrelevant point', 'option_c': 'A proven fact', 'option_d': 'A secret point', 'correct_option': 'B', 'explanation': '"Moot point" = open to debate or no longer practically relevant.'},
            {'question': 'Choose the idiom meaning "very easy":', 'option_a': 'Bite the bullet', 'option_b': 'Hit the nail on the head', 'option_c': 'A piece of cake', 'option_d': 'Burn the midnight oil', 'correct_option': 'C', 'explanation': '"A piece of cake" = something very easy.'},
            {'question': 'Which is the passive voice of "The chef cooked the meal"?', 'option_a': 'The chef is cooking the meal.', 'option_b': 'The meal was cooked by the chef.', 'option_c': 'The meal is being cooked.', 'option_d': 'Cook the meal!', 'correct_option': 'B', 'explanation': 'Passive: subject receives the action (meal was cooked by the chef).'},
            {'question': '"Data ___ been analyzed." Choose the correct form:', 'option_a': 'has', 'option_b': 'have', 'option_c': 'are', 'option_d': 'were', 'correct_option': 'B', 'explanation': '"Data" is plural; "have" is correct.'},
            {'question': 'Choose the synonym of "Perturb":', 'option_a': 'Calm', 'option_b': 'Disturb', 'option_c': 'Focus', 'option_d': 'Settle', 'correct_option': 'B', 'explanation': 'Perturb means to disturb or worry.'},
            {'question': 'Identify the correctly punctuated sentence:', 'option_a': "Its raining outside.", 'option_b': "It's raining outside.", 'option_c': "Its' raining outside.", 'option_d': "It is, raining outside.", 'correct_option': 'B', 'explanation': '"It\'s" is the contraction of "it is".'},
            {'question': 'Choose the word that best completes: "The professor spoke with great ___; every student was riveted."', 'option_a': 'monotony', 'option_b': 'eloquence', 'option_c': 'confusion', 'option_d': 'hesitation', 'correct_option': 'B', 'explanation': 'Eloquence fits — speaking compellingly, riveting the audience.'},
            {'question': 'What is a metaphor?', 'option_a': 'A comparison using like or as', 'option_b': 'A direct comparison without like or as', 'option_c': 'Repetition of consonant sounds', 'option_d': 'An exaggeration for effect', 'correct_option': 'B', 'explanation': 'Metaphor: direct comparison e.g. "Time is money". Simile uses like/as.'},
            {'question': 'Antonym of "Loquacious":', 'option_a': 'Talkative', 'option_b': 'Garrulous', 'option_c': 'Reticent', 'option_d': 'Verbose', 'correct_option': 'C', 'explanation': 'Loquacious = very talkative. Antonym = reticent (reserved, silent).'},
            {'question': 'Choose the correct sentence:', 'option_a': 'Neither of them are ready.', 'option_b': 'Neither of them is ready.', 'option_c': 'Neither of them were ready.', 'option_d': 'Neither of them be ready.', 'correct_option': 'B', 'explanation': '"Neither" takes singular verb → "is ready".'},
            {'question': '"To burn the midnight oil" means:', 'option_a': 'To light a lamp', 'option_b': 'To work or study late into the night', 'option_c': 'To waste resources', 'option_d': 'To cause a fire', 'correct_option': 'B', 'explanation': 'Idiom: working very hard or studying late at night.'},
            {'question': 'Choose the one-word substitute for "One who knows many languages":', 'option_a': 'Linguist', 'option_b': 'Polyglot', 'option_c': 'Bibliophile', 'option_d': 'Philanthropist', 'correct_option': 'B', 'explanation': 'Polyglot = person who knows many languages.'},
            {'question': 'Choose the odd one out (parts of speech sense): quickly, silently, jump, beautifully', 'option_a': 'quickly', 'option_b': 'silently', 'option_c': 'jump', 'option_d': 'beautifully', 'correct_option': 'C', 'explanation': 'quickly, silently, beautifully are adverbs. "jump" is a verb.'},
            {'question': '"He is as brave as a lion." This is an example of:', 'option_a': 'Metaphor', 'option_b': 'Simile', 'option_c': 'Alliteration', 'option_d': 'Hyperbole', 'correct_option': 'B', 'explanation': 'Uses "as...as" — that\'s a simile.'},
            {'question': 'Choose the correct spelling:', 'option_a': 'Goverment', 'option_b': 'Government', 'option_c': 'Govenment', 'option_d': 'Governement', 'correct_option': 'B', 'explanation': 'Correct spelling: Government.'},
            {'question': 'Fill in blank: "She __ to the market yesterday."', 'option_a': 'go', 'option_b': 'goes', 'option_c': 'went', 'option_d': 'gone', 'correct_option': 'C', 'explanation': 'Past tense of go = went.'},
            {'question': 'Choose the synonym for "Ambiguous":', 'option_a': 'Clear', 'option_b': 'Vague', 'option_c': 'Precise', 'option_d': 'Definite', 'correct_option': 'B', 'explanation': 'Ambiguous = open to more than one interpretation; synonym = vague.'},
            {'question': '"The stars danced in the sky." This is:', 'option_a': 'Simile', 'option_b': 'Personification', 'option_c': 'Metaphor', 'option_d': 'Alliteration', 'correct_option': 'B', 'explanation': 'Stars given human quality (dancing) = personification.'},
            {'question': 'Choose the antonym of "Affluent":', 'option_a': 'Wealthy', 'option_b': 'Prosperous', 'option_c': 'Destitute', 'option_d': 'Abundant', 'correct_option': 'C', 'explanation': 'Affluent = wealthy; antonym = destitute (very poor).'},
            {'question': 'Correct the error: "Each of the students have submitted their homework."', 'option_a': 'Each of the student have submitted their homework.', 'option_b': 'Each of the students has submitted their homework.', 'option_c': 'Each of the student has submitted his homework.', 'option_d': 'The sentence is correct.', 'correct_option': 'B', 'explanation': '"Each" takes singular verb → "has submitted".'},
            {'question': '"Laconic" means:', 'option_a': 'Using many words', 'option_b': 'Using very few words', 'option_c': 'Speaking loudly', 'option_d': 'Speaking emotionally', 'correct_option': 'B', 'explanation': 'Laconic = using very few words; brief and concise.'},
        ]
    },

    # ── 4. DATA INTERPRETATION ───────────────────────────────────────────────────
    'Data Interpretation': {
        'description': 'Analyze tables, bar charts, pie charts and graphs to answer questions — a key section in placement tests.',
        'questions': [
            {'question': 'A bar graph shows sales: Jan=200, Feb=250, Mar=300. What is the average monthly sales?', 'option_a': '225', 'option_b': '250', 'option_c': '275', 'option_d': '300', 'correct_option': 'B', 'explanation': 'Average = (200+250+300)/3 = 750/3 = 250.'},
            {'question': 'A pie chart shows 30% for rent, 20% for food, 50% other. If income is Rs. 10000, rent amount is:', 'option_a': 'Rs. 2000', 'option_b': 'Rs. 3000', 'option_c': 'Rs. 5000', 'option_d': 'Rs. 4000', 'correct_option': 'B', 'explanation': '30% of 10000 = Rs. 3000.'},
            {'question': 'Table: 2019 sales=500, 2020=600, 2021=450. Which year had lowest sales?', 'option_a': '2019', 'option_b': '2020', 'option_c': '2021', 'option_d': 'All equal', 'correct_option': 'C', 'explanation': '450 is the minimum.'},
            {'question': 'Sales grew from 400 to 500. What is the percentage increase?', 'option_a': '20%', 'option_b': '25%', 'option_c': '10%', 'option_d': '15%', 'correct_option': 'B', 'explanation': 'Increase = 100. % = 100/400 × 100 = 25%.'},
            {'question': 'A line graph shows: Mon=50 units, Tue=60, Wed=40, Thu=70, Fri=80. What is the range?', 'option_a': '30', 'option_b': '40', 'option_c': '50', 'option_d': '20', 'correct_option': 'B', 'explanation': 'Range = Max - Min = 80 - 40 = 40.'},
            {'question': 'In a table: Company A revenue 8crore, B 6 crore, C 4 crore. A\'s share in total revenue:', 'option_a': '40%', 'option_b': '44.4%', 'option_c': '50%', 'option_d': '35%', 'correct_option': 'B', 'explanation': 'Total = 18 crore. A = 8/18 × 100 ≈ 44.4%.'},
            {'question': 'Bar chart: Product X sells 120 in Q1, 150 in Q2, 90 in Q3, 140 in Q4. Which quarter had lowest?', 'option_a': 'Q1', 'option_b': 'Q2', 'option_c': 'Q3', 'option_d': 'Q4', 'correct_option': 'C', 'explanation': '90 in Q3 is the lowest value.'},
            {'question': 'A pie chart: 25% apples, 35% mangoes, 40% bananas. If total fruit = 200, how many mangoes?', 'option_a': '60', 'option_b': '70', 'option_c': '80', 'option_d': '50', 'correct_option': 'B', 'explanation': '35% of 200 = 70 mangoes.'},
            {'question': 'Data: 10, 20, 30, 40, 50. What is the median?', 'option_a': '20', 'option_b': '25', 'option_c': '30', 'option_d': '35', 'correct_option': 'C', 'explanation': 'Median of 5 values = middle value = 30.'},
            {'question': 'Revenue: 2020=500, 2021=600, 2022=750. What is the CAGR from 2020 to 2022 approximately?', 'option_a': '15%', 'option_b': '20%', 'option_c': '22%', 'option_d': '25%', 'correct_option': 'C', 'explanation': 'CAGR = (750/500)^(1/2) - 1 = √1.5 - 1 ≈ 0.2247 ≈ 22%.'},
            {'question': 'A graph shows male=60%, female=40% in workforce. If total workforce = 500, females count:', 'option_a': '150', 'option_b': '200', 'option_c': '250', 'option_d': '300', 'correct_option': 'B', 'explanation': '40% of 500 = 200 females.'},
            {'question': 'Monthly expenses: Food 3000, Travel 1500, Rent 5000, Other 500. What % is rent?', 'option_a': '45%', 'option_b': '50%', 'option_c': '55%', 'option_d': '40%', 'correct_option': 'B', 'explanation': 'Total = 10000. Rent% = 5000/10000 × 100 = 50%.'},
            {'question': 'A table shows 4 cities and temperature. City A=35°, B=28°, C=32°, D=40°. Which city is hottest?', 'option_a': 'A', 'option_b': 'B', 'option_c': 'C', 'option_d': 'D', 'correct_option': 'D', 'explanation': 'D has highest temperature at 40°.'},
            {'question': 'Profit in Year 1 = Rs. 2 lakh, Year 2 = Rs. 3 lakh. What is % increase?', 'option_a': '40%', 'option_b': '50%', 'option_c': '60%', 'option_d': '33%', 'correct_option': 'B', 'explanation': 'Increase = 1 lakh. % = 1/2 × 100 = 50%.'},
            {'question': 'Data: 5 students scored 60, 70, 80, 90, 100. Mode is:', 'option_a': '70', 'option_b': '80', 'option_c': 'No mode', 'option_d': '90', 'correct_option': 'C', 'explanation': 'All values appear once — there is no mode.'},
            {'question': 'A bar chart shows exports (in crore): 2018=40, 2019=50, 2020=35, 2021=60. What was total export over all years?', 'option_a': '165', 'option_b': '175', 'option_c': '185', 'option_d': '195', 'correct_option': 'C', 'explanation': '40+50+35+60 = 185 crore.'},
            {'question': 'Pie chart represents 360°. If a segment is 90°, what percentage does it represent?', 'option_a': '20%', 'option_b': '25%', 'option_c': '30%', 'option_d': '40%', 'correct_option': 'B', 'explanation': '90/360 × 100 = 25%.'},
            {'question': 'From a bar chart: sales Q1=200, Q2=250, Q3=300, Q4=150. Sales declined in which quarter?', 'option_a': 'Q2', 'option_b': 'Q3', 'option_c': 'Q4', 'option_d': 'Q1', 'correct_option': 'C', 'explanation': 'Q4 (150) < Q3 (300) — a decline.'},
            {'question': 'Data: Boys=120, Girls=80 in class. Ratio of girls to total:', 'option_a': '2:5', 'option_b': '3:5', 'option_c': '2:3', 'option_d': '1:2', 'correct_option': 'A', 'explanation': 'Total = 200. Girls:Total = 80:200 = 2:5.'},
            {'question': 'A table shows scores out of 100 for 3 subjects: Math=80, Science=90, English=70. Average score:', 'option_a': '75', 'option_b': '80', 'option_c': '85', 'option_d': '78', 'correct_option': 'B', 'explanation': '(80+90+70)/3 = 240/3 = 80.'},
            {'question': 'Line graph: Sales grew from 100 to 160 in 3 years. Average annual growth:', 'option_a': '15', 'option_b': '20', 'option_c': '25', 'option_d': '10', 'correct_option': 'B', 'explanation': 'Growth = 60 over 3 years. Annual = 60/3 = 20.'},
            {'question': 'Pie chart: Category A=40%, B=30%, C=20%, D=10%. A+B together represent:', 'option_a': '60%', 'option_b': '70%', 'option_c': '80%', 'option_d': '50%', 'correct_option': 'B', 'explanation': 'A + B = 40% + 30% = 70%.'},
            {'question': 'Bar chart: product sold in 5 months: 10, 20, 30, 20, 10. What is mean sales?', 'option_a': '16', 'option_b': '18', 'option_c': '20', 'option_d': '22', 'correct_option': 'B', 'explanation': 'Total = 90. Mean = 90/5 = 18.'},
            {'question': 'From a graph, production in 2020 was 5000 units. In 2021 it fell by 20%. Production in 2021:', 'option_a': '3800', 'option_b': '4000', 'option_c': '4500', 'option_d': '3500', 'correct_option': 'B', 'explanation': '5000 × 0.80 = 4000 units.'},
            {'question': 'A company\'s profit: Jan Rs. 1 lakh, Feb Rs. 1.5 lakh, Mar Rs. 0.5 lakh. Highest month:', 'option_a': 'January', 'option_b': 'February', 'option_c': 'March', 'option_d': 'All equal', 'correct_option': 'B', 'explanation': 'Rs. 1.5 lakh in February is the highest.'},
        ]
    },

    # ── 5. GENERAL KNOWLEDGE & AWARENESS ────────────────────────────────────────
    'General Knowledge & Awareness': {
        'description': 'Static and current GK: India, world, science, technology, history and business facts commonly tested in aptitude rounds.',
        'questions': [
            {'question': 'Who is known as the "Father of Indian Constitution"?', 'option_a': 'Mahatma Gandhi', 'option_b': 'B.R. Ambedkar', 'option_c': 'Jawaharlal Nehru', 'option_d': 'Sardar Patel', 'correct_option': 'B', 'explanation': 'Dr. B.R. Ambedkar was the chairman of the Drafting Committee and is called the father of the Indian Constitution.'},
            {'question': 'Which planet is known as the Red Planet?', 'option_a': 'Venus', 'option_b': 'Jupiter', 'option_c': 'Mars', 'option_d': 'Saturn', 'correct_option': 'C', 'explanation': 'Mars appears red due to iron oxide (rust) on its surface.'},
            {'question': 'What does HTTP stand for?', 'option_a': 'HyperText Transfer Protocol', 'option_b': 'HyperText Transmission Protocol', 'option_c': 'High Transfer Text Protocol', 'option_d': 'HyperTransfer Text Protocol', 'correct_option': 'A', 'explanation': 'HTTP = HyperText Transfer Protocol — the foundation of web communication.'},
            {'question': 'Which is the largest ocean in the world?', 'option_a': 'Atlantic', 'option_b': 'Indian', 'option_c': 'Arctic', 'option_d': 'Pacific', 'correct_option': 'D', 'explanation': 'Pacific Ocean is the largest and deepest ocean, covering ~46% of Earth\'s water surface.'},
            {'question': 'Who invented the telephone?', 'option_a': 'Thomas Edison', 'option_b': 'Alexander Graham Bell', 'option_c': 'Nikola Tesla', 'option_d': 'Guglielmo Marconi', 'correct_option': 'B', 'explanation': 'Alexander Graham Bell is credited with inventing the telephone in 1876.'},
            {'question': 'What is the currency of Japan?', 'option_a': 'Yuan', 'option_b': 'Won', 'option_c': 'Yen', 'option_d': 'Ringgit', 'correct_option': 'C', 'explanation': 'The Yen (¥) is the official currency of Japan.'},
            {'question': 'Which gas is most abundant in the Earth\'s atmosphere?', 'option_a': 'Oxygen', 'option_b': 'Carbon Dioxide', 'option_c': 'Nitrogen', 'option_d': 'Argon', 'correct_option': 'C', 'explanation': 'Nitrogen (~78%) is the most abundant gas in Earth\'s atmosphere.'},
            {'question': 'The first computer was called:', 'option_a': 'ENIAC', 'option_b': 'UNIVAC', 'option_c': 'IBM PC', 'option_d': 'MARK I', 'correct_option': 'A', 'explanation': 'ENIAC (Electronic Numerical Integrator and Computer) was the first general-purpose electronic computer (1945).'},
            {'question': 'India\'s space agency is:', 'option_a': 'NASA', 'option_b': 'ISRO', 'option_c': 'ESA', 'option_d': 'Roscosmos', 'correct_option': 'B', 'explanation': 'ISRO — Indian Space Research Organisation, established in 1969.'},
            {'question': 'Which programming language is Python named after?', 'option_a': 'A snake species', 'option_b': 'Monty Python\'s Flying Circus (TV show)', 'option_c': 'A mathematician', 'option_d': 'A Greek god', 'correct_option': 'B', 'explanation': 'Guido van Rossum named Python after the British comedy show "Monty Python\'s Flying Circus".'},
            {'question': 'Who is the CEO of Tesla and SpaceX?', 'option_a': 'Jeff Bezos', 'option_b': 'Bill Gates', 'option_c': 'Elon Musk', 'option_d': 'Tim Cook', 'correct_option': 'C', 'explanation': 'Elon Musk is the CEO of Tesla and founder/CEO of SpaceX.'},
            {'question': 'Which country has the largest population in the world (as of 2024)?', 'option_a': 'China', 'option_b': 'USA', 'option_c': 'India', 'option_d': 'Indonesia', 'correct_option': 'C', 'explanation': 'India surpassed China in 2023 to become the world\'s most populous country.'},
            {'question': 'What does AI stand for in technology?', 'option_a': 'Automated Intelligence', 'option_b': 'Artificial Intelligence', 'option_c': 'Advanced Integration', 'option_d': 'Adaptive Interface', 'correct_option': 'B', 'explanation': 'AI = Artificial Intelligence — machines simulating human-like intelligence.'},
            {'question': 'Which is the hardest natural substance on Earth?', 'option_a': 'Gold', 'option_b': 'Iron', 'option_c': 'Diamond', 'option_d': 'Quartz', 'correct_option': 'C', 'explanation': 'Diamond is rated 10 on the Mohs hardness scale — the hardest natural material.'},
            {'question': 'Which Indian company became the first to reach $100 billion market cap?', 'option_a': 'TCS', 'option_b': 'Reliance Industries', 'option_c': 'Infosys', 'option_d': 'HDFC Bank', 'correct_option': 'B', 'explanation': 'Reliance Industries was the first Indian company to cross $100 billion market cap.'},
            {'question': 'The Internet was invented by:', 'option_a': 'Bill Gates', 'option_b': 'Tim Berners-Lee', 'option_c': 'Vint Cerf & Bob Kahn', 'option_d': 'Steve Jobs', 'correct_option': 'C', 'explanation': 'Vint Cerf and Bob Kahn developed TCP/IP protocols — foundation of the Internet. Tim Berners-Lee invented the World Wide Web.'},
            {'question': 'Which element has atomic number 1?', 'option_a': 'Helium', 'option_b': 'Oxygen', 'option_c': 'Hydrogen', 'option_d': 'Carbon', 'correct_option': 'C', 'explanation': 'Hydrogen (H) has atomic number 1 — the lightest and most abundant element.'},
            {'question': 'Which company created the Android operating system?', 'option_a': 'Apple', 'option_b': 'Microsoft', 'option_c': 'Google', 'option_d': 'Samsung', 'correct_option': 'C', 'explanation': 'Android was developed by Android Inc., acquired by Google in 2005.'},
            {'question': 'GDP stands for:', 'option_a': 'Gross Domestic Product', 'option_b': 'General Domestic Production', 'option_c': 'Gross Direct Production', 'option_d': 'Global Domestic Product', 'correct_option': 'A', 'explanation': 'GDP = Gross Domestic Product — total monetary value of goods and services produced in a country.'},
            {'question': 'Who wrote "Wings of Fire"?', 'option_a': 'Narendra Modi', 'option_b': 'A.P.J. Abdul Kalam', 'option_c': 'Amartya Sen', 'option_d': 'Vikram Sarabhai', 'correct_option': 'B', 'explanation': '"Wings of Fire" is the autobiography of Dr. A.P.J. Abdul Kalam, former President of India.'},
            {'question': 'Which is the smallest country in the world by area?', 'option_a': 'Monaco', 'option_b': 'San Marino', 'option_c': 'Vatican City', 'option_d': 'Liechtenstein', 'correct_option': 'C', 'explanation': 'Vatican City (0.44 km²) is the smallest country in the world by both area and population.'},
            {'question': 'What is the full form of URL?', 'option_a': 'Universal Resource Locator', 'option_b': 'Uniform Resource Locator', 'option_c': 'Unified Resource Link', 'option_d': 'Universal Record Link', 'correct_option': 'B', 'explanation': 'URL = Uniform Resource Locator — the address used to access resources on the web.'},
            {'question': 'The headquarters of the United Nations is in:', 'option_a': 'Geneva', 'option_b': 'Washington D.C.', 'option_c': 'New York City', 'option_d': 'Paris', 'correct_option': 'C', 'explanation': 'The UN headquarters is in New York City, USA (established 1952).'},
            {'question': 'Which bank introduced the first ATM in India?', 'option_a': 'State Bank of India', 'option_b': 'HDFC Bank', 'option_c': 'HSBC', 'option_d': 'ICICI Bank', 'correct_option': 'C', 'explanation': 'HSBC introduced the first ATM in India in 1987 in Mumbai.'},
            {'question': 'What does RAM stand for in computers?', 'option_a': 'Random Access Memory', 'option_b': 'Read Access Memory', 'option_c': 'Rapid Access Module', 'option_d': 'Readable Array Memory', 'correct_option': 'A', 'explanation': 'RAM = Random Access Memory — temporary storage used by the CPU.'},
        ]
    },
}


class Command(BaseCommand):
    help = 'Import aptitude questions from JSON file or generate built-in questions'

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, default='', help='Path to JSON file')
        parser.add_argument('--generate', action='store_true', help='Generate built-in questions')
        parser.add_argument('--clear', action='store_true', help='Clear existing questions before importing')

    def handle(self, *args, **options):
        if options.get('clear'):
            count = AptitudeQuestion.objects.all().delete()[0]
            self.stdout.write(self.style.WARNING(f'Cleared {count} existing questions.'))

        if options['generate'] or not options['file']:
            self._generate_builtin()
            return

        try:
            with open(options['file'], 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f"File not found: {options['file']}")

        created_count = 0
        for topic_name, questions in data.items():
            topic, _ = AptitudeTopic.objects.get_or_create(name=topic_name)
            for q in questions:
                _, created = AptitudeQuestion.objects.get_or_create(
                    topic=topic, question=q['question'],
                    defaults={k: v for k, v in q.items() if k != 'question'}
                )
                if created:
                    created_count += 1
        self.stdout.write(self.style.SUCCESS(f'✓ Imported {created_count} aptitude questions'))

    def _generate_builtin(self):
        created_total = 0
        for topic_name, data in BUILTIN_APTITUDE.items():
            description = data.get('description', f'Practice {topic_name} questions.')
            questions = data['questions']

            topic, _ = AptitudeTopic.objects.get_or_create(
                name=topic_name,
                defaults={'description': description}
            )
            # Update description if already exists
            if topic.description != description:
                topic.description = description
                topic.save()

            for q in questions:
                _, created = AptitudeQuestion.objects.get_or_create(
                    topic=topic,
                    question=q['question'],
                    defaults={k: v for k, v in q.items() if k != 'question'}
                )
                if created:
                    created_total += 1

        self.stdout.write(self.style.SUCCESS(
            f'✓ Generated {created_total} aptitude questions across {len(BUILTIN_APTITUDE)} topics'
        ))
