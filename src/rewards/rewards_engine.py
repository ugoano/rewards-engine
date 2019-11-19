import logging
import json


LOGGER = logging.getLogger(__name__)


class RewardsEngine(object):

    # Store this here for now till I think of how we should get this data in to the Engine.
    REWARDS = {
        "rewards": [
            {"name": "General Ticket", "points": 100, "max_per_user": 5},
            {"name": "VIP Ticket", "points": 1000, "max_per_user": 1},
            {"name": "Weekend Ticket", "points": 250, "max_per_user": 2},
            {"name": "Free Drink Voucher", "points": 50, "max_per_user": 10},
            {"name": "Free Limo to event", "points": 5000, "max_per_user": 1}
        ]
    }

    def __init__(self, queueService, db):
        self._queueService = queueService
        self._db = db

    def points_from_purchase(self, price):
        return price * 10

    def on_message(self, body):
        LOGGER.info('REWARDS ENGINE message %s', body)
        message = json.loads(body.decode('utf-8'))
        points = self.points_from_purchase(message["cost"])

        # add to the points for a user
        self._db.update_points(message["user_id"], points)
        LOGGER.info(f'Update {message["user_id"]} by POINTS {points}')

        # get points and current purchased rewards for the user (latter currently random)
        user = self._db.get_user_details(message["user_id"])

        # make recommendation
        recommendations = self.recommend_rewards(user["points"], user["purchased_rewards"])
        recommendation_json = {
            "type": "rewards-recommendation",
            "rewards": recommendations,
        }
        LOGGER.info(f'REWARDS ENGINE recommendations {recommendation_json}')

        self._queueService._channel.basic_publish(
            "rewards-recommendation",
            "rewards-recommendation",
            json.dumps(recommendation_json, ensure_ascii=False),
            self._queueService.DEFAULT_MESSAGE_PROPERTY
        )

    def recommend_rewards(self, points, purchased_rewards):
        """Calculate best deals based on allowed rewards, points available and rewards purchased."""
        recommendations = []
        rewards = self.get_max_rewards_order_by_points(points)
        for reward in rewards:
            # Calculate permitted number of this reward based on points and max_per_user
            num_of_reward_allowed = min(
                reward["max_per_user"] - purchased_rewards.get(reward["name"], 0),  # Should use reward id
                int(points/reward["points"])
            )

            if num_of_reward_allowed == 0:
                continue

            # Calculate remaining points
            points = points - (num_of_reward_allowed * reward["points"])

            recommendation = {
                "name": reward["name"],
                "points": reward["points"],
                "count": num_of_reward_allowed,
            }
            recommendations.append(recommendation)
        return recommendations


    def get_max_rewards_order_by_points(self, points, rewards=None):
        """Would be a database call to the rewards ordered by points."""
        if not rewards:
            rewards = self.REWARDS  # pretend db call
        return filter(
            lambda x: x["points"] <= points,
            sorted(rewards["rewards"], key=lambda r: r["points"], reverse=True),
        )

    def make_recommendation(self, total_points, purchased_items):
        """Recommend the highest value items."""
        rewards = self.get_rewards_order_by_points()
