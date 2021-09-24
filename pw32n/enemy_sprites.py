import arcade

from pw32n import sprite_images


class EnemySprite(arcade.Sprite):
    def __init__(self, sprite_image: sprite_images.SpriteImage) -> None:
        super().__init__(sprite_image.filename, sprite_image.scaling)
        self.sprite_image = sprite_image
