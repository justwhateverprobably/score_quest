import pygame
import sys
import random
from enum import Enum
import json
import os

#Initialize pygame
pygame.init()
pygame.mixer.init()

#Create a display surface, and set caption
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
FPS = 60
pixel_font = pygame.font.Font('pixel_font.ttf', 32)
clock = pygame.time.Clock()
display = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("")
pygame.mixer.music.load('music.mp3')
sfx = pygame.mixer.Sound('click.wav')

class CircleElements(Enum):
    display = 1
    color = 2
    center = 3
    radius = 4
    width = 5

class Game:
    # ==========
    # INITIALIZE
    # ==========
    def __init__(self):
        self.save_path = 'cache.json'
        pygame.mixer.music.play(loops=-1)
        self.elements = CircleElements
        self.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2)
        self.default_speed_index = -1
        self.speed_index = self.default_speed_index # starts at 0, bc we add 1 when rand_speed called, accounts for 0 based indexing
        
        # player stats    
        self.player_radius = 20
        self.player_color = (252, 242, 89)

        # enemy stats
        self.enemy_radius_default = 500
        self.current_enemy_radius = self.enemy_radius_default
        self.enemy_color = (197, 23, 46)
        self.speed_increment = 0.1
        self.enemy_speed = self.update_speed()
        self.enemy_width = 30

        self.score = 0
        self.high_score = self.load(self.save_path)

    # ==========
    # HELPER FUNCTIONS
    # ==========
    def update_speed(self):
        self.speeds = [[0, 1, 2, 3, 4, 5, 6, 7],[3, 4, 5, 6, 7, 8, 9, 10, 11]] # [0] is min vals, [1] is max vals, they increment
        self.speed_index += 1 if self.speed_index < min(len(self.speeds[0]), len(self.speeds[1])) - 1 else 0 # add 1 to index if it's less than the max index of the shortest array (-1 bc 1 vs 0 based indexing with len and array)
        print(self.speed_index)
        return random.randint(self.speeds[0][self.speed_index], self.speeds[1][self.speed_index])

    def draw_score(self):
        self.score_text = pixel_font.render(f"Score: {self.score}", True, (133, 25, 60))
        self.score_text_rect = self.score_text.get_rect()
        self.score_text_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 200)
        display.blit(self.score_text, self.score_text_rect)

        self.high_score_text = pixel_font.render(f"High Score: {self.high_score}", True, (133, 25, 60))
        self.high_score_rect = self.high_score_text.get_rect()
        self.high_score_rect.center = (WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 250)
        display.blit(self.high_score_text, self.high_score_rect)


    def draw_player(self):
        pygame.draw.circle(self.player[self.elements.display], self.player[self.elements.color], self.player[self.elements.center], self.player[self.elements.radius])        

    def draw_enemy(self):
        pygame.draw.circle(self.enemy[self.elements.display], self.enemy[self.elements.color], self.enemy[self.elements.center], self.enemy[self.elements.radius], self.enemy[self.elements.width])

    def save(self, path):
        data = {'high_score': self.high_score}
        with open(path, 'w') as f:
            json.dump(data, f)
        
    def load(self, path):
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
            except (json.JSONDecodeError, ValueError, TypeError):
                return 0
        return 0

    # ==========
    # UPDATE
    # ==========
    def update(self):
        # update enemy state
        self.enemy_speed += self.speed_increment
        self.current_enemy_radius -= self.enemy_speed

        # refresh player and enemies with new state
        self.player = {self.elements.display: display, self.elements.color: self.player_color, self.elements.center: self.center, self.elements.radius: self.player_radius}
        self.enemy = {self.elements.display: display, self.elements.color: self.enemy_color, self.elements.center: self.center, self.elements.radius: self.current_enemy_radius, self.elements.width: self.enemy_width}
        
        # update high score
        if self.score > self.high_score:
            self.high_score = self.score
            self.save('cache.json')

        # check lose condition
        if self.current_enemy_radius + self.enemy_width < self.player_radius:
            self.score = 0
            self.speed_index = self.default_speed_index
            self.enemy_speed = self.update_speed()
            self.current_enemy_radius = self.enemy_radius_default
            

# ==========
# MAIN LOOP
# ==========
def main():
    running = True
    game = Game()
    game.update()
    bg_color = (74, 16, 42)
    elements = CircleElements

    while running:
            # check for events
            for event in pygame.event.get():
                # check to quit game
                if event.type == pygame.QUIT:
                    game.save(game.save_path)
                    running = False
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_SPACE] and game.enemy[elements.radius] > game.player[elements.radius]:
                        # sfx
                        sfx.play()
                        # calculate score
                        distance = game.enemy[elements.radius] - game.player[elements.radius]
                        epsilon = 0 # avoid division by 0 if player get perfect timing
                        scale = 10 # adjusts curve steepness, bigger scale, gentler curve
                        multiplier = 1000

                        score = 1 / (((distance / scale) + epsilon) ** 2) # score increases inversely to dist and exponentially (e.g. dist = 100, score = .01, but 10 it would be 0.1)
                        game.score += int(score * multiplier)

                        # reset enemy
                        game.current_enemy_radius = game.enemy_radius_default
                        game.enemy_speed = game.update_speed()


            # update events
            game.update()

            # fill screen with bg
            display.fill((bg_color))

            # draw elements to screen
            game.draw_enemy()
            game.draw_player()
            game.draw_score()

            # update screen
            pygame.display.flip()
            clock.tick(FPS)

if __name__ == "__main__":
    main()