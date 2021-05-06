# --------------------------------------------------------
# Nom : William Mallette
# Titre : Jeu questionnaire
# Description : Une amélioration de l'évaluation sommatif 2, utilisant des éléments graphiques
# --------------------------------------------------------

# - Importation des modules ------------------------------

# Tkinter
from tkinter import *

# J'ai déplacé le processus d'installation au module de setup
from modules.setup import setup; setup()

# Pillow, Pygame, et Pyglet
from PIL import Image
from pygame import mixer
from pyglet import font

# Des classes custom que j'ai crée pour ce projet, je voulais expérimenter avec les classes.
from modules.jeu.sprites import Sprite
from modules.jeu.player import Player
from modules.jeu.mettaton import MTT
from modules.jeu.arena import Arena
from modules.jeu.ui import UI
from modules.tuteur import questions, resultats, temps

# - Déclaration des fonctions ----------------------------

# Effectuer des changements périodiques
# Puisqu'il y a plusieurs objets qui doivent être changés maintenant,
# il faut être un peu plus prudent avec le chronomètrage pour éviter du lag,
# car nous avons un allocation de mémoire limitée.
def Update():
    # Update le player et mettaton
    player.Update()
    mtt.Update()
    # Loop
    fenetre.after(30, Update)

# Montrer les éléments du jeu
def montreJeu():
    # Clean up le text d'instructions
    fenetre.unbind("<z>")
    cnvMain.delete(txtControls)
    cnvMain.delete(sprNoir.image)

    # Un message d'introduction
    mtt.message(["ÊTES-VOUS PRÊT?\nCROYEZ-VOUS QUE\nVOUS POUVEZ\nSURVIVRE?",
                 "HA. HA. HA. HA. HA.\n"*5,
                 "JE RIGOLE...\n...TRÈS LENTEMENT.",
                 "BIEN, AU REVOIR!"], side="l", endfunc=commenceJeu)

    # Commencer Update
    fenetre.after(0, Update)

# Commencer le jeu
def commenceJeu():
    # Mettre le player sur le bouton
    ui.movePlayer()

    # Commencer la musique
    mixer.music.load("sons/mus_mettatonbattle.ogg")
    mixer.music.set_volume(0.15)
    mixer.music.play(loops=-1)

    # Créer le text du menu
    ui.menuText("* Mettaton attaque!")

# - Programme principal ----------------------------------

# Initialise le mixer
mixer.init()

# Le fenetre, utiliser le même truc qu'avant pour le centrer.
fenetre = Tk()
fenetre.resizable(False, False)
fenetre.geometry(f"640x480+{int(fenetre.winfo_screenwidth()/2)-320}+{int(fenetre.winfo_screenheight()/2)-240}")
fenetre.title("UNDERTALE")

# Utilisant font de Pyglet, ajoute des fonts au jeu
# Si on ouvre le fichier de ce font, nous découvrons que le nom du font est "Gulim".
# On devrait utiliser un grandeur de 11 et un police bold.
font.add_file("fonts/DotumCheRegular.ttc")
# Le nom de celui-ci est "Determination Mono", un grandeur de 20 est bon.
font.add_file("fonts/DTM-Mono.otf")
# "MenuFont," un grandeur de 18
font.add_file("fonts/MenuFont.otf")

# Un canvas sur lequel le canvas primaire se situe, pour permettre l'éffet de "shake"
cnvParent = Canvas(fenetre, width=640, height=480, bg="#000000", highlightthickness=0)
cnvParent.pack()

# Le canvas primaire du jeu
cnvMain = Canvas(fenetre, width=640, height=480, bg="#000000", highlightthickness=0)
cnvMain.pack()
# Garder référence à cnvParent dans cnvMain, mettre cnvMain sur cnvParent
cnvMain.parent = cnvParent
cnvMain.id = cnvParent.create_window(320, 240, window=cnvMain)

# Créer l'aréna
arena = Arena(fenetre, cnvMain)
arena.resize(570, 135)
arena.moveTo(319, 319)

# Créer le player
player = Player(fenetre, cnvMain, arena)

# Créer Mettaton
mtt = MTT(fenetre, cnvMain, player)

# Créer le menu (boutons, text de menu)
ui = UI(fenetre, cnvMain, player, mtt)

# Cacher les autres objets
sprNoir = Sprite(cnvMain, sprite=Image.new('RGBA', (640, 480), (0, 0, 0, 255,)))

# Créer les instructions
instructions = ["-"*10 + "CONTRÔLES" + "-"*10,
                "Mouvement : touches directionnelles",
                "Confirmer/avancer le text : Z",
                "Skip le text : X",
                "Indices : C",
                "",
                "Si votre HP atteint 0, tu as perdu!",
                "",
                "[Appuyez sur Z pour continuer]",
                "*Assurez-vous que votre CAPSLOCK est désactivé*",
                "*Sinon, le jeu vais détecter certains inputs différemment.*"]
txtControls = cnvMain.create_text(320, 240, text='\n'.join(instructions), font=("Gulim", 11, "bold"), fill="#888888", justify="center")
# Commencer le jeu
fenetre.bind("<z>", lambda z: montreJeu())

# Le titre et l'icone du fenetre
# Il faut faire ceci après la création de tous ces objets ci-dessus, puisque si on force l'interpreteur à lire l'ico il y aura un délai.
fenetre.iconbitmap("images/icon.ico")

# Garde le fenêtre ouvert
fenetre.mainloop()