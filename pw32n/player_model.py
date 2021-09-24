class PlayerModel:
    MIN_STRENGTH = 1.0

    def __init__(self) -> None:
        self.strength = self.MIN_STRENGTH

    @property
    def strength(self) -> float:
        return self.__strength

    @strength.setter
    def strength(self, strength: float) -> None:
        self.__strength = max(strength, self.MIN_STRENGTH)
