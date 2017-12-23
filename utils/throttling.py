import time


class TokenBucket:
    """
    注意：对于单个key的操作不是线程安全的
    """
    def __init__(self, key, capacity, fill_rate, default_capacity, redis_conn):
        """
        :param capacity: 最大容量
        :param fill_rate: 填充速度/每秒
        :param default_capacity: 初始容量
        :param redis_conn: redis connection
        """
        self._key = key
        self._capacity = capacity
        self._fill_rate = fill_rate
        self._default_capacity = default_capacity
        self._redis_conn = redis_conn

        self._last_capacity_key = "last_capacity"
        self._last_timestamp_key = "last_timestamp"

    def _init_key(self):
        self._last_capacity = self._default_capacity
        now = time.time()
        self._last_timestamp = now
        return self._default_capacity, now

    @property
    def _last_capacity(self):
        last_capacity = self._redis_conn.hget(self._key, self._last_capacity_key)
        if last_capacity is None:
            return self._init_key()[0]
        else:
            return float(last_capacity)

    @_last_capacity.setter
    def _last_capacity(self, value):
        self._redis_conn.hset(self._key, self._last_capacity_key, value)

    @property
    def _last_timestamp(self):
        return float(self._redis_conn.hget(self._key, self._last_timestamp_key))

    @_last_timestamp.setter
    def _last_timestamp(self, value):
        self._redis_conn.hset(self._key, self._last_timestamp_key, value)

    def _try_to_fill(self, now):
        delta = self._fill_rate * (now - self._last_timestamp)
        return min(self._last_capacity + delta, self._capacity)

    def consume(self, num=1):
        """
        消耗 num 个 token，返回是否成功
        :param num:
        :return: result: bool, wait_time: float
        """
        # print("capacity ", self.fill(time.time()))
        if self._last_capacity >= num:
            self._last_capacity -= num
            return True, 0
        else:
            now = time.time()
            cur_num = self._try_to_fill(now)
            if cur_num >= num:
                self._last_capacity = cur_num - num
                self._last_timestamp = now
                return True, 0
            else:
                return False, (num - cur_num) / self._fill_rate
