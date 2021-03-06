"""Defines the monster renderer."""
import pygame

from engine.system import Message
from engine.ui.core.manager import Manager
from engine.ui.core.zone import Zone
import engine.ui.element as element

class MonsterManager(Manager):
    """Manager for the monster class"""

    def __init__(self, monster, x, y):
        super(MonsterManager, self).__init__()
        SCALE = 4 # TEMPORARY VARIABLE
        self.monster = monster
        self.highlight = False

        # Load monster neutral image
        try:
            raw_image = pygame.image.load( \
                monster.graphic["neutral"]).convert_alpha()
            raw_image = pygame.transform.scale(raw_image, \
                (raw_image.get_width()*SCALE, raw_image.get_height()*SCALE))
        except pygame.error:
            raw_image = pygame.Surface((70*SCALE, 20*SCALE))
            raw_image.fill((255, 255, 255))
            raw_image.blit(element.Text.draw(monster.name, 20, (0, 0, 0),
                           70*SCALE, element.Text.CENTER), (0, 10))

        # Create image element
        self.image_element = element.Image(raw_image,
            x-raw_image.get_width()//2, y-raw_image.get_height())
        self.renderables.append(self.image_element)

        # Store raw image
        self.neutral_image = raw_image

        # Create selection image
        selection_image = pygame.Surface(
            (self.neutral_image.get_width() + 10,
            self.neutral_image.get_height() + 85),
            pygame.SRCALPHA)
        selection_image.fill((0, 0, 0, 0))
        pygame.draw.rect(selection_image, (255, 0, 0),
            selection_image.get_rect(), 1)
        self.selection_element = element.Image(selection_image,
            x-raw_image.get_width()//2-5, y-raw_image.get_height()-80)

        # Load monster hover image
        try:
            raw_image = pygame.image.load( \
                monster.graphic["hover"]).convert_alpha()
        except pygame.error:
            raw_image = pygame.Surface((70, 20))
            raw_image.fill((255, 255, 0))
            raw_image.blit(element.Text.draw(monster.name, 20, (0, 0, 0),
                           70*SCALE, element.Text.CENTER), (0, 10))

        # Store hover image
        self.hover_image = pygame.transform.scale(raw_image,
            (raw_image.get_width()*SCALE, raw_image.get_height()*SCALE))

        # Create text element
        self.text_element = element.Text(monster.name.title(), 20, x,
            y-self.image_element.surface.get_height()-75)
        self.text_element.x = x - self.text_element.surface.get_width()//2
        self.renderables.append(self.text_element)

        # Store hovered and neutral text surfaces
        self.neutral_name = self.text_element.surface
        self.hover_name = element.Text.draw(monster.name.title(), 20,
            (255, 255, 0), None, element.Text.LEFT)

        # Create health and action bars
        self.health_bar = element.Bar(32*SCALE, 2*SCALE, (116, 154, 104),
            x-16*SCALE , y-self.neutral_image.get_height()-40)
        self.action_bar = element.Bar(32*SCALE, 2*SCALE, (212, 196, 148),
            x-16*SCALE, y-self.neutral_image.get_height()-25)
        health_missing = element.Bar(32*SCALE, 2*SCALE, (30, 30, 30),
            x-16*SCALE,  y-self.neutral_image.get_height()-40)
        action_missing = element.Bar(32*SCALE, 2*SCALE, (30, 30, 30),
            x-16*SCALE,  y-self.neutral_image.get_height()-25)
        self.renderables.append(health_missing)
        self.renderables.append(action_missing)
        self.renderables.append(self.health_bar)
        self.renderables.append(self.action_bar)

    def update(self, game):
        super().update(game)
        self.health_bar.percent = 100*self.monster.get_cur_health()/ \
            self.monster.get_stat("health")
        self.action_bar.percent = 100*self.monster.action/ \
            self.monster.get_stat("action")

    def on_click(self, game):
        if game.selected_player and game.selected_player.selected_move and \
                not self.monster.fallen:
            if game.selected_player.selected_move.is_valid_target(
                    game.selected_player.target+[self.monster],
                    game.party.players,
                    game.encounter):
                game.selected_player.target.append(self.monster)

    def render(self, surface, game):
        if self.monster.fallen:
            return
        if self.highlight:
            self.text_element.surface = self.hover_name
            self.image_element.surface = self.hover_image
        else:
            self.text_element.surface = self.neutral_name
            self.image_element.surface = self.neutral_image
        super().render(surface, game)
        # Render selection
        if game.selected_player:
            if self.monster in game.selected_player.target:
                self.selection_element.render(surface, game)

    def __hash__(self):
        """This object is hashed by its name"""
        return hash(self.monster.name)