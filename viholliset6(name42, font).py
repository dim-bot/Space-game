import pygame
import os
import sys
import time
import random
import keyboard
from pygame.locals import *
from pygame import mixer

pygame.init()
pygame.font.init()


width, height = 800, 600
window = pygame.display.set_mode((width,height))
pygame.display.set_caption('SuperDuperAwesome SpaceGame')
main_font = pygame.font.Font('STENCIL.ttf', 20)

enemy_ship1 = pygame.image.load(os.path.join("assets","ufo.png"))
enemy_ship2 = pygame.image.load(os.path.join("assets","ufoenemy.png"))
enemy_ship3 = pygame.image.load(os.path.join("assets","attackship.png"))
player_ship = pygame.image.load(os.path.join("assets","spaceship.png"))
bullet_player = pygame.image.load(os.path.join("assets","bullet.png"))
bullet_enemy = pygame.image.load(os.path.join("assets", "bulletEnemy.png"))
background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space.jpeg')),(width,height))

with open("volume.txt", "r") as file:
    volumeList = file.readlines()
    volume_now = float(volumeList[0])


# background sounds
shotFired = mixer.Sound(os.path.join('assets', 'laser.wav'))
hitSound = mixer.Sound(os.path.join('assets', 'explosion.wav'))
hitSound.set_volume(volume_now)
shotFired.set_volume(volume_now)

mixer.music.load(os.path.join('assets','bg_music.wav'))
mixer.music.set_volume(volume_now)
mixer.music.play(-1)

#rgb sets
blue = (0,0,255)
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)

clicked = False

class TextInputBox(pygame.sprite.Sprite):
    def __init__(self, x, y, w, font):
        super().__init__()
        self.color = (255, 255, 255)
        self.backcolor = None
        self.pos = (x, y) 
        self.width = w
        self.font = font
        self.active = False
        self.text = ""
        self.render_text()

    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface((max(self.width, t_surf.get_width()+10), t_surf.get_height()+10), pygame.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft = self.pos)

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and len(self.text) != 0:
                    scoreHandler(self.text,True)
                elif event.key == pygame.K_RETURN and len(self.text) == 0:
                    pass
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_SPACE:
                    pass
                else:
                    self.text += event.unicode
                self.render_text()

def scoreHandler(text,state):
    
    with open("scores.txt", "r+") as file:
        score_list = file.readlines()
        score_list = [x.strip() for x in score_list]
        unsorted_list = []
        for score in score_list:
            space = score.find(" ")
            tempScore = score[space:]
            tempName = score[0:space]
            tempString = list()
            tempString.insert(0,tempName)
            tempString.insert(1,int(tempScore))
            unsorted_list.append(tempString)
        # sortin a list to be from highest to lowest score
        sorted_list = sorted(unsorted_list, key=lambda score: score[1], reverse=True)

    if state == False:
        return sorted_list

    if state == True:
        tempString = list()
        if text == "42":
            text = "Calculating"
        tempString.insert(0,text)
        tempString.insert(1,int(game_score))
        unsorted_list.append(tempString)
        sorted_list = sorted(unsorted_list, key=lambda score: score[1], reverse=True)
        with open("scores.txt", "w") as file:
            i=0
            for item in sorted_list:
                for thing in item:
                    file.writelines(str(thing))
                    i+=1
                    if i%2 ==0:
                        file.write("\n")
                    else:
                        file.write(" ")
                if i == 20:
                    break
                
        main_menu()

    

class button():
	
	button_col = (0, 0, 255)
	hover_col = (75, 225, 255)
	click_col = (50, 150, 255)
	text_col = black
	buttonW = 115
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

play_button = button(width/2-60, height/2+50, 'Play')
options_button = button(width/2-60, height/2+100, 'Options')
score_button = button(width/2-60, height/2+150, 'Scores')
quit_button = button(width/2-60, height/2+200, 'Quit')
back_button = button(width/2-60, height/2+200, 'Back')
credit_button = button(width/2-60, height/2+150, 'Credits')
main_button = button(width/2-60, height/2+200, 'Main Menu')

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

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.velocity = 1
        self.shooting = False
        self.bullets = []
        self.cool_down_counter = 0
        self.multi = False
        self.COOLDOWN = 30
        

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
                if obj.health <= 0:
                    global lives
                    if lives > 0:
                        lives -= 1
                        obj.health = 100

                    if lives <= 0 and obj.health <= 0:
                        game_over()
                    
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
        self.COOLDOWN = 15

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
                        enemy_vars = obj.__dict__
                        enemy_vars_items = enemy_vars.items()
                        for var in enemy_vars_items:
                            if var == ('multi', True):
                                global difficulty_multiplier
                                rand_top = difficulty_multiplier*1
                                for i in range(0,int(rand_top)):
                                    new_enemy = Enemy(obj.x-50, obj.y, random.choice(["pew","zoom"]))
                                    objs.append(new_enemy)
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
        "pew": (enemy_ship1, bullet_enemy,1,True,False),
        "zoom": (enemy_ship2, bullet_enemy,2,False,False),
        "chonk": (enemy_ship3, bullet_enemy,0.5,False,True)
    }
    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img, self.velocity, self.shooting, self.multi = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        global difficulty_multiplier
        if self.multi == False:
            self.velocity *= difficulty_multiplier
            direction = [-1,1]
            randomDirection = random.choice(direction)
            self.velocity *= randomDirection
    
    def move(self):
        if self.multi == True:
            self.y += self.velocity
        else:
            self.x += self.velocity
            if self.x <= 0:
                #self.velocity = 3
                self.velocity = -self.velocity
                self.y += 20
            elif self.x >= 766:
                self.velocity = -self.velocity
                self.y +=20

def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def pauseMenu(current,muted):
    pause_font = pygame.font.Font('STENCIL.ttf', 60)
    pause_label = pause_font.render("Game Paused",1,(255,255,255))

    while True:
        
        window.blit(pause_label,(width/2-(pause_label.get_width()/2),height/2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == KEYDOWN and event.key == K_m:
                if muted == False:
                    muted = True
                    mixer.music.pause()
                    shotFired.set_volume(0)
                    hitSound.set_volume(0)
                elif muted == True:
                    muted = False
                    mixer.music.play()
                    volume_cur = mixer.music.get_volume()
                    shotFired.set_volume(volume_cur)
                    hitSound.set_volume(volume_cur)

            if event.type == KEYDOWN and event.key == K_p:
                return muted
        
        if main_button.draw_button():
            main_menu()
        
        pygame.display.update()

def game_over():
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space3.jpg')),(width,height))
    clock = pygame.time.Clock()
    loss_font = pygame.font.Font('STENCIL.ttf', 70)
    input_font = pygame.font.Font('STENCIL.ttf',20)
    font = pygame.font.Font('STENCIL.ttf', 80)
    text_input_box = TextInputBox(300,400,200,font)
    lost_label = loss_font.render("Game Over", 1, (255, 255, 255))
    input_label = input_font.render("Enter your name and press enter",1,(255,255,255))
    group = pygame.sprite.Group(text_input_box)
    while True:
        
        window.blit(background,(0,0))
        window.blit(lost_label, ((width/2-lost_label.get_width()/2),250))
        window.blit(input_label,((width/2-input_label.get_width()/2),350))
        clock.tick(60)
        event_list = pygame.event.get()
        keys = pygame.key.get_pressed()
        #5.2 edit
        if back_button.draw_button():
            main_menu()
        for event in event_list:
            if event.type == pygame.QUIT:
                sys.exit()
        group.update(event_list)

        group.draw(window)
        pygame.display.flip()

def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    global lives
    lives = 3
    main_font = pygame.font.Font('STENCIL.ttf', 20)
    loss_font = pygame.font.Font('STENCIL.ttf', 70)
    
    enemies = []
    global game_score
    game_score = 0
    wave_legth = 5
    bullet_vel = 4
    global difficulty_multiplier
    difficulty_multiplier = 1

    mute = False

    player_speed = 6
    player = Player(385,500)

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
        
        pygame.display.update()


    while run:
        clock.tick(FPS)
        curr_window = redraw_window()

        if lives <= 0 and player.health <= 0:
            game_over()
 
            
        if len(enemies) == 0:
            level += 1
            temp_font = pygame.font.Font('STENCIL.ttf', 25)
            tutorial_label = temp_font.render("If enemies reach the bottom you'll lose, stop them!",1,(255,0,0))
            level_begin = loss_font.render(f"Level: {level}", 1, (200,2,50))
            timed_loop = int(time.time() + 4)
            time_now = int(time.time())
            integ = 0
            while True:
                wave_countdown = timed_loop-time_now
                if wave_countdown == 3 and integ == 0:
                    redraw_window()
                    integ += 1
                if wave_countdown == 2 and integ == 1:
                    redraw_window()
                    integ +=1
                if wave_countdown == 1 and integ == 2:
                    redraw_window()
                    integ +=1
                #5.2 edit
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()

                wave_start = loss_font.render(f"{wave_countdown}",1,(255,0,0))
                if time_now == timed_loop:
                    break
                if level == 1:
                    window.blit(tutorial_label,((width/2-tutorial_label.get_width()/2),height/2-100))
                window.blit(wave_start,((width/2-wave_start.get_width()/2),height/2+100))
                window.blit(level_begin,((width/2-level_begin.get_width()/2),height/2))
                pygame.display.update()
                time_now = int(time.time())
            #adds this many enemies to the next level, started with 5 enemies moved to 10 etc.
            if level > 1:
                lives += 1
            if level%2 != 0:
                wave_legth += 5
            else:
                difficulty_multiplier += 0.1

            for i in range(wave_legth):
                # gonna spawn them off screen, not aplicable for out game, but good to know
                enemy = Enemy(random.randrange(50, width-50), random.randrange(0,50), random.choice(["pew","zoom","chonk"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == KEYDOWN and event.key == K_p:
                mute = pauseMenu(curr_window, mute)
            if event.type == KEYDOWN and event.key == K_m:
                if mute == False:
                    mute = True
                    mixer.music.pause()
                    shotFired.set_volume(0)
                    hitSound.set_volume(0)
                elif mute == True:
                    mute = False
                    mixer.music.play()
                    volume_cur = mixer.music.get_volume()
                    shotFired.set_volume(volume_cur)
                    hitSound.set_volume(volume_cur)

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



        for enemy in enemies[:]:
            enemy.move()
            enemy.move_bullets(bullet_vel, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot() 

            if collide(enemy, player):
                player.health -= 10
                if player.health <= 0:
                    if lives > 0:
                        lives -= 1
                        player.health = 100

                    if lives <= 0 and player.health <= 0:
                        game_over()    
                enemy_vars = enemy.__dict__
                enemy_vars_items = enemy_vars.items()
                for var in enemy_vars_items:
                    if var == ('multi', True):
                        if enemy.y-40 < 0:
                            enemySpawnY = 0
                        else:
                            enemySpawnY = enemy.y-40
                        new_enemy = Enemy(enemy.x, enemySpawnY, random.choice(["pew","zoom"]))
                        enemies.append(new_enemy)
                enemies.remove(enemy)
                         
            
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)



        player.move_bullets(-bullet_vel, enemies)

def options_menu():
    with open("volume.txt", "r") as file:
        volumeList = file.readlines()
        volume_now = float(volumeList[0])

    volume_max = 1
    volume_min = 0
    volume_show = int(volume_now*10)
    volume_up = button(width/2+55, height/2, 'up')
    volume_down = button(width/2-175, height/2, 'down')
    control_menu = button(width/2-60, height/2+100, 'Controls')

    volume_label_bg = Rect(width/2-55, height/2, 105, 40)
    masterVolume_label = main_font.render("Master Volume",1,(255,255,255))
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','space2.webp')),(width,height))


    while True:
        volume_label = main_font.render(f"{volume_show}", 1, (255,0,0))
        window.blit(background,(0,0))
        window.blit(masterVolume_label,(width/2-60, height/2-50))
        pygame.draw.rect(window,(0,255,0),volume_label_bg)
        window.blit(volume_label, (width/2-8, height/2+10))
        if volume_up.draw_button():
            if volume_now < volume_max:
                volume_now += 0.1
                volume_now = round(volume_now,2)
                volume_show += 1
                with open("volume.txt", "w") as file:
                    file.write(str(volume_now))
                hitSound.set_volume(volume_now)
                shotFired.set_volume(volume_now)
                mixer.music.set_volume(volume_now)
        if volume_down.draw_button():
            if volume_now > volume_min:
                volume_now -= 0.1
                volume_now = round(volume_now,2)
                volume_show -= 1
                with open("volume.txt", "w") as file:
                    file.write(str(volume_now))
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
        menu_label = main_font.render("In game controls",1,(255,2,0))
        moveHow = main_font.render("W,A,S,D to move",1,(255,255,255))
        shootHow = main_font.render("Space to shoot",1,(255,255,255))
        muteHow = main_font.render("M to Mute and Unmute",1,(255,255,255))
        pauseHow = main_font.render("P to Pause and Unpause",1,(255,255,255))

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
    tops = scoreHandler("x",False)
    while True:
         
        window.blit(background,(0,0))

        scoreH = 140
        nameW = 350

        top5 = 0
        i = 0
        for item in tops:
            for thing in item:
                i+=1
                tempLable = main_font.render(f"{thing}",1,(255,255,255))
                if i%2 == 0:
                    nameW += margin
                    window.blit(tempLable,(nameW,scoreH))
                    nameW -= margin
                    scoreH += 40
                else:
                    window.blit(tempLable,(nameW,scoreH))
                    margin = (tempLable.get_width()+ 40)
            top5+=1
            if top5 == 5:
                break
        

        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()	

        pygame.display.update()

def credits():
    label_tekijat = main_font.render("Tekijät:", 1, (255,255,255))       
    label_nimet = main_font.render("Dima, Pekka, Konsta",1,(0,255,255))
    label_guru = main_font.render("Koodaus avustaja:", 1, (255,255,255))
    label_marko = main_font.render("Marko", 1, (0,255,255))
    while True:
        window.blit(background,(0,0))
        window.blit(label_tekijat, ((width/2-(label_tekijat.get_width()/2)), height/2-30))
        window.blit(label_nimet,((width/2-(label_nimet.get_width()/2)), height/2))
        window.blit(label_guru,((width/2-(label_guru.get_width()/2)), height/2+60))
        window.blit(label_marko,((width/2-(label_marko.get_width()/2)), height/2+90))

        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        pygame.display.update()
    
    
def main_menu():
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
            sys.exit()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.update()
main_menu()