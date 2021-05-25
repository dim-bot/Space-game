import pygame
import os
import sys
import time
import random
from pygame.locals import *
from pygame import mixer

pygame.init()
pygame.font.init()


width, height = 800, 600
window = pygame.display.set_mode((width,height))
pygame.display.set_caption('SuperDuperAwesome SpaceGame')
main_font = pygame.font.SysFont('comicsans', 30)

enemy_ship1 = pygame.image.load(os.path.join("assets","ufo.png"))
enemy_ship2 = pygame.image.load(os.path.join("assets","ufoenemy.png"))
player_ship = pygame.image.load(os.path.join("assets","spaceship.png"))
bullet_player = pygame.image.load(os.path.join("assets","bullet.png"))
bullet_enemy = pygame.image.load(os.path.join("assets", "bulletEnemy.png"))
background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space.jpeg')),(width,height))

# background sounds
shotFired = mixer.Sound(os.path.join('assets', 'laser.wav'))
hitSound = mixer.Sound(os.path.join('assets', 'explosion.wav'))

mixer.music.load(os.path.join('assets','bg_music.wav'))
mixer.music.set_volume(0.5)
mixer.music.play(-1)

#rgb sets
blue = (0,0,255)
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)

clicked = False

class button():
	
	button_col = (0, 0, 255)
	hover_col = (75, 225, 255)
	click_col = (50, 150, 255)
	text_col = black
	buttonW = 100
	buttonH = 40
	
	def __init__(self, x, y, text):
		self.x = x
		self.y = y
		self.text = text

	def draw_button(self):
		global clicked
		action = False

		pos = pygame.mouse.get_pos()
		button_rect = Rect(self.x, self.y, self.buttonW, self.buttonH)

		if button_rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1:
				clicked = True
				pygame.draw.rect(window,self.click_col,button_rect)
			elif pygame.mouse.get_pressed()[0] == 0 and clicked == True:
				clicked = False
				action = True
			else:
				pygame.draw.rect(window, self.hover_col, button_rect)
		else:
			pygame.draw.rect(window, self.button_col, button_rect)

		text_img = main_font.render(self.text, True, self.text_col)
		text_len = text_img.get_width()
		window.blit(text_img, (self.x + int(self.buttonW / 2) - int(text_len / 2), self.y+13))
		return action

play_button = button(width/2-40, height/2+50, 'Play')
options_button = button(width/2-40, height/2+100, 'Options')
score_button = button(width/2-40, height/2+150, 'Scores')
quit_button = button(width/2-40, height/2+200, 'Quit')
back_button = button(width/2-40, height/2+200, 'Back')
credit_button = button(width/2-40, height/2+150, 'Credits')

class Bullet:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def moveB(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.velocity = 0
        self.shooting = False
        self.bullets = []
        self.cool_down_counter = 0
        

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    def move_bullets(self, vel, obj):
        self.cooldown()
        for bullet in self.bullets:
            bullet.moveB(vel)
            if bullet.off_screen(height):
                self.bullets.remove(bullet)
            elif bullet.collision(obj):
                hitSound.play()
                obj.health -= 10
                self.bullets.remove(bullet)


    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter  += 1

    def shoot(self):
        if self.cool_down_counter == 0 and self.shooting == True:
            shotFired.play()
            bullet = Bullet(self.x, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

# player class ingerets everything within class Ship
class Player(Ship):

    def __init__(self, x, y, health=100):
        # super() = use ships init method the things inside () are ones that will change
        super().__init__(x, y, health)
        self.ship_img = player_ship
        self.bullet_img = bullet_player
        self.shooting = True
        # pygame has mask that allows for pixel perfect collision detection instead of basic square thingy
        # tells us where pixels are and aren't for collision
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.moveB(vel)
            if bullet.off_screen(height):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collision(obj):
                        # removing obj, removes the list containing it's bullets
                        hitSound.play()
                        objs.remove(obj)
                        global game_score
                        game_score += 10
                        if bullet in self.bullets:
                            self.bullets.remove(bullet)
    

    def draw(self,window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

class Enemy(Ship):
    COLOR_MAP = {
        "red": (enemy_ship1, bullet_enemy,1,True),
        "green": (enemy_ship2, bullet_enemy,3,False)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img, self.velocity, self.shooting = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
    
    def move(self):
        self.x += self.velocity
        if self.x <= 0:
            #self.velocity = 3
            self.velocity = -self.velocity
            self.y += 20
        elif self.x >= 766:
            self.velocity = -self.velocity
            self.y +=20

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def pauseMenu(current):
    pause_font = pygame.font.SysFont(None, 60)
    pause_label = pause_font.render("Game Paused",1,(255,255,255))
    while True:
        
        window.blit(pause_label,(width/2-(pause_label.get_width()/2),height/2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        '''
        if back_button.draw_button():
            return
        '''
        keys = pygame.key.get_pressed()
        if keys[pygame.K_m]:
            mixer.music.pause()
            shotFired.set_volume(0)
            hitSound.set_volume(0)
        if keys[pygame.K_n]:
            mixer.music.play()
            volume_cur = mixer.music.get_volume()
            shotFired.set_volume(volume_cur)
            hitSound.set_volume(volume_cur)
        if keys[pygame.K_o]:
            return

        pygame.display.update()


def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 3
    main_font = pygame.font.SysFont("comicsans", 30)
    loss_font = pygame.font.SysFont("comicsans", 80)
    
    enemies = []
    global game_score
    game_score = 0
    wave_legth = 5
    bullet_vel = 4
    
    lost = False
    lost_count = 0

    mute = True

    player_speed = 5
    player = Player(350,500)

    def redraw_window():
        window.blit(background, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,255))
        score_label = main_font.render(f"Score: {game_score}", 1, (0,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        window.blit(lives_label, (10,10))
        window.blit(level_label, (width-level_label.get_width()-10, 10))
        window.blit(score_label, (10,30))

        for enemy in enemies:
            enemy.draw(window)

        player.draw(window)

        if lost:
            lost_label = loss_font.render("You lost!", 1, (255, 255, 255))
            window.blit(lost_label, (width/2 - lost_label.get_width()/2, 300))

        
        pygame.display.update()


    while run:
        clock.tick(FPS)
        curr_window = redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1
        
        if lost:
            if lost_count > FPS*3:
                with open("scores.txt", "a") as file:
                    file.write(str(game_score)+"\n")
                run = False
            else:
                # continue here means dont run anything bellow it just go back to the beginning of loop
                continue

        if len(enemies) == 0:
            level += 1
            #adds this many enemies to the next level, started with 5 enemies moved to 10 etc.
            wave_legth += 5

            for i in range(wave_legth):
                # gonna spawn them off screen, not aplicable for out game, but good to know
                enemy = Enemy(random.randrange(50, width-100), random.randrange(0,50), random.choice(["red","green"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
        paused = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - player_speed > 0:
            player.x -= player_speed
        if keys[pygame.K_d] and player.x + player_speed + player.get_width() < width:
            player.x += player_speed
        if keys[pygame.K_w] and player.y - player_speed > 0:
            player.y -= player_speed
        if keys[pygame.K_s] and player.y + player_speed + player.get_height() + 15 < height:
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()
        if keys[pygame.K_m]:
            mixer.music.pause()
            shotFired.set_volume(0)
            hitSound.set_volume(0)
        if keys[pygame.K_n]:
            mixer.music.play()
            volume_cur = mixer.music.get_volume()
            shotFired.set_volume(volume_cur)
            hitSound.set_volume(volume_cur)
        if keys[pygame.K_p]:
            pauseMenu(curr_window)



        for enemy in enemies[:]:
            enemy.move()
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot() 

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)



        player.move_bullets(-bullet_vel, enemies)

def options_menu():
    volume_max = 1
    volume_min = 0
    volume_now = 0.5
    volume_show = 5
    volume_up = button(width/2+80, height/2, 'up')
    volume_down = button(width/2-160, height/2, 'down')
    control_menu = button(width/2-40, height/2+100, 'Controls')

    volume_label_bg = Rect(width/2-40, height/2, 100, 40)
    masterVolume_label = main_font.render("Master Volume",1,(255,255,255))
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space2.webp')),(width,height))


    while True:
        volume_label = main_font.render(f"{volume_show}", 1, (255,0,0))
        window.blit(background,(0,0))
        window.blit(masterVolume_label,(width/2-60, height/2-50))
        pygame.draw.rect(window,(0,255,0),volume_label_bg)
        window.blit(volume_label, (width/2+2, height/2+10))
        if volume_up.draw_button():
            if volume_now < volume_max:
                volume_now += 0.1
                volume_now = round(volume_now,2)
                volume_show += 1
                hitSound.set_volume(volume_now)
                shotFired.set_volume(volume_now)
                mixer.music.set_volume(volume_now)
        if volume_down.draw_button():
            if volume_now > volume_min:
                volume_now -= 0.1
                volume_now = round(volume_now,2)
                volume_show -= 1
                hitSound.set_volume(volume_now)
                shotFired.set_volume(volume_now)
                mixer.music.set_volume(volume_now)
            
        if control_menu.draw_button():
            controls()
        if back_button.draw_button():
            return
        if credit_button.draw_button():
            credits()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.update()

def controls():
    while True:
            
        window.blit(background,(0,0))
        menu_label = main_font.render("In game controls",1,(255,255,255))
        moveHow = main_font.render("W,A,S,D to move",1,(255,255,255))
        shootHow = main_font.render("Space to shoot",1,(255,255,255))
        muteHow = main_font.render("M to Mute, N to Unmute",1,(255,255,255))
        pauseHow = main_font.render("P to Pause, O to Unpause",1,(255,255,255))

        window.blit(menu_label,(width/2-(menu_label.get_width()/2), 40))
        window.blit(moveHow,(width/2-(moveHow.get_width()/2), 100))
        window.blit(shootHow,(width/2-(shootHow.get_width()/2), 140))
        window.blit(muteHow,(width/2-(muteHow.get_width()/2), 180))
        window.blit(pauseHow,(width/2-(pauseHow.get_width()/2), 220))

        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()	

        pygame.display.update()

def high_scores():
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space3.jpg')),(width,height))
    while True:
         
        window.blit(background,(0,0))
        temp_lable = main_font.render("Work in progress",1,(255,255,255))
        window.blit(temp_lable,(width/2-(temp_lable.get_width()/2),height/2))
        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()	

        pygame.display.update()

def credits():
    label_tekijat = main_font.render("Tekijät:", 1, (255,255,255))       
    label_nimet = main_font.render("Dima, Pekka, Konsta, Marko",1,(0,255,255))
    while True:
        window.blit(background,(0,0))
        window.blit(label_tekijat, ((width/2-(label_tekijat.get_width()/2)), height/2))
        window.blit(label_nimet,((width/2-(label_nimet.get_width()/2)), height/2+30))

        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        pygame.display.update()
    

run = True
while run:

	window.blit(background,(0,0))

	if play_button.draw_button():
		print('play')
		main()
	if options_button.draw_button():
		options_menu()
	if score_button.draw_button():
		high_scores()
	if quit_button.draw_button():
		print('quit')
		break



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False	

	pygame.display.update()

pygame.quit()