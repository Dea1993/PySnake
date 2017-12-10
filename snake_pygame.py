#!/usr/bin/env python2
#Sviluppatore: Andrea De Angelis - Dea1993
#sito internet http://deasproject.altervista.org

import pygame, sys, random, time, pickle, platform, numpy, os.path, py_compile
from pygame.locals import *
pygame.init()

#@@@@@SETUP@@@@@#
# compilazione del sorgente, generando il file .pyc
py_compile.compile('snake_pygame.py')

#imposto fps
FPS = 60
fpsClock = pygame.time.Clock()

#imposto font dei caratteri
font = pygame.font.Font(None, 24)
font2 = pygame.font.Font(None, 128)
#imposto valore del volume di default
volume = 0.2

#inizializzo colori che andro' ad usare nel gioco
BIANCO = (255, 255, 255)
VERDE = (0, 200, 0)
VERDE_SCURO = (0, 100 , 0)

#assegno alle 2 variabili le dimensioni che deve assumere la finestra
size_w = 555		#larghezza
size_h = 404		#altezza

#imposto dimensioni e nome finestra
surface = pygame.display.set_mode((size_w, size_h))
pygame.display.set_caption('snake 0.7.3')

#carico tutte le immagini che usero' nel gioco
sfondo = pygame.image.load("Immagini/sfondo.png")					#immagine di sfondo
gameover_img = pygame.image.load("Immagini/gameover.png")			#immagine per il gameover
nuovo_record = pygame.image.load("Immagini/nuovo_record.png")		#immagine per nuovo record
mela = pygame.image.load("Immagini/mela.png")						#immagine della mela
teschio = pygame.image.load("Immagini/teschio.png")				#immagine del teschio
dimezza = pygame.image.load("Immagini/dimezza_coda.png")			#immagine del bonus dimezza coda
pausa_img = pygame.image.load("Immagini/pausa.png")				#immagine schermata di pausa
icona = pygame.image.load('Immagini/snake_pygame-icon.png')			#immagine dell'icona del gioco

#imposto icona del gioco
pygame.display.set_icon(icona)

#creo il serpente
snake = pygame.Surface((14, 14))			#creo un quadrato (14x14) snake che sara' il corpo del serpente
snake_testa = pygame.Surface((14, 14))	#snake_testa e' la testa del serpente, la differenzio dal corpo per potergli assegnare un colore diverso
snake.fill(VERDE_SCURO)					#coloro di verde scuro il corpo del serpente
snake_testa.fill(VERDE)					#coloro di verde chiaro la testa del serpente

OS = platform.system()		#guardo il sistema operativo

if OS == "Linux":
	from xdg import BaseDirectory
	path_data = BaseDirectory.save_config_path('snake_pygame/')	#imposto il path per il file del record	

	#se la cartella del gioco contenente il record non esiste la creo e creo anche il file record.txt impostando il record a 0
	if not os.path.exists(path_data):
		#la cartella non esiste
		os.mkdir(path_data)								#creo la cartella

elif OS == "Windows":
	path_data = os.path.expanduser("~\\")+"snake_pygame\\"

	if not os.path.exists(path_data):
		#la cartella non esiste
		os.mkdir(path_data)

else:		#per gli altri sistemi operativi crea la cartella record all'interno della cartella di gioco
	path_data = ("Record/")
	
	if not os.path.exists(path_data):
		#la cartella non esiste
		os.mkdir(path_data)

#@@@@@INIZIALIZZAZIONI FUNZIONI@@@@@#

#qui ci sono le variabili che devono essere inizializzate all'inizio del programma e dopo il restart
def inizializzazione():
	global volume, punti, snake_x, snake_y, min, max_x, max_y, direzione, direzione_precedente, difficolta, record, bonus_icon, bonus_x, bonus_y, spostamento_effettuato
	
	try:
		record_file = open(path_data+"record.txt","r")		#apro il file record.txt in sola lettura e lo assegno alla variabile record
	except:
		record_file = open(path_data+"record.txt","w")		#se il file record.txt non esiste lo creo assegnando il record a 0
		record_file.write("0")
		record_file.close()
		record_file = open(path_data+"record.txt","r")
		
	record = int(record_file.read())					#apro il file e leggo il miglior punteggio
	record_file.close()		#chiudo il file precedentemente aperto
	punti = 0										#punti iniziali del giocatore
	snake_x = [180, 165, 150, 135, 120, 105]			#creo il serpente 6 blocchi iniziali distanziati di 15px l'uno dall'altro
	snake_y = [180]*6								#assegno al serpente le stesse coordinate in altezza
	min = 30										#limite minimo dello spazio usabile dal serpente
	max_x = 525									#limite massimo dello spazio usabile dal serpente in larghezza
	max_y = 375									#limite massimo dello spazio usabile dal serpente in altezza
	direzione_precedente = direzione = 'destra'			#direzione di default in cui si muove il serpente, la variabile "direzione_precedente" serve per ricordare quale era il verso prima di mettere in pausa il gioco
	difficolta = 0.05								#velocita' iniziale del serpente
	genera_oggetti(snake_x[0],snake_y[0])				#chiamo la funzione che genera tutti gli oggetti sullo schermo
	bonus_icon = '0'
	bonus_x = bonus_y = 800
	spostamento_effettuato = '0'
	pygame.mixer.music.load("Sound/music.ogg")		#carico il file audio
	pygame.mixer.music.set_volume(volume)			#regolo il volume del file audio (va da 0.0 a 1.0)
	pygame.mixer.music.play(-1)						#eseguo il file in modalita' loop

		
#funzione che genera gli oggetti
def genera_oggetti(snake_x, snake_y):
	global mela_x, mela_y, teschio_x, teschio_y, bonus_x, bonus_y		#esporto le variabili per renderle usabili anche al di fuori della funzione

	#genero casualmente le coordinate della mela e del teschio indicando i limiti minimi e massimi
	#l'algoritmo che ho usato fa in modo che la mela e il serpente, vengano generati nella stessa linea del serpente
	#perche' il serpente fa movimenti di 15pixel, quindi l'operazione 15*(min/15) e' uguale a 30 e questa e' la coordinata minina che possono assumere la mela o il teschio
	#invece l'operazione 15*((max_x/15)-1) e' uguale a 510 e questa e' la coordinata massima che il teschio e la mela possono assumere, essendo gli oggetti grandi 15px, 
	#sono costretto a mettere come coordinate massime di spawn 15px in meno, perche' altrimenti uscirebbe fuori dal campo di gioco
	mela_x = 15*(random.randint((min/15), ((max_x/15)-1)))		
	mela_y = 15*(random.randint((min/15), ((max_y/15)-1)))
	teschio_x = 15*(random.randint((min/15), ((max_x/15)-1)))
	teschio_y = 15*(random.randint((min/15), ((max_y/15)-1)))
	
	#adesso verifico che il teschio non spawna troppo vicino al serpente per evitare di morire inevitabilmente
	while ( ((teschio_x >= snake_x-90 and teschio_x <= snake_x+90) and (teschio_y >= snake_y-90 and teschio_y <= snake_y+90)) or (teschio_x == mela_x and teschio_y == mela_y) ):
		teschio_x = 15*(random.randint((min/15), ((max_x/15)-1)))
		teschio_y = 15*(random.randint((min/15), ((max_y/15)-1)))
	
	genera_num = random.randint(1, 40)			#genero un numero tra 1 e 40 se esce 1 allora faccio comparire il bonus
	if genera_num == 1:
		bonus_x = 15*(random.randint((min/15), ((max_x/15)-1)))
		bonus_y = 15*(random.randint((min/15), ((max_y/15)-1)))
		
		while ((bonus_x == teschio_x and bonus_y == teschio_y) or (bonus_x == mela_x and bonus_y == mela_y)):
			bonus_x = 15*(random.randint((min/15), ((max_x/15)-1)))
			bonus_y = 15*(random.randint((min/15), ((max_y/15)-1)))
	else:
		bonus_x = bonus_y = 800

#funzione che visualizza gli oggetti a schermo
def mostra():
	global direzione
		
	punteggio = font.render('Punteggio: %d' % (punti), True, BIANCO)
	highscore = font.render('Record: %d' % (record), True, BIANCO)
	vol = font.render('Volume: %d' % (volume*5), True, BIANCO)
	bonus = font.render('Bonus: [      ]', True, BIANCO)
	surface.blit(sfondo, (0, 0))	
	surface.blit(punteggio, (30, 8))
	surface.blit(highscore, (430, 8))
	surface.blit(vol, (30, 382))
	surface.blit(bonus, (430, 382))
	
	for i in range(1,len(snake_x)):					#mostro tutti i blocchi del corpo dello snake
		surface.blit(snake, (snake_x[i], snake_y[i]))
	surface.blit(snake_testa, (snake_x[0], snake_y[0]))	#mostro la testa dello snake
	
	surface.blit(mela, (mela_x, mela_y))				#mostro la mela
	surface.blit(teschio, (teschio_x, teschio_y))			#mostro il teschio
	surface.blit(dimezza, (bonus_x, bonus_y))
	if bonus_icon == '1':							#se ho preso il bonus allora mostro l'icona
		surface.blit(dimezza, (500, 384))
	
	pygame.display.update()							#aggiorno tutto
	fpsClock.tick(FPS)


#funzione che salva il nuovo record all'interno dell'apposito file
def scrivi():
	record_file = open(path_data+"record.txt","w")		#apro il file record.txt in sola scrittura e lo assegno alla variabile record
	record_file.write(str(int(punti)))					#converto la variabile "punti" in stringa e scrivo il contenuto nel file record.txt
	record_file.close()							#chiudo il file precedentemente aperto
	
	surface.blit(nuovo_record, (0, 0))				#mostro la schermata di gameover
	pygame.display.update()						#aggiorno lo schermo
	
	for event in pygame.event.get():				#controllo la pressione del tasto
		if event.key == K_r:						#se premo "r" chiama la funzione inizializzazione()
			inizializzazione()
		elif event.key == K_ESCAPE:				#se premo "ESC" vai alla funzione game_over()
			game_over()

#funzione che mostra la schermata di pausa
def pausa():
	surface.blit(pausa_img, (0, 0))				#mostro la schermata di pausa
	pygame.display.update()						#aggiorno lo schermo

#CHIEDO SE SI VUOLE RICOMINCIARE IL GIOCO
def restart():
	pygame.mixer.music.stop()						#interrompo il file audio
	
	#controllo se l'attuale punteggio e' piu' alto dell'attuale record
	if punti > record:
		scrivi()		#se entro dentro a questo if significa che ho fatto un nuovo record quindi chiamo l'apposita funzione
	else:
		surface.blit(gameover_img, (0, 0))		#mostro la schermata di gameover
		pygame.display.update()				#aggiorno lo schermo
		for event in pygame.event.get():		#controllo la pressione del tasto
			if event.type == QUIT:			#se viene premuto il tasto chiudi della finestra, vai alla funzione game_over()
				game_over()
		
			#controllo quali tasti vengono premuti
			elif event.type == KEYDOWN:
				if event.key == K_r:				#se premo "r" chiama la funzione inizializzazione()
					inizializzazione()
				elif event.key == K_ESCAPE:		#se premo "ESC" vai alla funzione game_over()
					game_over()
	
#questa funzione chiude pygame e tutti i moduli caricati
def game_over():
	pygame.quit()
	sys.exit()


#INIZIO PROGRAMMA
inizializzazione()			#chiamo la funzione per inizializzare tutte le variabili

while True:
	#controllo in base ai punti raggiunti quale livello di difficolta' (velocita' di aggiornamento immagine) devo settare
	if punti < 10:
		difficolta = 0.07
	elif punti < 30:
		difficolta = 0.06
	elif punti < 50:
		difficolta = 0.05
	elif punti < 80:
		difficolta = 0.04
	elif punti > 80:
		difficolta = 0.035
	
	incremento_punti = 1+round(punti*difficolta)		#algoritmo per l'incremento del punteggio, la funziona round arrotonda il numero togliendo la parte dopo la virgola
	
	time.sleep(difficolta)	#e' il tempo che trascorre prima di mostrare il nuovo frame (piu' il tempo e' basso maggiore e' la velocita')
	
	mostra()				#chiamo la funzione che mostra gli elementi a schermo
	
	for event in pygame.event.get():		#controllo la pressione del tasto
		if event.type == QUIT:			#se viene premuto il tasto chiudi della finestra, vai alla funzione game_over()
			game_over()
		
		#controllo quali tasti vengono premuti
		elif event.type == KEYDOWN:
			#se premo il tasto "freccia destra" o "d", e l'attuale direzione non e' "sinistra" e se non sono nella schermata di gameover, allora la nuova direzione e' "destra" (lo stesso discorso vale per gli altri if)
			if ((((event.key == K_RIGHT or event.key == K_d) and direzione != 'sinistra') and direzione != 'gameover') and direzione != '0'):
				#controllo se il serpente si e' spostato, cosi' da evitare che spostandosi velocemente prima su/giu e poi a destra, 
				#il serpente non fa in tempo a spostarsi su/giu andando di conseguenza solo a destra causando il gameover
				if spostamento_effettuato == '1':
					direzione_precedente = direzione = 'destra'
					spostamento_effettuato = '0'
					
			elif ((((event.key == K_LEFT or event.key == K_a) and direzione != 'destra') and direzione != 'gameover') and direzione != '0'):
				if spostamento_effettuato == '1':
					direzione_precedente = direzione = 'sinistra'
					spostamento_effettuato = '0'
					
			elif ((((event.key == K_DOWN or event.key == K_s) and direzione != 'su') and direzione != 'gameover') and direzione != '0'):
				if spostamento_effettuato == '1':
					direzione_precedente = direzione = 'giu'
					spostamento_effettuato = '0'
					
			elif ((((event.key == K_UP or event.key == K_w) and direzione != 'giu') and direzione != 'gameover') and direzione != '0'):
				if spostamento_effettuato == '1':
					direzione_precedente = direzione = 'su'
					spostamento_effettuato = '0'
					
			elif (event.key == K_p and direzione != 'gameover'):
				if direzione == '0':
					direzione = direzione_precedente
				else:
					direzione = '0'
			
			elif event.key == K_KP_PLUS or event.key == K_PLUS:	#controllo se viene premuto il tasto + della tastiera o del numpad
				if volume < 1.0:			
					volume += 0.2			#alzo il volume
				elif volume > 1.0:
					volume = 1.0
				pygame.mixer.music.set_volume(volume)
			
			elif event.key == K_KP_MINUS or event.key == K_MINUS:	#controllo se viene premuto il tasto - della tastiera o del numpad
				if volume > 0.0:
					volume -= 0.2			#abbasso il volume
				elif volume < 0.0:
					volume = 0.0
				pygame.mixer.music.set_volume(volume)
				
			elif event.key == K_ESCAPE:
				game_over()
				
			elif event.key == K_r:
				inizializzazione()
				
			elif (event.key == K_SPACE and  bonus_icon == '1' and direzione != 'gameover' and direzione != '0'):
				bonus_icon = '0'
				i = (len(snake_x)-1)
				meta_snake = (i / 2)
				while meta_snake < i:
					del snake_x[i]
					i -= 1
			
	
	if direzione == '0':				#se direzione e' uguale a '0' allora e' stato premuto il tasto "p" quindi vai alla funzione pausa()
		pausa()
		
	elif direzione == 'gameover':		#se direzione e' uguale a "gameover" allora ho perso quindi vai alla funzione restart()
		restart()


	#se se la variabile "direzione" non soddisfa le 2 condizioni precedenti allora si puo' continuare
	else:
		#algoritmo per lo spostamento del serpente
		i = len(snake_x)-1
		while i > 0:
			snake_x[i] = snake_x[i-1]		#il blocco del corpo prende le coordinate del blocco precedente
			snake_y[i] = snake_y[i-1]	
			i -= 1					#decremento l'indice per controllare un altro blocco
				
		#muovo il serpente in base al tasto che ho premuto
		if direzione == 'destra':
			snake_x[0] += 15					#sposto il serpente
			spostamento_effettuato = '1'		#segnalo che il serpente ha effettuato lo spostamento
		elif direzione == 'sinistra':
			snake_x[0] -= 15
			spostamento_effettuato = '1'
		elif direzione == 'giu':
			snake_y[0] += 15
			spostamento_effettuato = '1'
		elif direzione == 'su':
			snake_y[0] -= 15
			spostamento_effettuato = '1'

		i = len(snake_x)-1
		#controllo se il serpente colpisce la mela
		if snake_x[0] == mela_x and snake_y[0] == mela_y:
			punti += incremento_punti					#aggiunto un punto
			genera_oggetti(snake_x[0],snake_y[0])			#chiamo la funzione per generare gli oggetti				
			#aggiungo un nuovo blocco al corpo del serpente per allungarlo
			snake_x.append(800)
			snake_y.append(800)

		#controllo se il serpente prende l'oggetto bonus	
		if snake_x[0] == bonus_x and snake_y[0] == bonus_y:		#se colpisco l'oggetto bonus
			bonus_icon = '1'								#abilito l'icona bonus in basso a sinistra
			punti += 5+round(punti*difficolta)					#aggiunto 5 punti piu' un punteggio proporzinale alla difficolta' e i punti attuali
			genera_oggetti(snake_x[0],snake_y[0])				#rigenero gli oggetti
			bonus_x = bonus_y = 800						#faccio scomparire l'oggetto bonus dalla schermata
			snake_x.append(800)
			snake_y.append(800)
			
		#controllo se il serpente colpisce il teschio
		if snake_x[0] == teschio_x and snake_y[0] == teschio_y:
			direzione = 'gameover'
		
		#verifico se il serpente "si morde", il controllo lo faccio sopra a 4, perche' non si puo' mordere nei primi 4 blocchi, quidni non serve fare controlli inutili
		while i > 4:
			if snake_x[0] == snake_x[i] and snake_y[0] == snake_y[i]:
				direzione = 'gameover'
			i -= 1
		
		#controllo se il serpente esce dal bordo, in tal caso lo faccio uscire dal bordo opposto
		if (snake_x[0] >= max_x):
			snake_x[0] = 30
		if (snake_y[0] >= max_y):
			snake_y[0] = 30
		if (snake_x[0] < min):
			snake_x[0] = max_x
		if (snake_y[0] < min):
			snake_y[0] = max_y