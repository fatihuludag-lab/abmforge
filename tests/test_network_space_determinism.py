from __future__ import annotations

import os
import subprocess
import sys


def test_network_space_order_is_independent_of_python_hash_seed() -> None:
    script = """
import json

from abmforge import Agent, Model, NetworkSpace


class Person(Agent):
    pass


model = Model(seed=1)
agents = model.agents.create(Person, n=4)

space = NetworkSpace()
space.add_edge("center", "b")
space.add_edge("center", "a")
space.add_edge("center", "c")

space.place_agent(agents[0], "center")
space.place_agent(agents[1], "b")
space.place_agent(agents[2], "a")
space.place_agent(agents[3], "c")

print(
    json.dumps(
        {
            "nodes": space.neighbor_nodes("center"),
            "neighbors": [agent.unique_id for agent in space.neighbors(agents[0])],
        },
        sort_keys=True,
    )
)
"""

    outputs: list[str] = []

    for hash_seed in ["1", "2", "3", "4", "5"]:
        env = os.environ.copy()
        env["PYTHONHASHSEED"] = hash_seed

        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
            env=env,
        )
        outputs.append(completed.stdout.strip())

    assert outputs == [outputs[0]] * len(outputs)
    assert outputs[0] == '{"neighbors": [2, 3, 4], "nodes": ["b", "a", "c"]}'
