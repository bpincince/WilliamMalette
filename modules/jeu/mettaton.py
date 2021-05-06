# --------------------------------------------------------
# Nom : William Mallette
# Titre : Mettaton
# Description : Contrôle MTT, le host du jeu
# --------------------------------------------------------

# - Importation des modules ------------------------------

from modules.jeu.sprites import Sprite, Gif
from modules.jeu.dialogue import Dialogue
from PIL import Image
from pygame import mixer
from math import sin, cos

# - Variables globales -----------------------------------

# Compteur global
timer = 0

# - Déclaration des fonctions ----------------------------

# Un class pour contrôler Mettaton, un personnage du jeu vidéo Undertale
class MTT:
    def __init__(self, root, parent, player):
        # Garder le fenêtre, le canvas, et le player
        self.root = root
        self.parent = parent
        self.player = player

        # Mouvement
        self.moving = False
        self.position = 1
        self.speed = 20
        self.x = 320
        self.y = 150

        # Le corps
        self.corps = Sprite(parent, Image.open("images/mtt/corps_default.png"), 320, 150)
        self.corps.scale(2, 2)

        # Les bras
        self.bras = Sprite(parent, Image.open("images/mtt/bras/wave_1.png"), 320, 100)
        self.bras.scale(2, 2)
        self._laser = None
        self.blast = None
        self.canlaser = True

        # Initialiser le gif de confetti
        self.confetti = Gif(root, parent, Image.open("images/confetti.gif"), y=125)

        # Des animations en forme d'une liste d'images
        self.anim_wave = ["images/mtt/bras/wave_1.png", "images/mtt/bras/wave_2.png"]
        self.anim_question = ["images/mtt/bras/question_1.png", "images/mtt/bras/question_2.png"]
        self.anim_celebration = ["images/mtt/bras/celebration_1.png", "images/mtt/bras/celebration_2.png"]
        # D'autres variables d'animation
        self.bras_anim = self.anim_wave
        self.bras_anim_index = 0
        self.animate = True

        # Une liste des sons de son voix
        self.voix = []
        for i in range(9):
            self.voix.append("sons/voix/v_mtt" + str(i + 1) + ".wav")

        # Commencer self.Update
        self.Update()

    # Pour changer l'animation des bras
    def setAnim(self, anim):
        newspr = Image.open(anim[0]).convert("RGBA")
        w, h = newspr.size
        newspr = newspr.resize((w * 2, h * 2), Image.NEAREST)
        self.bras.basespr = newspr
        self.bras_anim = anim

    # Créer un message de dialogue avec les paramètres idéals
    def message(self, text, side="r", takeInput=True, endfunc=None):
        if side == "r": x_offset = 80
        else: x_offset = -60
        self.msg = Dialogue(self.root, self.parent, text, x=self.x + x_offset, y=self.y, sons=self.voix, side=side,
                            takeInput=takeInput, endfunc=endfunc)

    # Bouger Mettaton d'un position ou l'autre (il y a seulement deux positions auxquels il peut être)
    def move(self, position):
        self.position = position
        self.moving = True

    # Commencer le laser
    def laser(self, endfunc=None):
        # Jouer le son
        s = mixer.Sound("sons/snd_wrong.wav")
        s.set_volume(0.125)
        s.play()

        # Changer l'animation
        self.setAnim(["images/mtt/bras/point.png"])

        # Créer le laser
        self._laser = self.parent.create_line(self.bras.x + self.bras.width / 2.5,
                                              self.bras.y - self.bras.height * cos(self.bras.rotation) / 6,
                                              self.player.x,
                                              self.player.y,
                                              fill="#FFFFFF",
                                              width=4)

        # Créer le blast
        self.blast = Sprite(self.parent, Image.open("images/blast_1.png"), self.player.x, self.player.y)
        self.blast.index = 0

        # Après un peu de temps, unlaser
        self.root.after(1000, lambda: self.unlaser(endfunc))

    # Enlève le laser
    def unlaser(self, endfunc):
        # Cleanup
        def cleanup(endfunc):
            self.parent.delete(self._laser)
            self.parent.delete(self.blast.image)
            self._laser = None
            self.blast = None
            # Exécuter le endfunc
            if endfunc: endfunc()

        # Hurt le player
        self.player.hurt(5)

        # Cleanup
        if self.canlaser: self.root.after(700, lambda: cleanup(endfunc))

    # Update l'animation
    def Update(self):
        global timer
        timer += 1

        # Le laser
        if self._laser:
            # Assurer que les points du ligne sont en ordre
            self.parent.coords(self._laser,
                               self.bras.x + self.bras.width / 2.5,
                               self.bras.y - 5 * sin(timer / 3),
                               self.player.x,
                               self.player.y,
                               )

            # Un simple animation d'oscillation
            self.parent.itemconfig(self._laser, width=int(2 * sin(timer / 3) + 5))

            # Le petit sprite de blast autour le player, simple animation de frame
            blasts = ["blast_1", "blast_2", "blast_3"]
            if timer % 3 == 0:
                if self.blast.index < 2:
                    self.blast.index += 1
                else:
                    self.blast.index = 0
                self.blast.set(Image.open(f"images/{blasts[self.blast.index]}.png"), adjust=False)
            self.blast.moveTo(self.player.x, self.player.y)

        # Mettaton
        if not self.moving:
            if self.animate:
                # Controler l'animation du personnage
                # Rotation
                rotation = 2 * sin(timer / 3)
                self.corps.rotate(rotation)

                # Changer l'image des bras périodiquement
                if timer % 6 == 0:
                    # Alterner dans la liste de l'animation actif
                    if (self.bras_anim_index) < len(self.bras_anim) - 1:
                        self.bras_anim_index += 1
                    else:
                        self.bras_anim_index = 0

                    # Format l'image correctement
                    img = Image.open(self.bras_anim[self.bras_anim_index]).convert("RGBA")
                    w, h = img.size
                    img_2 = img.resize((w * 2, h * 2), resample=Image.NEAREST)

                    # Change l'image de base des bras (le façon dans lequel spr.rotate() fonctionne va mettre à jour l'image automatiquement)
                    self.bras.basespr = img_2

                # Appliquer la rotation et translation nécessaire aux bras
                # J'ai essayé plusieurs méthodes trigonométriques exactes pour figurer une fonction universel, mais je n'étais pas capable de le figurer
                # Ce problème persiste même dans le code de mouvement, aussi.
                self.bras.rotate(rotation)
                new_x = self.corps.x
                new_y = self.corps.y - 25 - 5 * sin(timer / 3)
                self.bras.moveTo(new_x, new_y)

        # Le mouvement
        else:
            # Vers la position 2 (quand il demande une question)
            if self.position == 2:
                if self.x > 100:
                    # Bouger les objets
                    self.x -= self.speed
                    self.corps.move(-self.speed)
                    self.bras.move(-self.speed)

                    # Une rotation
                    if self.corps.rotation > -20:
                        self.corps.rotate(self.corps.rotation - 4)
                        self.bras.rotate(self.corps.rotation)
                        self.bras.moveTo(self.x + 16, self.y - 22)

                else:
                    # Lorsqu'on arrive à la position, reverse les changements d'avant
                    if self.corps.rotation < -5:
                        self.corps.rotate(self.corps.rotation + 8)
                        self.bras.rotate(self.corps.rotation)
                        self.bras.moveTo(self.x - abs(self.bras.rotation) / 2, self.y - abs(self.bras.rotation) * 2)

                    else:
                        self.moving = False

            # Vers la position 1 (normal)
            else:
                # Fait les mêmes choses qu'avant, mais à l'inverse
                if self.x < 320:
                    self.x += self.speed
                    self.corps.move(self.speed)
                    self.bras.move(self.speed)

                    if self.corps.rotation < 20:
                        self.corps.rotate(self.corps.rotation + 4)
                        self.bras.rotate(self.corps.rotation)
                        self.bras.moveTo(self.x - 16, self.y - 22)

                else:
                    if self.corps.rotation < 5:
                        self.corps.rotate(self.corps.rotation - 8)
                        self.bras.rotate(self.corps.rotation)
                        self.bras.moveTo(self.x + abs(self.bras.rotation) / 2, self.y - abs(self.bras.rotation) * 2)

                    else:
                        self.moving = False