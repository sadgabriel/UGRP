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
    
    def is_attackable(self, id1: int, id2: int,movement_point: int, shooting_range: int) -> bool:
        """
        Check whether is id1 able to attack id2.
        considering a range not only a movepoint.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
            movement_point: movement point of id1
            shooting_range:range of attack(action)

        Returns:
            True/False
        """

        return self.map.is_movable_with_range(id1, id2, movement_point, shooting_range)
    
    def attack_move(self, id1: int, id2: int, movement_point: int, shooting_range: int) -> None:
        """
        This is just Attack move function.
        id1 will move toward id2 to attack id2.
        id1 stay max range.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
            movement_point: movement point of id1
            shooting_range:range of attack(action)
        """

        # movement_point: movement point of id1
        # shooting_range: range of attack 

        self.map.attack_move(id1, id2, movement_point, shooting_range)

        return

    def set_obj(self, name: str, id: int) -> None:

        self.idcontainer[name] = id
        self.map.put(id)

        return

    def get_obj(self, name: str) -> int:

        return self.idcontainer[name]
    
    def get_position(self, id: int) -> tuple:

        return self.map.tracer[id]
    
    def print_map(self) -> None:

        self.map.print_map()

        return

    def random_place(self) -> None:

        self.map.random_place()

        return


if __name__ == "__main__":

    spacemodule = SpaceModule()

    spacemodule.set_obj('dog', 1)
    spacemodule.set_obj('cat', 2)

    spacemodule.random_place()

    spacemodule.print_map()

    print("is dog(id:1) able to attack cat(id:2)?:", spacemodule.is_attackable(1, 2, 3, 4))

    spacemodule.attack_move(1, 2, 3, 4)
    spacemodule.print_map()
