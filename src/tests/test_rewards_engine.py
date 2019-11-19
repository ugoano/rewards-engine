import unittest
import pytest

from ..rewards.rewards_engine import RewardsEngine
from ..queue.queue_service import QueueService


def test_points_from_purchase():
    rewards = RewardsEngine(QueueService(3, 'rewards', 'rewards'), None)
    assert rewards.points_from_purchase(10) == 100


@pytest.mark.parametrize(
    "points,expected",
    [
        (
            7000,
            [
                {"name": "Free Limo to event", "points": 5000, "max_per_user": 1},
                {"name": "VIP Ticket", "points": 1000, "max_per_user": 1},
                {"name": "Weekend Ticket", "points": 250, "max_per_user": 2},
                {"name": "General Ticket", "points": 100, "max_per_user": 5},
                {"name": "Free Drink Voucher", "points": 50, "max_per_user": 10},
            ],
        ),
        (
            4000,
            [
                {"name": "VIP Ticket", "points": 1000, "max_per_user": 1},
                {"name": "Weekend Ticket", "points": 250, "max_per_user": 2},
                {"name": "General Ticket", "points": 100, "max_per_user": 5},
                {"name": "Free Drink Voucher", "points": 50, "max_per_user": 10},
            ],
        ),
        (
            200,
            [
                {"name": "General Ticket", "points": 100, "max_per_user": 5},
                {"name": "Free Drink Voucher", "points": 50, "max_per_user": 10},
            ],
        )
    ]
)
def test_get_max_rewards_order_by_points(points, expected):
    rewards = RewardsEngine(QueueService(3, 'rewards', 'rewards'), None)
    assert list(rewards.get_max_rewards_order_by_points(points)) == expected


@pytest.mark.parametrize(
    "points,purchased_rewards,expected",
    [
        (
            7000, {"VIP Ticket": 1},
            [
                {"name": "Free Limo to event", "points": 5000, "count": 1},
                {"name": "Weekend Ticket", "points": 250, "count": 2},
                {"name": "General Ticket", "points": 100, "count": 5},
                {"name": "Free Drink Voucher", "points": 50, "count": 10},
            ],
        ),
        (
            4000, {},
            [
                {"name": "VIP Ticket", "points": 1000, "count": 1},
                {"name": "Weekend Ticket", "points": 250, "count": 2},
                {"name": "General Ticket", "points": 100, "count": 5},
                {"name": "Free Drink Voucher", "points": 50, "count": 10},
            ],
        ),
        (
            200, {"Free Drink Voucher": 3},
            [
                {"name": "General Ticket", "points": 100, "count": 2},
            ],
        ),
        (
            200, {"General Ticket": 4, "Free Drink Voucher": 3},
            [
                {"name": "General Ticket", "points": 100, "count": 1},
                {"name": "Free Drink Voucher", "points": 50, "count": 2},
            ],
        )
    ]
)
def test_recommend_rewards(points, purchased_rewards, expected):
    rewards = RewardsEngine(QueueService(3, 'rewards', 'rewards'), None)
    assert rewards.recommend_rewards(points, purchased_rewards) == expected
