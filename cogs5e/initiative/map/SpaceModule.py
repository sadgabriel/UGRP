"""
SpaceModule.py
This is class for the Connection to the Text Part.
"""

from cogs5e.initiative.map import Map
from cogs5e.initiative.map import IDContainer

# Not needed for now.
# import SpaceAIModule


class SpaceModule:
    def __init__(self) -> None:
        self.map = Map.Map()

        # Not needed for now.
        # self.aimodule = SpaceAIModule.SpaceAIModule("given text")

        self.idcontainer = IDContainer.IDContainer()

        return

    def is_attackable(self, id1: int, id2: int) -> bool:
        """
        Check whether is id1 able to attack id2.
        considering a range not only a movepoint.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object

        Returns:
            True/False
        """

        # movement_point: movement point of id1
        # shooting_range: range of attack
        temp_data = self.get_data(id1)
        movement_point = temp_data["movement point"]
        shooting_range = temp_data["shooting range"]

        return self.map.is_movable_with_range(id1, id2, movement_point, shooting_range)

    def attack_move(self, id1, id2) -> None:
        """
        This is just Attack move function.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
        """

        # movement_point: movement point of id1
        # shooting_range: range of attack
        temp_data = self.get_data(id1)
        movement_point = temp_data["movement point"]
        shooting_range = temp_data["shooting range"]

        self.map.attack_move(id1, id2, movement_point, shooting_range)

        return

    def set_obj(self, name: str, id: int) -> None:

        self.idcontainer[name] = id
        self.map.put(id)

        return

    def get_obj(self, name: str) -> int:

        return self.idcontainer[name]

    def set_data(self, id: int, data: tuple) -> None:
        """
        args
            data: tuple(hp: int, movement_point: int, shooting_range: int)
        """

        self.idcontainer.set_data(id, data)

        return

    def get_data(self, id: int) -> dict:

        return self.idcontainer.get_data(id).data

    def print_map(self) -> None:

        self.map.print_map()

        return

    def random_place(self) -> None:

        self.map.random_place()

        return


if __name__ == "__main__":

    spacemodule = SpaceModule()

    spacemodule.set_obj("dog", 1)
    spacemodule.set_data(1, (10, 2, 1))
    spacemodule.set_obj("cat", 2)
    spacemodule.set_data(2, (6, 3, 3))

    spacemodule.random_place()

    spacemodule.print_map()

    print("is dog(id:1) able to attack cat(id:2)?:", spacemodule.is_attackable(1, 2))

    spacemodule.attack_move(1, 2)
    spacemodule.print_map()
