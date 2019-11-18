import unittest

from ..rewards.rewards_engine import RewardsEngine
from ..queue.queue_service import QueueService


class TestRewardsEngine(unittest.TestCase):

    def test_points_from_purchase(self):
        rewards = RewardsEngine(QueueService(3, 'rewards', 'rewards'))
        self.assertEqual(rewards.points_from_purchase(10), 100)
