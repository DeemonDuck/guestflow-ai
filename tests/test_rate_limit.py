from fastapi.testclient import TestClient

import main

client = TestClient(main.app)


def test_feedback_endpoint_is_rate_limited():
    # Isolate from any other test's counter
    main.limiter.reset()
    try:
        statuses = [
            client.post("/feedback/RL", json={"rating": 5}).status_code
            for _ in range(32)
        ]
        # Limit is 30/minute: first 30 allowed, then 429
        assert statuses.count(200) == 30
        assert 429 in statuses
    finally:
        main.limiter.reset()
