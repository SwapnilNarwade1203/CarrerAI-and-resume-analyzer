from django.core.management.base import BaseCommand
from analyzer.models import CompanyQuestion

# (company_name, job_role, question, answer_hints, category)
COMPANY_QUESTIONS = [

    # ── Google ──────────────────────────────────────────────────────────────
    ('Google', 'Software Engineer', 'What is the time complexity of searching in a balanced BST?', 'O(log n) — the height of a balanced BST is log n.', 'technical'),
    ('Google', 'Software Engineer', 'Explain the difference between a process and a thread.', 'Processes are independent; threads share memory within a process. Context-switch is cheaper for threads.', 'technical'),
    ('Google', 'Software Engineer', 'How does Google Search index web pages?', 'Crawling → indexing (inverted index) → ranking (PageRank + ML signals).', 'technical'),
    ('Google', 'Software Engineer', 'Design a URL shortener like bit.ly.', 'Hash/encode the URL to a 6-char key, store in DB, redirect on lookup. Discuss collisions, caching, analytics.', 'technical'),
    ('Google', 'Software Engineer', 'Tell me about a time you disagreed with your manager.', 'Use STAR — show you raised concerns respectfully and reached a good outcome.', 'behavioral'),
    ('Google', 'Software Engineer', 'How would you improve Google Maps?', 'Identify user pain points, propose features, prioritise by impact/effort.', 'situational'),
    ('Google', 'Data Scientist', 'How do you detect a biased ML model?', 'Check fairness metrics (demographic parity, equalised odds), confusion matrices per group, data distribution analysis.', 'technical'),
    ('Google', 'Data Scientist', 'What is the difference between L1 and L2 regularisation?', 'L1 (Lasso) produces sparse weights; L2 (Ridge) shrinks weights but rarely to zero.', 'technical'),
    ('Google', 'Data Scientist', 'Explain how you would A/B test a new feature.', 'Define hypothesis, split traffic randomly, run for statistical significance, measure primary + guardrail metrics.', 'technical'),
    ('Google', 'Product Manager', 'How would you prioritise features for Google Photos?', 'Use frameworks like RICE or ICE; align with user needs, business goals, and engineering effort.', 'situational'),
    ('Google', 'Product Manager', 'Describe a product you admire and why.', 'Focus on design decisions, user value, and metrics — show structured product thinking.', 'behavioral'),

    # ── Amazon ──────────────────────────────────────────────────────────────
    ('Amazon', 'Software Engineer', 'What is the difference between SQS and SNS?', 'SQS: point-to-point queue (pull); SNS: pub/sub fan-out (push). Often used together.', 'technical'),
    ('Amazon', 'Software Engineer', 'Explain Amazon DynamoDB\'s partition key design.', 'Choose high-cardinality keys to distribute data evenly and avoid hot partitions.', 'technical'),
    ('Amazon', 'Software Engineer', 'Design an e-commerce order management system.', 'Discuss services: order, inventory, payment, notification. Event-driven with SQS/SNS. Idempotent retries.', 'technical'),
    ('Amazon', 'Software Engineer', 'How do you ensure microservices are resilient?', 'Circuit breakers, retries with exponential backoff, bulkheads, health checks, dead-letter queues.', 'technical'),
    ('Amazon', 'Software Engineer', 'Tell me about a time you delivered results under tight deadlines.', 'Amazon LP: Deliver Results — give a concrete example with measurable outcome.', 'behavioral'),
    ('Amazon', 'Software Engineer', 'Describe a time you took ownership of a problem that wasn\'t yours.', 'Amazon LP: Ownership — show initiative and accountability.', 'behavioral'),
    ('Amazon', 'Data Analyst', 'How would you build a churn prediction model for Prime subscribers?', 'Feature engineering (usage, tenure, payment), logistic regression/GBM, evaluate with AUC-ROC, deploy with SageMaker.', 'technical'),
    ('Amazon', 'Data Analyst', 'What metrics would you track for Amazon\'s recommendation engine?', 'CTR, conversion rate, revenue per recommendation, diversity, and coverage.', 'technical'),
    ('Amazon', 'Machine Learning Engineer', 'Explain how collaborative filtering works.', 'User-user or item-item similarity, or matrix factorisation (SVD/ALS) to predict ratings.', 'technical'),
    ('Amazon', 'Machine Learning Engineer', 'How do you handle cold-start in recommendation systems?', 'Content-based fallback, popularity-based defaults, onboarding questionnaire, or hybrid approach.', 'technical'),
    ('Amazon', 'Product Manager', 'Tell me about a time you used data to change a product decision.', 'Show data gathering, analysis, insight, and how it influenced the roadmap.', 'behavioral'),

    # ── Microsoft ────────────────────────────────────────────────────────────
    ('Microsoft', 'Software Engineer', 'What is the difference between abstract classes and interfaces in C#?', 'Abstract classes can have implementation and state; interfaces define contracts only (pre-C#8). C#8+ interfaces can have default methods.', 'technical'),
    ('Microsoft', 'Software Engineer', 'Explain SOLID principles.', 'Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.', 'technical'),
    ('Microsoft', 'Software Engineer', 'How does Azure Blob Storage differ from Azure Table Storage?', 'Blob: unstructured binary/text data (files, images); Table: NoSQL key-value structured data.', 'technical'),
    ('Microsoft', 'Software Engineer', 'Design a distributed cache system.', 'Consistent hashing for node assignment, LRU eviction, replication for fault tolerance, TTL for expiry.', 'technical'),
    ('Microsoft', 'Software Engineer', 'Tell me about a time you mentored a colleague.', 'Show empathy, knowledge transfer, and measurable improvement in their performance.', 'behavioral'),
    ('Microsoft', 'Data Scientist', 'How do you evaluate a classification model?', 'Accuracy, precision, recall, F1, AUC-ROC — choose based on class imbalance and business cost of FP vs FN.', 'technical'),
    ('Microsoft', 'Data Scientist', 'What is the curse of dimensionality?', 'As dimensions increase, data becomes sparse and distance metrics lose meaning. Mitigate with PCA, feature selection.', 'technical'),
    ('Microsoft', 'Frontend Developer', 'What is the Virtual DOM in React?', 'An in-memory representation of the real DOM. React diffs Virtual DOM trees and batches minimal real DOM updates.', 'technical'),
    ('Microsoft', 'Frontend Developer', 'Explain CSS specificity.', 'Inline > ID > class/attribute/pseudo-class > element. Calculated as a 4-part score (a, b, c, d).', 'technical'),
    ('Microsoft', 'Product Manager', 'How would you improve Microsoft Teams for remote teams?', 'Identify pain points (async communication, focus time), propose features, validate with user research.', 'situational'),

    # ── Meta (Facebook) ──────────────────────────────────────────────────────
    ('Meta', 'Software Engineer', 'How does Facebook\'s News Feed ranking work at a high level?', 'Candidate generation → scoring (ML model on engagement signals) → filtering (diversity, integrity) → ranking.', 'technical'),
    ('Meta', 'Software Engineer', 'Design Instagram\'s story feature at scale.', 'Upload → media processing pipeline → CDN distribution, ephemeral storage (TTL 24h), view tracking with HyperLogLog.', 'technical'),
    ('Meta', 'Software Engineer', 'What is the difference between optimistic and pessimistic locking?', 'Optimistic: assume no conflict, check at commit (versioning); Pessimistic: lock early, block concurrent access.', 'technical'),
    ('Meta', 'Software Engineer', 'Tell me about a time you moved fast and broke something — and fixed it.', 'Show bias to action, ownership of the mistake, and systematic fix.', 'behavioral'),
    ('Meta', 'Data Scientist', 'How would you measure the impact of a new Facebook feature?', 'Define north-star and secondary metrics, run A/B test, check for network effects and novelty bias.', 'technical'),
    ('Meta', 'Data Scientist', 'What is a network effect and how do you model it?', 'Value increases with more users. Model with graph features (degree, clustering coefficient) or causal inference.', 'technical'),
    ('Meta', 'Machine Learning Engineer', 'Explain how Meta\'s content moderation uses ML.', 'Multi-modal classifiers (text + image + video), active learning, human-in-the-loop review, adversarial robustness.', 'technical'),
    ('Meta', 'Machine Learning Engineer', 'What is the difference between online and batch learning?', 'Online: updates model incrementally per sample (low latency); Batch: trains on full dataset periodically.', 'technical'),
    ('Meta', 'Frontend Developer', 'What is reconciliation in React?', 'React\'s diffing algorithm compares old and new Virtual DOM trees to determine the minimal set of actual DOM changes.', 'technical'),

    # ── Apple ────────────────────────────────────────────────────────────────
    ('Apple', 'iOS Developer', 'What is the difference between strong, weak, and unowned references in Swift?', 'Strong: retain cycle risk; Weak: optional, zeroed on dealloc; Unowned: non-optional, not zeroed — use when lifetime is guaranteed.', 'technical'),
    ('Apple', 'iOS Developer', 'Explain the iOS app lifecycle.', 'Not Running → Inactive → Active → Background → Suspended. AppDelegate/SceneDelegate manage transitions.', 'technical'),
    ('Apple', 'iOS Developer', 'What is Grand Central Dispatch (GCD)?', 'Apple\'s concurrency framework — dispatches tasks to serial or concurrent queues, avoiding thread management overhead.', 'technical'),
    ('Apple', 'iOS Developer', 'How do you optimise battery usage in an iOS app?', 'Reduce background work, batch network requests, use efficient APIs (Core Location significant-change), profile with Instruments.', 'technical'),
    ('Apple', 'Software Engineer', 'Describe a time you pushed back on a requirement that wasn\'t technically feasible.', 'Show clear communication, data-backed reasoning, and constructive alternative proposal.', 'behavioral'),
    ('Apple', 'Software Engineer', 'How would you design the Siri voice assistant pipeline?', 'ASR → NLU → Dialog Manager → NLG → TTS. Discuss latency, privacy (on-device ML), and personalisation.', 'technical'),
    ('Apple', 'Data Scientist', 'How does on-device ML benefit Apple\'s users?', 'Privacy (data stays on device), low latency, offline support. Challenges: model size, compute constraints.', 'technical'),

    # ── Netflix ──────────────────────────────────────────────────────────────
    ('Netflix', 'Software Engineer', 'How does Netflix handle video streaming at scale?', 'Adaptive bitrate streaming (MPEG-DASH/HLS), global CDN (Open Connect), pre-positioned content caches near ISPs.', 'technical'),
    ('Netflix', 'Software Engineer', 'Explain Netflix\'s chaos engineering philosophy.', 'Chaos Monkey randomly terminates instances to ensure systems are resilient and recovery is automated.', 'technical'),
    ('Netflix', 'Software Engineer', 'Design a notification system for Netflix (email, push, SMS).', 'Event-driven with Kafka, provider-agnostic notification service, retry queue, user preference store, rate limiting.', 'technical'),
    ('Netflix', 'Data Scientist', 'How does Netflix\'s recommendation algorithm work?', 'Collaborative filtering + content-based features + contextual signals (time, device, history), trained offline, served real-time.', 'technical'),
    ('Netflix', 'Data Scientist', 'How would you measure the success of a new recommendation model?', 'Offline: NDCG, precision@K; Online: A/B test on play rate, watch time, retention, cancellation rate.', 'technical'),
    ('Netflix', 'Machine Learning Engineer', 'What is two-tower architecture in recommendation systems?', 'Separate encoders for users and items → dot-product similarity → ANN retrieval. Efficient for large-scale retrieval.', 'technical'),
    ('Netflix', 'Product Manager', 'How would you decide which countries to expand Netflix into next?', 'Market size, internet penetration, content licensing costs, competitive landscape, payment infrastructure.', 'situational'),

    # ── Uber ─────────────────────────────────────────────────────────────────
    ('Uber', 'Software Engineer', 'How does Uber match riders to drivers in real time?', 'Geospatial indexing (H3/S2), supply-demand balancing, minimise ETA, consider surge pricing zones.', 'technical'),
    ('Uber', 'Software Engineer', 'Design the Uber surge pricing system.', 'Monitor supply/demand ratio by geohash, compute multiplier, notify drivers/riders, decay when balance restores.', 'technical'),
    ('Uber', 'Software Engineer', 'How do you ensure data consistency in a ride-sharing distributed system?', 'Saga pattern for distributed transactions, idempotent APIs, eventual consistency with reconciliation jobs.', 'technical'),
    ('Uber', 'Data Scientist', 'How would you reduce rider cancellations?', 'Identify cancellation triggers (ETA, driver rating, price), build predictive model, personalise matching to reduce cancellations.', 'technical'),
    ('Uber', 'Data Scientist', 'Explain Uber\'s dynamic pricing model.', 'Supply-demand ratio → pricing multiplier via regression/ML, constrained by regulatory caps and user tolerance.', 'technical'),
    ('Uber', 'Machine Learning Engineer', 'How would you build an ETA prediction model?', 'Features: historical trip times, real-time traffic, route, time of day. Model: gradient boosting or LSTM for sequences.', 'technical'),
    ('Uber', 'Software Engineer', 'Tell me about a time you improved system reliability.', 'Give concrete metrics: uptime%, incident reduction, MTTR improvement.', 'behavioral'),

    # ── Flipkart ─────────────────────────────────────────────────────────────
    ('Flipkart', 'Software Engineer', 'How would you design Flipkart\'s flash sale system?', 'Pre-warm caches, token-based queue to throttle requests, atomic inventory decrement in Redis, async order processing.', 'technical'),
    ('Flipkart', 'Software Engineer', 'Explain the CAP theorem with a real example.', 'A distributed system can guarantee only 2 of: Consistency, Availability, Partition tolerance. e.g., DynamoDB is AP.', 'technical'),
    ('Flipkart', 'Software Engineer', 'Design a product search engine for Flipkart.', 'Elasticsearch with inverted index, faceted filters, typo tolerance, ranking by relevance + sales + reviews.', 'technical'),
    ('Flipkart', 'Data Analyst', 'How would you analyse a sudden drop in Flipkart\'s conversion rate?', 'Check date/time, segment by device/category/region, investigate funnel drop-off, correlate with releases or external events.', 'situational'),
    ('Flipkart', 'Data Analyst', 'What SQL query would you use to find the top 5 selling products per category?', 'Use ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) and filter WHERE rank <= 5.', 'technical'),
    ('Flipkart', 'Machine Learning Engineer', 'How would you build a fraud detection system for Flipkart payments?', 'Features: velocity, location, device fingerprint, amount. Model: Isolation Forest/GBM. Real-time scoring with <100ms SLA.', 'technical'),
    ('Flipkart', 'Product Manager', 'How would you improve the Flipkart seller onboarding experience?', 'Map current journey, identify drop-off points, propose guided wizard, faster catalogue upload, transparent fee structure.', 'situational'),

    # ── TCS (Tata Consultancy Services) ─────────────────────────────────────
    ('TCS', 'Software Engineer', 'What is the difference between TCP and UDP?', 'TCP: connection-oriented, reliable, ordered (HTTP, FTP). UDP: connectionless, faster, no guarantee (video streaming, DNS).', 'technical'),
    ('TCS', 'Software Engineer', 'Explain the MVC design pattern.', 'Model (data/logic), View (UI), Controller (intermediary). Separates concerns for maintainability.', 'technical'),
    ('TCS', 'Software Engineer', 'What are the ACID properties in databases?', 'Atomicity, Consistency, Isolation, Durability — ensure reliable transactions.', 'technical'),
    ('TCS', 'Software Engineer', 'What is polymorphism in OOP?', 'One interface, multiple implementations. Compile-time (method overloading) and runtime (method overriding).', 'technical'),
    ('TCS', 'Software Engineer', 'Tell me about yourself and why you want to join TCS.', 'Structured intro: education, skills, projects, and alignment with TCS\'s scale and learning culture.', 'behavioral'),
    ('TCS', 'Software Engineer', 'Where do you see yourself in 3 years at TCS?', 'Show ambition: skill growth, taking on larger projects, potentially leading a team.', 'behavioral'),
    ('TCS', 'Data Analyst', 'What is the difference between OLTP and OLAP?', 'OLTP: transactional, row-oriented, low-latency writes. OLAP: analytical, column-oriented, complex reads.', 'technical'),
    ('TCS', 'Data Analyst', 'How do you perform root cause analysis on a data quality issue?', '5 Whys or fishbone diagram — trace back through pipeline stages to find the source.', 'situational'),

    # ── Infosys ──────────────────────────────────────────────────────────────
    ('Infosys', 'Software Engineer', 'What is dependency injection and why is it useful?', 'Pass dependencies from outside rather than creating them internally. Improves testability and decoupling.', 'technical'),
    ('Infosys', 'Software Engineer', 'Explain the Singleton design pattern.', 'Ensures only one instance of a class exists. Use lazy initialisation and double-checked locking for thread safety.', 'technical'),
    ('Infosys', 'Software Engineer', 'What is REST vs SOAP?', 'REST: lightweight, JSON/HTTP, stateless. SOAP: protocol, XML, WS-Security, stricter contract.', 'technical'),
    ('Infosys', 'Software Engineer', 'Describe a time you handled multiple projects simultaneously.', 'Show time management, prioritisation, communication with stakeholders, and outcomes.', 'behavioral'),
    ('Infosys', 'Data Analyst', 'What is the difference between GROUP BY and HAVING?', 'GROUP BY aggregates rows; HAVING filters on aggregated results (like WHERE but post-aggregation).', 'technical'),
    ('Infosys', 'Data Analyst', 'How would you design a dashboard for a client\'s sales data?', 'Understand KPIs, choose right chart types, build in Tableau/Power BI, schedule refreshes, share with stakeholders.', 'situational'),

    # ── Wipro ────────────────────────────────────────────────────────────────
    ('Wipro', 'Software Engineer', 'What is the difference between stack and heap memory?', 'Stack: function call frames, automatic allocation, LIFO. Heap: dynamic allocation, manual or GC managed, larger but slower.', 'technical'),
    ('Wipro', 'Software Engineer', 'Explain normalisation in databases up to 3NF.', '1NF: atomic values; 2NF: no partial dependency on composite key; 3NF: no transitive dependency.', 'technical'),
    ('Wipro', 'Software Engineer', 'What is the difference between an interface and an abstract class in Java?', 'Interface: pure contract, multiple inheritance; Abstract class: partial implementation, single inheritance.', 'technical'),
    ('Wipro', 'Software Engineer', 'Tell me about a time you received critical feedback.', 'Show openness, specific actions taken to improve, and positive result.', 'behavioral'),
    ('Wipro', 'Data Analyst', 'What is data warehousing?', 'Centralised repository of integrated data from multiple sources, optimised for reporting and analytics (star/snowflake schema).', 'technical'),
    ('Wipro', 'Data Analyst', 'How do you handle duplicate records in a dataset?', 'Identify with COUNT + GROUP BY or DISTINCT; deduplicate using ROW_NUMBER() or pandas drop_duplicates(); document the rule.', 'technical'),
]


class Command(BaseCommand):
    help = 'Seed pre-loaded company interview questions into CompanyQuestion model'

    def handle(self, *args, **options):
        created_count = 0
        skipped_count = 0

        for company, role, question, hints, category in COMPANY_QUESTIONS:
            _, created = CompanyQuestion.objects.get_or_create(
                company_name=company,
                question=question,
                defaults={
                    'job_role': role,
                    'answer_hints': hints,
                    'category': category,
                    'submitted_by': None,   # marks as pre-loaded, not user-submitted
                }
            )
            if created:
                created_count += 1
            else:
                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Company questions seeded successfully!'
        ))
        self.stdout.write(f'  Created : {created_count}')
        self.stdout.write(f'  Skipped (already exist): {skipped_count}')
        self.stdout.write(f'  Total in DB: {CompanyQuestion.objects.count()}')
