# Verve Code Test

## Introduction

Welcome to the Verve code test. The test is broken into two parts

* Code Review
* Implementation of a new recommendation system

You are free to tackle the sections in any order. Please take as much or as little time
as you need in order to complete the test to your satisfaction. We recommend that test
should take a couple of hours (2-3) rather than days. All we ask is that you
let us know, truthfully, how much time you spent on the test. There is no right or wrong
amount of time, this info will simply help us with context when reviewing the results.

Imagine that someone in your sprint team was working on a story and just went
off sick and left this story on your lap with his few notes in the code. Take a
look at the existing code and provide an honest code review (in the way you'd normally
do when you'd be providing feedback on a Pull Request of your teammate) and then work
to finish off as much as you can do before sending it all back to us.

What we are looking for from you is:

* Code review of the Python code
* A working recommendation system in Python
* … along with some notes on possible refinements

## Pre-Requisites

Before starting this code test you should ensure that you have the
following environment setup.

 * Python 3.6

### Required dependencies

To install Python dependencies, run the following command:

```sh
make install
```

This script will create a Python virtualenv and install requirements in it using pip.

### Additional dependencies

To give you a working system you can install Docker, though it's not required
to complete the test:

 * Docker Environment (https://www.docker.com/)

The running system uses an AMQP Broker to relay messages from a little Python
helper service. We tested this with rabbitmq which can be quickly deployed locally
using the `rabbitmq:latest` docker image:

```sh
make rabbit
```

## Story Specification

The new Python RewardsEngine will receive `sale` messages in the following format:

```json
{"type": "sale", "item_id": 7, "cost": "3.35", "currency": "GBP", "user_id": 987654}
```

Users are given points for their purchases based on a simple algorithm
already implemented in the Rewards Engine but you'll need a simple way
to store the number of points the user has accumulated. This new system
will make `reward-recommendation`s based on the current total of points
the user has. Currently there are only a few types of rewards which are
detailed here:

```json
{
  "rewards": [
    {"name": "General Ticket", "points": 100, "max_per_user": 5},
    {"name": "VIP Ticket", "points": 1000, "max_per_user": 1},
    {"name": "Weekend Ticket", "points": 250, "max_per_user": 2},
    {"name": "Free Drink Voucher", "points": 50, "max_per_user": 10},
    {"name": "Free Limo to event", "points": 5000, "max_per_user": 1}
  ]
}
```

What we need you to do is to return a suggested list of rewards that
the user can buy with their points. So for example:

- if the `sale`s for a user gives them a total of 600 points you could suggest a
basket with 2x 'Weekend Ticket's and a 'General Ticket'.

How you make the selection is up to you. Just provide a list of rewards that the
user can buy up to their current point total.

Be mindful that some rewards can only be bought by a user specific number of times.
This is defined in the rewards dictionary as well.

This list can be sent back via the Queue Service using the JSON format:

```json
{"type":"rewards-recommendation","rewards":[...]}
```

## Environment

To run current test suite, enter this command:

```sh
make test
```

To generate sales data for testing, you can run SalesService in this way:

```sh
make sales
```

To use and test RewardsService, run this:

```sh
make rewards
```
