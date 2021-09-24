class Combatant:
    # Subclasses may want to override this.
    MIN_STRENGTH = 0.0

    def __init__(self) -> None:
        self.__strength = self.MIN_STRENGTH

    @property
    def strength(self) -> float:
        return self.__strength

    @strength.setter
    def strength(self, strength: float) -> None:
        self.__strength = max(strength, self.MIN_STRENGTH)

    @property
    def is_dead(self) -> bool:
        return self.strength == 0.0


class PlayerModel(Combatant):
    # Players can't die.
    MIN_STRENGTH = 1.0


class EnemyModel(Combatant):
    def __init__(self, strength: float) -> None:
        super().__init__()
        self.strength = strength
