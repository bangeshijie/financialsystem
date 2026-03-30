
# 雪花算法


import time


def _next_millis(last_timestamp):
    """等待直到下一毫秒"""
    timestamp = int(time.time() * 1000)
    while timestamp <= last_timestamp:
        time.sleep(0.001)  # 休眠 1ms
        timestamp = int(time.time() * 1000)
    return timestamp


class SnowflakeIdGenerator:
    """
    简易版雪花算法实现
    结构: 1位符号 + 41位时间戳 + 5位数据中心ID + 5位机器ID + 12位序列号
    """

    def __init__(self, worker_id=1, datacenter_id=1):
        # 起始时间戳 (毫秒)，这里设为 2024-01-01 00:00:00
        # 你可以根据需要修改这个起始时间
        self.start_timestamp = 1704067200000

        # 位数分配
        self.worker_id_bits = 5
        self.datacenter_id_bits = 5
        self.sequence_bits = 12

        # 最大值计算
        self.max_worker_id = -1 ^ (-1 << self.worker_id_bits)
        self.max_datacenter_id = -1 ^ (-1 << self.datacenter_id_bits)
        self.sequence_mask = -1 ^ (-1 << self.sequence_bits)

        # 移位计算
        self.worker_id_shift = self.sequence_bits
        self.datacenter_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_left_shift = self.sequence_bits + self.worker_id_bits + self.datacenter_id_bits

        # 校验 ID 范围
        if worker_id > self.max_worker_id or worker_id < 0:
            raise ValueError(f"worker_id 必须在 0 到 {self.max_worker_id} 之间")
        if datacenter_id > self.max_datacenter_id or datacenter_id < 0:
            raise ValueError(f"datacenter_id 必须在 0 到 {self.max_datacenter_id} 之间")

        self.worker_id = worker_id
        self.datacenter_id = datacenter_id
        self.last_timestamp = -1
        self.sequence = 0

    def next_id(self):
        """生成下一个 ID"""
        timestamp = int(time.time() * 1000)

        # 处理时钟回拨
        if timestamp < self.last_timestamp:
            raise Exception(f"时钟回拨！检测到时间倒退，拒绝生成ID。上次时间：{self.last_timestamp}, 当前时间：{timestamp}")

        if timestamp == self.last_timestamp:
            # 同一毫秒内，序列号自增
            self.sequence = (self.sequence + 1) & self.sequence_mask
            if self.sequence == 0:
                # 序列号用完，等待下一毫秒
                timestamp = _next_millis(self.last_timestamp)
        else:
            # 不同毫秒，序列号归零
            self.sequence = 0

        self.last_timestamp = timestamp

        # 位运算组合最终 ID
        return ((timestamp - self.start_timestamp) << self.timestamp_left_shift) | \
            (self.datacenter_id << self.datacenter_id_shift) | \
            (self.worker_id << self.worker_id_shift) | \
            self.sequence


