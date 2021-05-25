#Tekijät: Petrov Dmitry, Hautala Pekka, Karapalo Konsta. Koodi "neuvottelija": Ollila Marko.
#Space "Invader" -esq peli, Versio 7.2, Tampere 2020-16.05.2021

import pygame
import os
import sys
import time
import random
from pygame.locals import *
from pygame import mixer

#Käynnistetään pygame ja fontti
pygame.init()
pygame.font.init()

#Määritellään ruudun koko, otsikko, iconi ja pääfontti
width, height = 800, 600
window = pygame.display.set_mode((width,height))
pygame.display.set_caption('Space Incursion 2073')
icon = pygame.image.load(os.path.join("assets","Space Incursion 2073 Icon.png"))
pygame.display.set_icon(icon)

#Ladataan pääfontti ja kuvat
main_font = pygame.font.Font('STENCIL.ttf', 20)
enemy_ship1 = pygame.image.load(os.path.join("assets","attackship_1.png"))
enemy_ship2 = pygame.image.load(os.path.join("assets","attackship_2.png"))
enemy_ship3 = pygame.image.load(os.path.join("assets","attack_ship.png"))
player_ship = pygame.image.load(os.path.join("assets","player.png"))
bullet_player = pygame.image.load(os.path.join("assets","player_ammo_harmaa.png"))
bullet_enemy = pygame.image.load(os.path.join("assets", "Enemyammo.png"))
background = pygame.transform.scale(pygame.image.load(os.path.join('assets','background.gif')),(width,height))
background_1 = pygame.transform.scale(pygame.image.load(os.path.join('assets','menu background_logo.png')),(width,height))

#Avataan tekstitiedosto jossa on tallennettu ääniasetukset
with open("volume.txt", "r") as file:
    volumeList = file.readlines()
    volume_mus = float(volumeList[0])
    volume_fx = float(volumeList[1])

#Ladataan ja asetetaan äänenvoimakkuus ääniefekteille sekä musiikille
shotFiredEnemy = mixer.Sound(os.path.join('assets', 'Ampuminen_vihollinen.mp3'))
shotFiredPlayer = mixer.Sound(os.path.join('assets', 'player_shooting.wav'))
hitSound = mixer.Sound(os.path.join('assets', 'Räjähdys2.mp3'))
hitSound.set_volume(volume_fx)
shotFiredEnemy.set_volume(volume_fx)
shotFiredPlayer.set_volume(volume_fx)

mixer.music.load(os.path.join('assets','musiikki.wav'))
mixer.music.set_volume(volume_mus)
mixer.music.play(-1)

#Määritellään muutama RGB väri
blue = (0,0,255)
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)

clicked = False

#Luokka joka hoitaa kirjoittamisen tulostusta kun pelaaja pelin loputtua
class TextInputBox(pygame.sprite.Sprite):

    #Määritellään teksikentälle tyhjiä muuttujia
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

    #Funktio joka piirtää suorakulmion ja tulostaa tekstin
    def render_text(self):
        t_surf = self.font.render(self.text, True, self.color, self.backcolor)
        self.image = pygame.Surface((max(self.width, t_surf.get_width()+10), t_surf.get_height()+10), pygame.SRCALPHA)
        if self.backcolor:
            self.image.fill(self.backcolor)
        self.image.blit(t_surf, (5, 5))
        pygame.draw.rect(self.image, self.color, self.image.get_rect().inflate(-2, -2), 2)
        self.rect = self.image.get_rect(topleft = self.pos)

    #Funktio joka katsoo käyttäjän syötettä. Mikäli suöte on välilyönti tai jos nimen pituus on 0, mitään ei tapahdu
    #Muulloin tulosetetaan käyttäjän syöttämät kirjaimet ruudulle, kunnes painetaan ENTER
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

#Funktio joka hoitaa pistelaskuja
def scoreHandler(text,state):
    
    #Avataan tekstitiedosto jossa on nimet ja niiden pisteen. Luetaan, heitetään ylimääräiset \n ja välit pois
    #Laitetaan kaikki muuttujat listaan
    with open("scores.txt", "r+") as file:
        score_list = file.readlines()
        score_list = [x.strip() for x in score_list]
        unsorted_list = []
        #Käsittelee muuttuja kerrallaan ja pilkkoo ne kahteen osaan, jonka jälkeen tallentaa ne kirjastoon
        for score in score_list:
            space = score.find(" ")
            tempScore = score[space:]
            tempName = score[0:space]
            tempString = list()
            tempString.insert(0,tempName)
            tempString.insert(1,int(tempScore))
            unsorted_list.append(tempString)
        #Järjestetään kirjasto suuruusjärjestykseen isommasta pienempään
        sorted_list = sorted(unsorted_list, key=lambda score: score[1], reverse=True)

    #Tämä toteutuu ainoastaan main menusta
    if state == False:
        return sorted_list

    #Tämä toteutuu ainoastaan jos pelaaja tallentaa nimen, jolloin sen nimi ja pisteet lisätään edelliseen listaan
    #Sen jälkeen lista järjestetään suuruusjärjestykseen ja tallennetaan ensimmäiset 20 riviä eli 10 nimeä ja 10 tulosta
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
        #Kun pisteet on tallentunut, palataan takaisin main menuun.
        main_menu()

    
#Luokka joka hoitaa näppäinten luonteja
class button():
	
    #Muutama RGB väri ja näppäimen suunnat
	button_col = (0, 0, 255)
	hover_col = (75, 225, 255)
	click_col = (50, 150, 255)
	text_col = black
	buttonW = 115
	buttonH = 40
	
    #Määritellään tyhjän tekstikentän ja paikan
	def __init__(self, x, y, text):
		self.x = x
		self.y = y
		self.text = text

    #Funktio joka piirtää näppäimen ruudulle
	def draw_button(self):
		global clicked
		action = False
        #Tarkistaa hiiren koordinaatteja näppäimiä vastaan ja jos hiiren kursori on näppäimen yläpuolella sekä hiiren näppäintä
        #painetaan muutetaan näppäimen väriä
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

#Luodaan näppäimiä
play_button = button(width/2-60, height/2+50, 'Play')
options_button = button(width/2-60, height/2+100, 'Options')
score_button = button(width/2-60, height/2+150, 'Scores')
quit_button = button(width/2-60, height/2+200, 'Quit')
back_button = button(width/2-60, height/2+200, 'Back')

#Luokka joka hoitaa luoteihin liittyviä asioita
class Bullet:

    #Määritellään muuttujia ja asetetaan luodille mask. Mask on tarkempi tapa laskea missä kuvan pixelit menee, jotta oikean
    # osumat voitasiin vertailla
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    #Piirretään luoteja
    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    #luodin nopeus funktio
    def moveB(self, vel):
        self.y += vel

    #Tarkistaa onko luoti ruudun ulkopuolella
    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    #Tarkistaa onko luoti törmännyt jhonkin
    def collision(self, obj):
        return collide(self, obj)

#Luokka jota käytetään sekä pelaajan että vihollisten määrittelyyn
class Ship:

    #Määritellään muuttujia
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
        
    #Kutsutaan bullet luokka draw funktio, eli piirretään luoteja
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for bullet in self.bullets:
            bullet.draw(window)

    #Funktio joka hoitaa luotien liikkumista.
    def move_bullets(self, vel, obj):
        #Tarkistaa voiko tietty objekti ampua vai ei, jonka jälkeen liikutetaan luoteja jotka on luotu eteenpäin
        self.cooldown()
        for bullet in self.bullets:
            bullet.moveB(vel)
            if bullet.off_screen(height):
                self.bullets.remove(bullet)

            #Jos luoti osuu pelaajaan, toistetaan ääniefekti ja miinustetaan pelaajan HP, jonka jälkeen poistetaan luoti
            elif bullet.collision(obj):
                hitSound.play()
                obj.health -= 10
                if obj.health <= 0:
                    global lives
                    if lives > 0:
                        lives -= 1
                        obj.health = 100
                    #Jos elämät ja pelaajan HP on 0, peli loppuu
                    if lives <= 0 and obj.health <= 0:
                        game_over()
                self.bullets.remove(bullet)

    #Funktio joka laskee voiko jokin objekti ampua vielä vai ei
    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter  += 1

    #Riippuen kuka ampui, toistetaan oikea ääniefekti ja lisätään luoti listaan
    def shoot(self,identity):
        if self.cool_down_counter == 0 and self.shooting == True:
            if identity == "player":
                shotFiredPlayer.play()
            elif identity == "enemy":
                shotFiredEnemy.play()
            bullet = Bullet(self.x+20, self.y, self.bullet_img)
            self.bullets.append(bullet)
            self.cool_down_counter = 1

    #Laskee alusten mittoja
    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

#Luokka joka hoitaa pelaajan asetuksia käyttämällä Ship luokkaa pohjana.
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

    #Liikutetaan pelaajan luoteja ja tarkistetaan osuiko ne
    def move_bullets(self, vel, objs):
        self.cooldown()
        for bullet in self.bullets:
            bullet.moveB(vel)
            if bullet.off_screen(height):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    #Jos luoti osui poistetaan objekti johon se törmäsi
                    if bullet.collision(obj):
                        # Kun vihollinen poistetaan, sen omat bullet listat poistetaan myös, mikä poistaa kaikki sen vihollisen luodit
                        # jotka ovat vielä matkalla
                        hitSound.play()
                        enemy_vars = obj.__dict__
                        enemy_vars_items = enemy_vars.items()
                        for var in enemy_vars_items:
                            #Tämä tarkistaa jos vihollisaluksen tag on multi, ja jos on, niin kutsuu sen tilalle uusia vihollisia
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
    
    #Piirretään pelaaja
    def draw(self,window):
        super().draw(window)
        self.health_bar(window)

    #Piirretään pelaajan HP mitta
    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))

#Luokka joka hoitaa vihollisten asetuksia käyttämällä Ship luokkaa pohjana.
class Enemy(Ship):

    #Kun kutsutaan funktiota joka luo vihollisia se arpoo kolmen sanan välillä yhden ja luo vastaavan käyttämällä alla olevaa karttaa
    COLOR_MAP = {
        "pew": (enemy_ship1, bullet_enemy,1,True,False),
        "zoom": (enemy_ship2, bullet_enemy,2,False,False),
        "chonk": (enemy_ship3, bullet_enemy,0.5,False,True)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        #Tässä annteaan useammalle muuttujalle arvo COLOR_MAP järjestyksen perusteella
        self.ship_img, self.bullet_img, self.velocity, self.shooting, self.multi = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        global difficulty_multiplier
        #Mikäli kyseessä on alus jolla multi muuttuja on FALSE, asetetaan niille uusi nopeus ja arvotaan kulkusuunta
        if self.multi == False:
            self.velocity *= difficulty_multiplier
            direction = [-1,1]
            randomDirection = random.choice(direction)
            self.velocity *= randomDirection
    
    #Liikuttaa vihollis alusta 
    def move(self):

        #Jos Multi arvo aluksella on True, sitä liikutetaan Y-akselia pitkin, muulloin X-akselia.
        # Kun alus saavuttaa ruudun reunaan, tiputetaan se hitusen alas,
        # sen "nopeus" arvo muuttuu negatiiviseksi, jolloin se lähtee kulkemaan eri suuntaan
        if self.multi == True:
            self.y += self.velocity
        else:
            self.x += self.velocity
            if self.x <= 0:
                self.velocity = -self.velocity
                self.y += 20
            elif self.x >= 766:
                self.velocity = -self.velocity
                self.y +=20

#Tarkistaa onko pelaaja törmännyt viholliseen maskin avulla
def collide(obj1, obj2):
    offset_x = int(obj2.x - obj1.x)
    offset_y = int(obj2.y - obj1.y)
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

#Kun painetaan P:ta laitetaan peli pauselle
def pauseMenu(current,muted):
    pause_font = pygame.font.Font('STENCIL.ttf', 60)
    pause_label = pause_font.render("Game Paused",1,(255,255,255))
    main_button = button(width/2-60, height/2+200, 'Main Menu')
    while True:
        
        window.blit(pause_label,(width/2-(pause_label.get_width()/2),height/2))

        for event in pygame.event.get():

            #Jos käyttäjä painaa raksia, sammutetaan ikkuna ja peli
            if event.type == pygame.QUIT:
                sys.exit()
            
            #Jos painetaan m ja mute ei ole True, mykistetään äänet, muulloin laitetaan äänet aikaisempien asetuksien perusteella
            if event.type == KEYDOWN and event.key == K_m:
                if muted == False:
                    muted = True
                    mixer.music.set_volume(0)
                    shotFiredPlayer.set_volume(0)
                    shotFiredEnemy.set_volume(0)
                    hitSound.set_volume(0)
                elif muted == True:
                    muted = False
                    mixer.music.set_volume(volume_mus)
                    shotFiredPlayer.set_volume(volume_fx)
                    shotFiredEnemy.set_volume(volume_fx)
                    hitSound.set_volume(volume_fx)

            #Jos painetaan P:ta uudestaan, palataan takasin peliin
            if event.type == KEYDOWN and event.key == K_p:
                return muted
        
        #Jos pelaaja ei haluaa jatkaa, palataan takaisiin main menuun
        if main_button.draw_button():
            main_menu()
        
        #Päivitetään ruutua, muulloin mitään liikettä ei näkyisi
        pygame.display.update()

#Peli loppui menu
def game_over():

    #Määritellään muuttujia ja fontteja
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','menu background_logo.png')),(width,height))
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
        #Tarkistetaan kaikkia syötteitä, laitetaan ne listaan
        event_list = pygame.event.get()
        keys = pygame.key.get_pressed()
        #Nappi jolla voi palata takaisin main menuun, jos ei haluaa tallentaa tulosta
        if back_button.draw_button():
            main_menu()
        for event in event_list:
            if event.type == pygame.QUIT:
                sys.exit()
        #Kutsutaan text_imput_box luokasta update funktio ja annetaan sille muuttujina koko tapahtuma lista
        group.update(event_list)

        group.draw(window)
        pygame.display.flip()

#Pää peli silmukka
def main():

    #Määritellään muuttujia
    with open("volume.txt", "r") as file:
        volumeList = file.readlines()
        volume_mus = float(volumeList[0])
        volume_fx = float(volumeList[1])
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
    player = Player(370,500)

    #Piirretään ruudulle otsikoita, jotka muuttuu ajan kanssa
    def redraw_window():
        window.blit(background, (0,0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (0,0,255))
        score_label = main_font.render(f"Score: {game_score}", 1, (0,255,255))
        level_label = main_font.render(f"Level: {level}", 1, (255,255,255))
        window.blit(lives_label, (10,10))
        window.blit(level_label, (width-level_label.get_width()-10, 10))
        window.blit(score_label, (10,30))

        #piirtää vihollisia, pelaajaa ja päivittää ruudun, muuten asiat liikkuisi, mutta sitä ei näkyisi
        for enemy in enemies:
            enemy.draw(window)

        player.draw(window)
        
        pygame.display.update()

    #Silmukka jossa itse peli pääosin sijaitsee
    while run:

        clock.tick(FPS)
        curr_window = redraw_window()

        if lives <= 0 and player.health <= 0:
            game_over()
 
        #Tarkistetaan onko vihollis lista tyhjä ja jos on luodaan uusia vihollisia
        if len(enemies) == 0:
            level += 1
            temp_font = pygame.font.Font('STENCIL.ttf', 25)
            tutorial_label = temp_font.render("If enemies reach the bottom you'll lose, stop them!",1,(255,0,0))
            level_begin = loss_font.render(f"Level: {level}", 1, (200,2,50))
            timed_loop = int(time.time() + 4)
            time_now = int(time.time())
            integ = 0
            #Tulosaa ruudulle milloin seuraava taso alkaa
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
            #Kun taso vaihtuu peplaaja saa yhden elämän
            if level > 1:
                lives += 1
            #Jos taso on on tasan kahdella jaettava, luodaan enemmän vihollisia ja jos ei, niin lisätään vihollisten mod
            # mod nostaa "zoom" ja "pew" vihollisten nopeutta, sekä määrittää kertoimen "chonk" viholliselle, joka tuhoutuessaan
            # kutsuu uusia vihollisia mod perusteella
            if level%2 != 0:
                wave_legth += 5
            else:
                difficulty_multiplier += 0.1

            for i in range(wave_legth):
                #Peru jokainen vihollinen mitä kentälle pitäisi kutsua, arvotaan sille koordinaatti ja sana, joka määrittää
                # vihollisen alus tyypin. tämän jälkeen lisätään se listaan
                enemy = Enemy(random.randrange(50, width-50), random.randrange(0,50), random.choice(["pew","zoom","chonk"]))
                enemies.append(enemy)

        #Tarkistetaan tapahtumia. P ja M, pause ja mute.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == KEYDOWN and event.key == K_p:
                mute = pauseMenu(curr_window, mute)
            if event.type == KEYDOWN and event.key == K_m:
                if mute == False:
                    mute = True
                    mixer.music.set_volume(0)
                    shotFiredPlayer.set_volume(0)
                    shotFiredEnemy.set_volume(0)
                    hitSound.set_volume(0)
                elif mute == True:
                    mute = False
                    mixer.music.set_volume(volume_mus)
                    shotFiredPlayer.set_volume(volume_fx)
                    shotFiredEnemy.set_volume(volume_fx)
                    hitSound.set_volume(volume_fx)

        #Liikutetaan pelaaja oikeeseen suuntaan, niin kauan kunnes törmätään ruudun reunaan. Jos pelaaja painaa välilyöntiä
        # kutsutaan pelaaja luokan shoot funktiota, joka luo pelaajalle luodin.
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
            var = "player"
            player.shoot(var)


        #Liikutetaan vihollisia ja niiden luoteja
        for enemy in enemies[:]:
            enemy.move()
            enemy.move_bullets(bullet_vel, player)

            #Tämä arpoo numeroita 0-120 ja jos se osuu 1, mikäli vihollinen voi ampua, se ampuu. Koko silmukkaa käydään läpi 60 kertaa
            # sekunnissa, joten keskivarvon mukaan vihollis alus ampuu aina 2s välein. Tämä ei välttämättä aina pidä paikkansa,
            # mutta koska vihollisilla on COOLDOWN = 30, niin ne eivät voi ampua 60 kertaa sekunnissa jos kone arpoo pelkkiä ykkösiä.
            if random.randrange(0, 120) == 1:
                var1 = "enemy"
                enemy.shoot(var1) 

            #Jos vihollinen osui pelaajaan tai pelaaja taklasi vihollisen aluksellaan
            # Huom. Pelaaja ei saa pisteitä törmäämällä viholliseen, sillä tarkoituksena on ampua heidän ja välttyä vahingolta
            if collide(enemy, player):
                player.health -= 10
                if player.health <= 0:
                    if lives > 0:
                        lives -= 1
                        player.health = 100

                    if lives <= 0 and player.health <= 0:
                        game_over()
                #Tässä tutkitaan vihollisten listaa ja katsotaan onko törmänneellä vihollisella muuttuja multi == True
                # Jos on, niin kutsutaan lisää vihollisia tässä kohtaa ja poistetaan kanto alus.
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
                         
            #Jos vihollis alus pääsee alareunaan asti, alus poistetaan ja vähennetään yksi elämä
            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)


        #Kutsutaan funktio joka liikuttaa pelaajan luoteja
        player.move_bullets(-bullet_vel, enemies)

#
def options_menu():
    #Luodaan painikkeita ja luetaan listasta ääniesetuksia jotta niitä voidaan muokata nappeja painalalla. Uudet ääniaetukset tallennetaan
    # Kun käyttäjä poistuu valikosta takaisin main menuun 
    credit_button = button(width/2-60, height/2+150, 'Credits')
    with open("volume.txt", "r") as file:
        volumeList = file.readlines()
        volume_mus = float(volumeList[0])
        volume_fx = float(volumeList[1])
    volume_now = volume_mus

    volume_max = 1
    volume_min = 0
    volume_show_mus = int(volume_mus*10)
    volume_show_fx = int(volume_fx*10)

    volume_up_mus = button(width/2+55, height/2-100, 'up')
    volume_down_mus = button(width/2-175, height/2-100, 'down')

    volume_up_fx = button(width/2+55, height/2, 'up')
    volume_down_fx = button(width/2-175, height/2, 'down')  

    control_menu = button(width/2-60, height/2+100, 'Controls')

    mus_volume_label_bg = Rect(width/2-55, height/2, 105, 40)
    fx_volume_label_bg = Rect(width/2-55, height/2-100, 105, 40)
    musicVolume_label = main_font.render("Music Volume",1,(255,255,255))
    fxVolume_label = main_font.render("FX Volume",1,(255,255,255))
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','menu background_logo.png')),(width,height))


    while True:
        mus_volume_label = main_font.render(f"{volume_show_mus}", 1, (255,0,0))
        fx_volume_label = main_font.render(f"{volume_show_fx}", 1, (255,0,0))
        window.blit(background,(0,0))
        window.blit(musicVolume_label,(width/2-(musicVolume_label.get_width()/2)-5, height/2-130))
        window.blit(fxVolume_label,(width/2-(fxVolume_label.get_width()/2)-3, height/2-30))
        pygame.draw.rect(window,(0,255,0),mus_volume_label_bg)
        pygame.draw.rect(window,(0,255,0),fx_volume_label_bg)
        window.blit(mus_volume_label, (width/2-8, height/2-90))
        window.blit(fx_volume_label, (width/2-8, height/2+10))

        # music buttons
        if volume_up_mus.draw_button():
            if volume_mus < volume_max:
                volume_mus += 0.1
                volume_mus = round(volume_mus,2)
                volume_show_mus += 1
                mixer.music.set_volume(volume_mus)
        if volume_down_mus.draw_button():
            if volume_mus > volume_min:
                volume_mus -= 0.1
                volume_mus = round(volume_mus,2)
                volume_show_mus -= 1
                mixer.music.set_volume(volume_mus)
        # fx buttons
        if volume_up_fx.draw_button():
            if volume_fx < volume_max:
                volume_fx += 0.1
                volume_fx = round(volume_fx,2)
                volume_show_fx += 1
                hitSound.set_volume(volume_fx)
                shotFiredPlayer.set_volume(volume_fx)
                shotFiredEnemy.set_volume(volume_fx)
        if volume_down_fx.draw_button():
            if volume_fx > volume_min:
                volume_fx -= 0.1
                volume_fx = round(volume_fx,2)
                volume_show_fx -= 1
                hitSound.set_volume(volume_fx)
                shotFiredPlayer.set_volume(volume_fx)
                shotFiredEnemy.set_volume(volume_fx)
        
        #Napit jotka johtaa ohjausmenuun, takasin alku valikkoon tai credits menuun
        if control_menu.draw_button():
            controls()
        if back_button.draw_button():
            with open("volume.txt", "w") as file:
                file.write(str(volume_mus)+"\n")
                file.write(str(volume_fx))
            return
        
        if credit_button.draw_button():
            credits()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.update()

#Tämä menu piirtää vain muutaman lauseen jotka selostaa pelin ohjauksia
def controls():
    while True:
            
        window.blit(background_1,(0,0))
        menu_label = main_font.render("In game controls",1,(255,2,0))
        moveHow = main_font.render("W,A,S,D to move",1,(255,255,255))
        shootHow = main_font.render("Space to shoot",1,(255,255,255))
        muteHow = main_font.render("M to Mute and Unmute",1,(255,255,255))
        pauseHow = main_font.render("P to Pause and Unpause",1,(255,255,255))

        window.blit(menu_label,(width/2-(menu_label.get_width()/2), 200))
        window.blit(moveHow,(width/2-(moveHow.get_width()/2), 300))
        window.blit(shootHow,(width/2-(shootHow.get_width()/2), 320))
        window.blit(muteHow,(width/2-(muteHow.get_width()/2), 340))
        window.blit(pauseHow,(width/2-(pauseHow.get_width()/2), 360))

        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()	

        pygame.display.update()

#Menu jossa näkyy parhaat tulokset
def high_scores():
    background = pygame.transform.scale(pygame.image.load(os.path.join('assets','menu background_logo.png')),(width,height))
    #Kutsutaan muuttuja joha hoitaa pistelaskut
    tops = scoreHandler("x",False)
    while True:
         
        window.blit(background,(0,0))

        scoreH = 140
        nameW = 350

        top5 = 0
        i = 0
        #Silmukka joka tulostaa 5 parasta tulosta
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
    #paria nappia jolla voi selata, muutama lista jossa on tekstiä
    next_page = button(width/2, height/2+150, 'Next')
    prev_page = button(width/2-120, height/2+150, 'Prev')

    credits_list = ['This game was created as a school project', 'by the following ICT students at Sasky Tampere.','Pekka Hautala','Konsta Karapalo',
    'Dmitry Petrov','Special Thanks to','Python code consulting', 'Marko Ollila']
    enemy_list = ['Enemy ships:', 'wuhu','https://opengameart.org/content/spaceships-1','MillionthVector','https://opengameart.org/content/pack-spaceships-and-building']
    player_list = ['Player ship:', 'xavier4321', 'https://opengameart.org/content/parts2-art-space-ships']
    bg_list = ['Backgrounds:', 'http://clipart-library.com/clipart/1071652.htm', 'http://clipart-library.com/clipart/space.htm']
    sound_list = ['Music:', 'Cleyton Kauffman', 'https://opengameart.org/content/rpg-battle-theme-ii', 'Player shot:', 'Michel Baradari',
    'https://opengameart.org/content/4-projectile-launches']
    common_list = 'All links are available in notepad'
    page_num = 1

    while True:
        window.blit(background_1,(0,0))
        common_lable = main_font.render(common_list,1,(20,255,0))
        window.blit(common_lable,(width/2-(common_lable.get_width()/2),height/2+130))
        rows = 150
        #Riippuen siitä painetaanko seuraava tai edellinen tulostetaan oikea sivu.
        # Kun sivu vaihtuu, tulostetaan listasta tekstiä. rows ovat siellä selkeyden vuoksi, on helpompaa erotella otsikot ja nimet
        if page_num == 1:
            for item in credits_list:
                tempLable = main_font.render(f"{item}",1,(255,42,42))
                window.blit(tempLable,(width/2-(tempLable.get_width()/2),rows))
                if rows == 170 or rows == 250 or rows == 310:
                    rows += 40
                else:
                    rows += 20       
        if page_num == 2:
            for item in enemy_list:
                tempLable = main_font.render(f"{item}",1,(255,42,42))
                window.blit(tempLable,(width/2-(tempLable.get_width()/2),rows))
                if rows == 150 or rows == 210:
                    rows += 40
                else:
                    rows += 20
        if page_num == 3:
            for item in player_list:
                tempLable = main_font.render(f"{item}",1,(255,42,42))
                window.blit(tempLable,(width/2-(tempLable.get_width()/2),rows))
                if rows == 150:
                    rows += 40
                else:
                    rows += 20
        if page_num == 4:
            for item in bg_list:
                tempLable = main_font.render(f"{item}",1,(255,42,42))
                window.blit(tempLable,(width/2-(tempLable.get_width()/2),rows))
                if rows == 150:
                    rows += 40
                else:
                    rows += 20
        if page_num == 5:
            for item in sound_list:
                tempLable = main_font.render(f"{item}",1,(255,42,42))
                window.blit(tempLable,(width/2-(tempLable.get_width()/2),rows))
                if rows == 150 or rows == 210:
                    rows += 40
                else:
                    rows += 20

        if page_num != 5:
            if next_page.draw_button():
                page_num += 1
        if page_num != 1:
            if prev_page.draw_button():
                page_num -= 1


        if back_button.draw_button():
            return

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
        pygame.display.update()
    
#Päävalikko    
def main_menu():
    run = True
    #Silmukan siällä luodaan nappeja jotka johtaa eri menuihin tai pelin sisään.
    while run:

        window.blit(background_1,(0,0))

        if play_button.draw_button():
            main()
        if options_button.draw_button():
            options_menu()
        if score_button.draw_button():
            high_scores()
        if quit_button.draw_button():
            sys.exit()


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        pygame.display.update()

main_menu()

#EOF
