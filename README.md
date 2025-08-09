# exam-platform

A FastAPI application to implement an exam taking platform

## Indexing Strategies

For submissions, we'll be creating the following indexes:

- test_id + user_id + question_id - To avoid duplicate submission
- test_id + user_id - For user scores retrieval
- test_id + subject - For subjectwise analysis
- test_id + score - For leaderboards
