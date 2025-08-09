# exam-platform

A FastAPI application to implement an exam taking platform

## Indexing Strategies

For submissions, we'll be creating the following indexes:

- test_id + user_id + question_id - To avoid duplicate submission
- test_id + user_id - For user scores retrieval
- test_id + subject - For subjectwise analysis
- test_id + score - For leaderboards

## Ranking and Percentiles Calculations

For ranking, used Redis' zrevrank to cache the ranks and get the ranks faster for percentile calculations afterwards
Also used the TDigest data structure to store subject-wise percentiles (t-digest is useful for rank-based stats)

The flow works after a test ends, either through a scheduler or an API call to calculate and cache final scores and ranks
which then can be quickly read from the cache and even stored in a results collection if needed afterwards as and when needed for the user
