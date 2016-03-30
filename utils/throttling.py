# coding=utf-8
import time
import redis


class TokenBucket(object):
    def __init__(self, fill_rate, capacity, last_capacity, last_timestamp):
        self.capacity = float(capacity)
        self._left_tokens = last_capacity
        self.fill_rate = float(fill_rate)
        self.timestamp = last_timestamp

    def consume(self, tokens=1):
        if tokens <= self.tokens:
            self._left_tokens -= tokens
            return True
        return False

    def expected_time(self, tokens=1):
        _tokens = self.tokens
        tokens = max(tokens, _tokens)
        return (tokens - _tokens) / self.fill_rate * 60

    @property
    def tokens(self):
        if self._left_tokens < self.capacity:
            now = time.time()
            delta = self.fill_rate * ((now - self.timestamp) / 60)
            self._left_tokens = min(self.capacity, self._left_tokens + delta)
            self.timestamp = now
        return self._left_tokens


class BucketController(object):
    def __init__(self, user_id, redis_conn, default_capacity):
        self.user_id = user_id
        self.default_capacity = default_capacity
        self.redis = redis_conn
        self.key = "bucket_" + str(self.user_id)

    @property
    def last_capacity(self):
        value = self.redis.hget(self.key, "last_capacity")
        if value is None:
            self.last_capacity = self.default_capacity
            return self.default_capacity
        return int(value)

    @last_capacity.setter
    def last_capacity(self, value):
        self.redis.hset(self.key, "last_capacity", value)

    @property
    def last_timestamp(self):
        value = self.redis.hget(self.key, "last_timestamp")
        if value is None:
            timestamp = int(time.time())
            self.last_timestamp = timestamp
            return timestamp
        return int(value)

    @last_timestamp.setter
    def last_timestamp(self, value):
        self.redis.hset(self.key, "last_timestamp", value)


"""
# token bucket 机制限制用户提交大量代码
# demo
success = failure = 0
current_user_id = 1
token_bucket_default_capacity = 50
token_bucket_fill_rate = 10


for i in range(5000):
    controller = BucketController(user_id=current_user_id,
                                  redis_conn=redis.Redis(),
                                  default_capacity=token_bucket_default_capacity)
    bucket = TokenBucket(fill_rate=token_bucket_fill_rate,
                         capacity=token_bucket_default_capacity,
                         last_capacity=controller.last_capacity,
                         last_timestamp=controller.last_timestamp)

    time.sleep(0.05)
    if bucket.consume():
        success += 1
        print i, ": Accepted"
        controller.last_capacity -= 1
    else:
        failure += 1
        print i, "Dropped, time left ", bucket.expected_time()
print success, failure
"""