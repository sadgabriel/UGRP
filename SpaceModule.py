"""
SpaceModule.py
This is class for the Connection to the Text Part.
"""

import Map

class SpaceModule:
    def __init__(self) -> None:
        self.map = Map.Map()

        return
    
    def is_attackable(self, id1, id2, movement_point, shooting_range):
        """
        A attackablility check that consider a range not only a movepoint.
        check whether is id1 able to attack id2.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
            movement_point: movement point of id1
            shooting_range: range of attack

        Returns:
            bool
        """

        return self.map.is_movable_with_range(id1, id2, movement_point, shooting_range)
    
    def attack_move(self, id1, id2, movement_point, shooting_range):
        """
        This is just Attack move function.

        Args:
            id1: subject or caster (attacker/mover)
            id2: object
            movement_point: movement point of id1
            shooting_range: range of attack

        Returns:
            None
        """

        self.map.attack_move(id1, id2, movement_point, shooting_range)

        return
    
    def get_data(self):

        return
