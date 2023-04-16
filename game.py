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
		pg.init()
		# Traitement des parametres
		if BORDERLESS:
			flags = pg.NOFRAME | pg.SCALED
		else:
			flags = pg.SCALED
		self.screen 	 = pg.display.set_mode((width, height),flags,vsync=1)
		
		# Load Icon Image
		surf_ico = pg.image.load(ICON).convert_alpha()
		
		pg.display.set_icon(surf_ico)
		pg.display.set_caption(TITLE)
		pg.mouse.set_visible(MOUSE_VISIBLE)

		self.clock		 = pg.time.Clock() 
		# indice 0 la Key associée, indice 1 la valeur de la direction associé sur l'axe y  
		self.keys 		 = ((P1_UP,-1),
							(P1_DOWN,1),
							(P2_UP,-1),
							(P2_DOWN,1)
						   )		 
		# utilisé pour sortir du jeu
		self.running = True
		
		# Load sounds
		self.ballhitbat	 = pg.mixer.Sound(BALL_HIT_BAT)
		self.ballhitwall = pg.mixer.Sound(BALL_HIT_WALL)
		self.balllost	 = pg.mixer.Sound(BALL_LOST)

		# Load Fonts
		# font for score
		self.font = pg.font.Font(FONT1,FONT_SIZE)
		# font for other stuff
		self.font2 = pg.font.Font(FONT2,FONT_SIZE2)
		
		# Gamestates
		self.gamestate 		= GameState.pause
		self.key_released 	= True

		# FONTS
		# pause
		self.fnt_pause		 = self.font2.render(TXT_PAUSE,False,C_DARKGREY)
		# play after pause
		self.fnt_play		 = self.font2.render(TXT_PLAY,False,C_DARKGREY)
		# Gameover
		self.fnt_winner	 	 = None
		# Winners
		self.left_win		 = self.font2.render(TXT_L_PLAYER_WIN,False,C_WHITE)
		self.right_win		 = self.font2.render(TXT_R_PLAYER_WIN,False,C_WHITE)
		
		# restart
		self.fnt_restart	 = self.font2.render(TXT_RESTART,False,C_WHITE)

		self.__start()
		

	def __start(self):
		
		self.vline 		 	= pg.Rect((SCR_W - LINE_WIDTH)/2, LINE_MIN, LINE_WIDTH, SCR_H - (LINE_MIN * 2))
		self.ball 			= pg.Rect(BALL_X,BALL_Y,BALL_W,BALL_H)
		self.balldx		 	= random.choice(Game.choices)
		 
		self.ballangle	 	= BALL_MAX_ANGLE
		self.batl 		 	= pg.Rect(BATL_X,BATL_Y,BAT_W,BAT_H)
		self.batr 		 	= pg.Rect(BATR_X,BATR_Y,BAT_W,BAT_H)
		
		# Scores
		self.lscore		 	= 0
		self.rscore		 	= 0
		
		
		self.__init()
		

	def __init(self):
		
		self.vx_norm = TRIG_ANGLE_START  # angle de depart 45 degrés
		self.vy_norm = TRIG_ANGLE_START  # angle de depart 45 degrés
		
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

		# scores
		self.fnt_lscore		 = self.font.render(str(self.lscore),False,C_WHITE)
		self.fnt_rscore		 = self.font.render(str(self.rscore),False,C_WHITE)

	def run(self):
		while self.running:
			self.dt = self.clock.tick(FPS)/1000.0
			self._update()
			self._draw()
			pg.display.update()
		pg.quit()
	
	def _update(self):
		self._check_Events()
		if self.gamestate == GameState.run:
			# deplacement des raquettes
			self.__move_bats()
			# test collisions ball bats
			self.__manage_collisions()
			# deplacement de la balle
			self.__move_ball()
		
		elif self.gamestate == GameState.pause:    # Pause
			pass
		elif self.gamestate == GameState.gameover: # GameOver
			pass
			
	
	def _draw(self):
		self.screen.fill(C_BLACK)
		Game.__drawscores(self.screen,self.fnt_lscore,self.fnt_rscore)
		Game.__draw_alternate_lines_in_obj(self.screen,self.vline, round(self.vline.height / VLINE_NB_SEGMENTS), C_GREY,C_BLACK)
		Game.__draw_alternate_lines_in_obj(self.screen,self.vline, 1, C_BLACK)
		
		if self.gamestate == GameState.run or self.gamestate == GameState.pause:
			Game.__draw_alternate_lines_in_obj(self.screen,self.ball, THICKNESS, C_WHITE, C_BLACK)
			Game.__draw_alternate_lines_in_obj(self.screen,self.batl, THICKNESS, C_WHITE, C_BLACK)
			Game.__draw_alternate_lines_in_obj(self.screen,self.batr, THICKNESS, C_WHITE, C_BLACK)
		if self.gamestate == GameState.pause:
			self._draw_pause()
		elif self.gamestate == GameState.gameover:
			self._draw_gameover()
		
	def _check_Events(self):
		# check events
		for event in pg.event.get():
			if event.type == pg.QUIT: # Croix de fermeture
				self.running=False
				return	
			if event.type == pg.KEYUP:  # lorque les touches raquettes sont relachées
				for i in range(0,len(self.keys)):
					if event.key == self.keys[i][0]:
						self.batspeeddec[int(i/2)] = True

		
		keys = pg.key.get_pressed()
		if keys[EXIT_PRG]:  # Touche ECHAP Pressée
			self.running = False
			return

		self.key_pause_pressed = keys[PAUSE]
		if self.key_pause_pressed: 
			if self.key_released:   		  # Key released
				self.key_released = False
				if self.gamestate == GameState.run:
					self.gamestate = GameState.pause
				elif self.gamestate == GameState.pause:
					self.gamestate = GameState.run
				elif self.gamestate == GameState.gameover:
					self.gamestate = GameState.run
					self.__start()
		else: 
			self.key_released = True
							
		

	def _draw_pause(self):
		Game.__drawstate(self.screen,self.fnt_pause, self.fnt_play)

	def _draw_gameover(self):
		Game.__drawstate(self.screen,self.fnt_winner, self.fnt_restart)
				

	def __move_bats(self):
		
		# gestion acceleration des bats (on appuie sur une touche)
		keys = pg.key.get_pressed()
		for i in range(0,len(self.keys)):
			if keys[self.keys[i][0]]:
				self.batdirs[int(i/2)] = self.keys[i][1]
				self.batspeeddec[int(i/2)] = False
				self.tweenspeed[int(i/2)] = math.sqrt(self.tweenspeed[int(i/2)])
				if self.tweenspeed[int(i/2)] > TWEEN_MAX:
					self.tweenspeed[int(i/2)] = TWEEN_MAX
			
		# gestion de la deceleration des bats (on a relaché une touche)
		for i in range(0,len(self.batspeeddec)):
			if self.batspeeddec[i]:
				self.tweenspeed[i] /= 3
				if self.tweenspeed[i] < TWEEN_MIN:
					self.tweenspeed[i] = TWEEN_MIN
					self.batdirs[i] = 0		
		
		for i in range (0,len(self.speedbat_frame_dy)):
			self.speedbat_frame_dy[i]=self.dt * SPD_BAT * self.batdirs[i] * self.tweenspeed[i]

		self.batl.y += self.speedbat_frame_dy[0]
		self.batr.y += self.speedbat_frame_dy[1]
			
		self.batl.y = Game.clamp(self.batl.y,SPC_Y,SCR_H - self.batl.height - SPC_Y)
		self.batr.y = Game.clamp(self.batr.y,SPC_Y,SCR_H - self.batr.height - SPC_Y)
	

	def __move_ball(self):
		 
		if self.ball.y < 0 or self.ball.y > SCR_H - self.ball.height:
			pg.mixer.Sound.play(self.ballhitwall)
			self.vy_norm = abs(self.vy_norm)
			if self.ball.y < 0:
				self.ball.y = 0
				self.balldy = 1
			elif self.ball.y > SCR_H - self.ball.height:
				self.ball.y = SCR_H - self.ball.height
				self.balldy = -1
			
			
		if self.ball.x < (self.batl.x - self.ball.width): # joueur droite gagne
			pg.mixer.Sound.play(self.balllost)
			self.balldx = -1
			self.rscore += 1
			if self.rscore >= MAX_SCORE:
				self.rscore = MAX_SCORE
				self.gamestate = GameState.gameover
				self.fnt_winner = self.right_win
				self.fnt_rscore	  = self.font.render(str(self.rscore),False,C_WHITE)
				return
				
			else:
				self.__init()
		
		elif self.ball.x > (self.batr.right + self.ball.width):  # joueur gauche gagne
			pg.mixer.Sound.play(self.balllost)
			self.balldx = 1
			self.lscore += 1
			if self.lscore >= MAX_SCORE:
				self.lscore = MAX_SCORE
				self.gamestate = GameState.gameover
				self.fnt_winner = self.left_win
				self.fnt_lscore	  = self.font.render(str(self.lscore),False,C_WHITE)
				return
				
			else:
				self.__init()

		# UPD ball position
		self.ball.x += SPD_BALL * self.dt * self.balldx * self.vx_norm
		self.ball.y += SPD_BALL * self.dt * self.balldy * self.vy_norm
		
	
	def __manage_collisions(self):
		# collide with bats
		if pg.Rect.colliderect(self.ball,self.batl): # left bat
			
			pg.mixer.Sound.play(self.ballhitbat)
			self.balldx = 1
			self.ball.x = self.batl.right
			self.vx_norm, self.vy_norm = Game.__calc_result_angles(self.batl,self.ball,self.balldy)
			

		elif pg.Rect.colliderect(self.ball,self.batr): # right bat
			
			pg.mixer.Sound.play(self.ballhitbat)
			self.balldx = -1
			self.ball.x = self.batr.x - self.ball.width
			self.vx_norm, self.vy_norm = Game.__calc_result_angles(self.batr,self.ball,self.balldy)


	@staticmethod	
	def __draw_alternate_lines_in_obj(scr, obj, thickness, color1, color2=False):
		alt=0
		for i in range(0,obj.height,thickness):
			alt = alt^1	 
			if alt==0:
				pg.draw.rect(scr,color1,pg.Rect(obj.x,obj.y + i,obj.width, thickness))
			else:
				if color2:
					pg.draw.rect(scr,color2,pg.Rect(obj.x,obj.y + i,obj.width, thickness))

	@staticmethod
	def __drawscores(scr,fntscore_l,fntscore_r):
		xr = BATR_X - BAT_W - fntscore_r.get_width()
		xl = round(SCR_W / 3.3)
		
		rect_xr = pg.Rect(xr,SCR_H/20,fntscore_r.get_width(),fntscore_r.get_height())
		rect_xl = pg.Rect(xl,SCR_H/20,fntscore_l.get_width(),fntscore_l.get_height())

		scr.blit(fntscore_r,(xr,SCR_H/RATIO_START_V))
		scr.blit(fntscore_l,(xl,SCR_H/RATIO_START_V))

		Game.__draw_alternate_lines_in_obj(scr,rect_xr,THICKNESS,C_BLACK)
		Game.__draw_alternate_lines_in_obj(scr,rect_xl,THICKNESS,C_BLACK)
	
	@staticmethod
	def __drawstate(scr,fnt_text,fnt_next):
		xt = round((SCR_W - fnt_text.get_width()) / 2)
		yt = round((SCR_H - fnt_text.get_height()) / 2)

		rect_t = pg.Rect(xt,yt,fnt_text.get_width(),fnt_text.get_height())
		scr.blit(fnt_text,(xt,yt))
		Game.__draw_alternate_lines_in_obj(scr,rect_t,THICKNESS,C_BLACK)

		xt = round((SCR_W - fnt_next.get_width()) / 2)
		yt += fnt_next.get_height() + 8
		rect_t = pg.Rect(xt,yt,fnt_next.get_width(),fnt_next.get_height())
		scr.blit(fnt_next,(xt,yt))
		Game.__draw_alternate_lines_in_obj(scr,rect_t,THICKNESS,C_BLACK)

	@staticmethod
	def __calc_result_angles(objbat, objball, objballdy):
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
		angleres = angleres * MIN_ANGLE_RAD # conversion en radians
		norm_vx = abs(math.cos(angleres)) 
		norm_vy = math.sin(angleres) * objballdy
		return norm_vx, norm_vy
		