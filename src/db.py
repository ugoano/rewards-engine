import os
import random

from tinydb import TinyDB, Query, where
from tinydb.operations import add


class DB:

    def __init__(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.db = TinyDB(os.path.join(dir_path, "tinydb.json"))

    def update_points(self, user_id, points):
        users = self.db.table("User")
        User = Query()
        result = users.update(add("points", points), User.user_id == user_id)
        if not result:
            random_purchased_rewards = random.choice([
                {"General Ticket": random.randint(1, 5)},
                {"Free Drink Voucher": random.randint(1, 10)},
                {},
                {"Weekend Ticket": random.randint(1, 2)},
                {},
            ])
            users.insert({
                "user_id": user_id, "points": points,
                "purchased_rewards": random_purchased_rewards
            })

    def get_user_details(self, user_id):
        users = self.db.table("User")
        try:
            return users.search(where("user_id") == user_id)[0]
        except IndexError:
            return None  # No user
