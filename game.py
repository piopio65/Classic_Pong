from constants import *
from readcfg import *
import random
import math
import time

class Game():
	
	clamp = lambda value, minv, maxv: max(min(value, maxv), minv)
	choices = (-1,1,-1,1,-1,1)
	lost = False

	def __init__(self,width=SCR_W,height=SCR_H):
		random.seed(time.time() *1000)
		py.init()
		# Traitement des parametres
		if BORDERLESS:
			flags = py.NOFRAME | py.SCALED
		else:
			flags = py.SCALED

		#self.screen 	 = py.display.set_mode((width, height),py.NOFRAME,py.SCALED,vsync=1)
		self.screen 	 = py.display.set_mode((width, height),flags,vsync=1)
		
		# Load Icon Image
		surf_ico = py.image.load(ICON).convert_alpha()
		
		py.display.set_icon(surf_ico)
		py.display.set_caption(TITLE)
		
		self.clock		 = py.time.Clock() 
		# indice 0 la Key associée, indice 1 la valeur de la direction associé sur l'axe y  
		self.keys 		 = ((P1_UP,-1),
							(P1_DOWN,1),
							(P2_UP,-1),
							(P2_DOWN,1)
						   )		 
		# utilisé pour sortir du jeu
		self.running = True
		
		# Load sounds
		self.ballhitbat	 = py.mixer.Sound(BALL_HIT_BAT)
		self.ballhitwall = py.mixer.Sound(BALL_HIT_WALL)
		self.balllost	 = py.mixer.Sound(BALL_LOST)

		# Load Font
		self.font = py.font.Font(FONT1,FONT_SIZE)
		
		self.__start()
		

	def __start(self):
		# 1er indice dy player 1,  2eme indice dy player 2, vitesses de deplacements en Y
		self.vline 		 = py.Rect((SCR_W - LINE_WIDTH)/2, LINE_MIN, LINE_WIDTH, SCR_H - (LINE_MIN * 2))
		self.ball 		 = py.Rect(BALL_X,BALL_Y,BALL_W,BALL_H)
		self.balldx		 = random.choice(Game.choices)
		 
		self.ballangle	 = BALL_MAX_ANGLE
		self.batl 		 = py.Rect(BATL_X,BATL_Y,BAT_W,BAT_H)
		self.batr 		 = py.Rect(BATR_X,BATR_Y,BAT_W,BAT_H)
		
		# Scores
		self.lscore		 = 0
		self.rscore		 = 0
		
		# lwin True si joueur gauche gagne 
		# rwin True si joueur droit gagne
		#
		self.lwin		 = False
		self.rwin		 = False
		# debug
		self.tic = False
		self.__init()
		

	def __init(self):
		
		self.x_angle = TRIG_ANGLE_START  # angle de depart 45 degrés
		self.y_angle = TRIG_ANGLE_START  # angle de depart 45 degrés
		
		self.balldy  = random.choice(Game.choices)
		
		if self.balldx < 0:
			self.ball.x = self.batr.x - self.ball.width
			self.ball.y = self.batr.centery
		else:
			self.ball.x = self.batl.right 
			self.ball.y = self.batl.centery
		

		self.speedbat_frame_dy = [0,0]  # instant speed bat / frame  ind0 : left player, ind1: right player
		self.batdirs		   = [0,0]	# dirs for each bat -1:up, 0:stop, 1:down   ind0 : left player, ind1: right player
		self.tweenspeed		   = [TWEEN_MIN,TWEEN_MIN]
		self.batspeeddec	   = [False,False]

		self.fnt_lscore		 = self.font.render(str(self.lscore),False,C_WHITE)
		self.fnt_rscore		 = self.font.render(str(self.rscore),False,C_WHITE)


	def run(self):
		
		while self.running:
			self.dt = self.clock.tick(FPS)/1000.0
			self.screen.fill(C_BLACK)
			self.__update()
			self.__draw()
			py.display.update()
		
		py.quit()
	
	def __moveball(self):
		 
		if self.ball.y < 0 or self.ball.y > SCR_H - self.ball.height:
			py.mixer.Sound.play(self.ballhitwall)
			self.y_angle = abs(self.y_angle)
			if self.ball.y < 0:
				self.ball.y = 0
				self.balldy = 1
			elif self.ball.y > SCR_H - self.ball.height:
				self.ball.y = SCR_H - self.ball.height
				self.balldy = -1
			
			
		if self.ball.x < (self.batl.x - self.ball.width): # joueur droite gagne
			py.mixer.Sound.play(self.balllost)
			#Game.lost = True
			self.balldx = -1
			self.rscore += 1
			if self.rscore >= MAX_SCORE:
				self.rscore = MAX_SCORE
				self.__start()
			else:
				self.__init()
		
		elif self.ball.x > (self.batr.right + self.ball.width):  # joueur gauche gagne
			py.mixer.Sound.play(self.balllost)
			#Game.lost = True
			self.balldx = 1
			self.lscore += 1
			if self.lscore >= MAX_SCORE:
				self.lscore = MAX_SCORE
				self.__start()
			else:
				self.__init()

		
	def __manage_collisions(self):
		# collide with bats
		if py.Rect.colliderect(self.ball,self.batl):
			
			py.mixer.Sound.play(self.ballhitbat)
			self.balldx = 1
			self.ball.x = self.batl.right
			self.x_angle, self.y_angle = Game.__calc_result_angles(self.batl,self.ball,self.balldy)
			

		elif py.Rect.colliderect(self.ball,self.batr):
			
			py.mixer.Sound.play(self.ballhitbat)
			self.balldx = -1
			self.ball.x = self.batr.x - self.ball.width
			self.x_angle, self.y_angle = Game.__calc_result_angles(self.batr,self.ball,self.balldy)
		
	
	def __update(self):
		
		# gestion des events
		for event in py.event.get():
			
			if event.type == py.QUIT: # croix de fermeture
				self.running = False
			elif event.type == py.KEYDOWN:
				if event.key == EXIT_PRG: # ESC
					self.running = False
			
			elif event.type == py.KEYUP:  # lorque les touches raquettes sont relachés
				for i in range(0,len(self.keys)):
					if event.key == self.keys[i][0]:
						self.batspeeddec[int(i/2)] = True
						
		#RAZ speed bat for left player and right player
		#for i in range(0,len(self.speedbat_frame_dy)):
		#	self.speedbat_frame_dy[i]=0
		

		# gestion de la deceleration des bats (on a relaché une touche)
		for i in range(0,len(self.batspeeddec)):
			if self.batspeeddec[i]:
				self.tweenspeed[i] = pytweening.easeInExpo(self.tweenspeed[i])
				if self.tweenspeed[i] < TWEEN_MIN:
					self.tweenspeed[i] = TWEEN_MIN
					self.batdirs[i] = 0

		# gestion acceleration des bats (on appuie sur une touche)
		keys = py.key.get_pressed()
		for i in range(0,len(self.keys)):
			if keys[self.keys[i][0]]:
				self.batdirs[int(i/2)] = self.keys[i][1]
				self.batspeeddec[int(i/2)] = False
				self.tweenspeed[int(i/2)] = pytweening.easeOutExpo(self.tweenspeed[int(i/2)])
				if self.tweenspeed[int(i/2)] > TWEEN_MAX:
					self.tweenspeed[int(i/2)] = TWEEN_MAX

				
		
		for i in range (0,len(self.speedbat_frame_dy)):
			#self.speedbat_frame_dy[i]=self.dt * SPD_BAT * self.speedbat_frame_dy[i]
			self.speedbat_frame_dy[i]=self.dt * SPD_BAT * self.batdirs[i] * self.tweenspeed[i]

		self.batl.y += self.speedbat_frame_dy[0]
		self.batr.y += self.speedbat_frame_dy[1]
		
		self.batl.y = Game.clamp(self.batl.y,SPC_Y,SCR_H - self.batl.height - SPC_Y)
		self.batr.y = Game.clamp(self.batr.y,SPC_Y,SCR_H - self.batr.height - SPC_Y)

		# deplacement de la balle
		self.__moveball()
		# test collisions ball bats
		self.__manage_collisions()
		
		# MAJ positions
		self.ball.x += SPD_BALL * self.dt * self.balldx * self.x_angle
		self.ball.y += SPD_BALL * self.dt * self.balldy * self.y_angle

	def __draw(self):
		#py.display.set_caption("fps: " + str(self.clock.get_fps()))
		Game.__drawscores(self.screen,self.fnt_lscore,self.fnt_rscore)
		Game.__draw_alternate_lines_in_obj(self.screen,self.vline, round(self.vline.height / VLINE_NB_SEGMENTS), C_GREY,C_BLACK)
		Game.__draw_alternate_lines_in_obj(self.screen,self.vline, 1, C_BLACK)
		Game.__draw_alternate_lines_in_obj(self.screen,self.batl, THICKNESS, C_WHITE, C_BLACK)
		Game.__draw_alternate_lines_in_obj(self.screen,self.batr, THICKNESS, C_WHITE, C_BLACK)
		Game.__draw_alternate_lines_in_obj(self.screen,self.ball, THICKNESS, C_WHITE, C_BLACK)
		
	
	@staticmethod	
	def __draw_alternate_lines_in_obj(scr, obj, thickness, color1, color2=False):
		alt=0
		for i in range(0,obj.height,thickness):
			alt = alt^1	 
			if alt==0:
				py.draw.rect(scr,color1,py.Rect(obj.x,obj.y + i,obj.width, thickness))
			else:
				if color2:
					py.draw.rect(scr,color2,py.Rect(obj.x,obj.y + i,obj.width, thickness))

	@staticmethod
	def __drawscores(scr,fntscore_l,fntscore_r):
		xr = BATR_X - BAT_W - fntscore_r.get_width()
		xl = round(SCR_W / 3.3)
		
		rect_xr = py.Rect(xr,SCR_H/20,fntscore_r.get_width(),fntscore_r.get_height())
		rect_xl = py.Rect(xl,SCR_H/20,fntscore_l.get_width(),fntscore_l.get_height())

		scr.blit(fntscore_r,(xr,SCR_H/RATIO_START_V))
		scr.blit(fntscore_l,(xl,SCR_H/RATIO_START_V))

		Game.__draw_alternate_lines_in_obj(scr,rect_xr,THICKNESS,C_BLACK)
		Game.__draw_alternate_lines_in_obj(scr,rect_xl,THICKNESS,C_BLACK)

	
	@staticmethod
	def __calc_result_angles(objbat, objball, objballdy,minangle=2):
		'''
			Calcul des valeurs sur x et y de l'angle calculé lors d'une colision
			ball bat 
			p1 : un objet raquette
			p2 : un objet ball
			p3 : l'objet objballdy
		'''
		dist = objball.centery - objbat.centery
		angleres = (dist / (BAT_H/2)) * BALL_MAX_ANGLE # Angle resultant en degrés
		angleres += random.uniform(-ANGLE_RANDOM_RANGE,ANGLE_RANDOM_RANGE)
		
		#print(f"angleres: {angleres}")
	
		angleres = angleres * MIN_ANGLE_RAD # conversion en radians
		x_angle = abs(math.cos(angleres)) 
		y_angle = math.sin(angleres) * objballdy
		return x_angle, y_angle
		
		
		