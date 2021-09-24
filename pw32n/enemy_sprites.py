from typing import Any

import arcade

from pw32n import sprite_images, models


class EnemySprite(arcade.Sprite):
    def __init__(self, model: models.EnemyModel, *args: Any, **kargs: Any) -> None:
        super().__init__(*args, **kargs)
        self.model = model
