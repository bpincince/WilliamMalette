# --------------------------------------------------------
# Nom : William Mallette
# Titre : Player
# Description : L'objet du player, ainsi que des objets liées (HP bar, etc.)
# --------------------------------------------------------

# - Importation des modules ------------------------------

from modules.jeu.sprites import Sprite
from modules.jeu.ui import compileResults
from PIL import Image
from pygame import mixer
from random import randrange, uniform

# - Déclaration des fonctions ----------------------------

# Lorsque l'HP devient 0
def gameOver(player):
    # Arrête la musique
    mixer.music.stop()

    # Prévenir le retour au menu via MTT.unlaser()
    player.UI.mtt.canlaser = False

    # Unbind le mouvement
    player.bindInput()

    # 0 HP
    # Cacher le sprite du HP bar (puisque Pillow ne permet pas un scale de 0)
    player.parent.tag_lower(player.hp_spr.image)
    # Changer le text de l'indicateur
    player.parent.itemconfig(player.hp_txt, text=f"00 / {player.maxhp}")

    # Les sons
    s_1 = mixer.Sound("sons/heartbreak.wav")
    s_1.set_volume(0.125)
    s_2 = mixer.Sound("sons/heartsplosion.wav")
    s_2.set_volume(0.125)

    # Après un moment, cacher ce qui se passe
    player.root.after(150, lambda: Sprite(player.parent, Image.new("RGBA", (640, 480), (0, 0, 0, 255))))

    # L'explosion
    def explode():
        # Un class pour les shards
        class shard:
            def __init__(self, xvel, yvel):
                # L'animation
                self.anim = []
                for i in range(4): self.anim.append(Image.open("images/heartshard" + str(i + 1) + ".png"))
                self.anim_id = randrange(0, 4)

                # Le sprite
                self.spr = Sprite(player.parent, self.anim[self.anim_id], x=player.x, y=player.y, adjust=True)

                # Un accélération aléatoire
                self.yacc = round(uniform(0.5, 1), 2)

                # Les vélocités
                self.xvel = xvel
                self.yvel = yvel

                # Un timer
                self.timer = 0

                # Commencer self.update()
                self.update()

            def update(self):
                self.timer += 1
                # À chaque cinquième update, changer le sprite
                if self.timer % 5 == 0:
                    # Garder self.anim_id dans les limites
                    if self.anim_id < len(self.anim) - 1:
                        self.anim_id += 1
                    else:
                        self.anim_id = 0

                    # Changer le sprite
                    # Je voulais utiliset spr.set() mais il y avait un anomalie visuel
                    self.spr.basespr = self.anim[self.anim_id]

                    # Provoque un changement du sprite en effectuant une rotation de 0 degrés
                    self.spr.rotate(0)

                # Augmente le vélocité verticale
                self.yvel += self.yacc

                # Bouger le shard
                self.spr.move(self.xvel, self.yvel)

                # Loop
                player.root.after(30, self.update)

        # Jouer un son
        s_2.play()

        # Cacher le player
        player.set(Image.new("RGBA", (1, 1), (0) * 4), adjust=False)

        # Liste de vitesses initiales
        vel = [(-10, -10), (-5, -15), (5, -5), (9, 2)]

        # Créer des shards
        for i in range(len(vel)): shard(vel[i][0], vel[i][1])

        # Après un moment, montrer les résultats
        player.root.after(1000, lambda: compileResults(player.UI, skipFade=True))

    # Briser le coeur
    def breakh():
        # Jouer un son
        s_1.play()
        # Changer le sprite
        player.set(Image.open("images/heart_broken.png"), adjust=False)
        player.color(player._color, (255, 255, 255, 255))
        # Explode
        player.root.after(1000, explode)

    # Après un moment, brise le coeur
    player.root.after(200, breakh)

# Un class pour le player
class Player(Sprite):
    def __init__(self, root, parent, arena):
        # Garder un référence à la fenêtre
        self.root = root

        # Garder un référence à l'aréna
        self.arena = arena

        # Créer le sprite
        Sprite.__init__(self, parent, Image.open("images/ut-heart.png"), adjust=True, x=arena.x, y=arena.y)

        # Les directions [L, R, U, D]
        self.direction = [False] * 4

        # La vitesse
        self.speed = 2.75*2

        # Changer le couleur
        self.color((255, 0, 0, 255))

        # Une liste d'objets avec lequel le player peut intéragir
        self.collidables = []

        # Les frames pour lequel le player 'blink' après un hurt(), voir hurt()
        self.iframes = 0

        # HP, max HP, et LV
        self.lv = 1
        self.maxhp = 20
        self.hp = self.maxhp

        # L'indicateur d'LV
        self.lv_text = parent.create_text(132, 412, text="LV 1", font=("MenuFont", 18), fill="#FFFFFF", anchor="w")

        # Un indicateur d'HP
        self.hp_txt = parent.create_text(314, 412, font=("MenuFont", 18), fill="#FFFFFF", anchor="w")

        # L'image qui dit 'HP'
        self.HP_mark = Sprite(parent, Image.open("images/ui/spr_hpname_0.png"), x=255, y=410)

        # Le max HP
        self.maxhp_spr = Sprite(parent, Image.open("images/ui/hpbar.png"), x=263, y=411, anchor="w")
        self.maxhp_spr.color((255, 0, 0, 255))
        self.setMaxHP(self.maxhp)

        # L'HP
        self.hp_spr = Sprite(parent, Image.open("images/ui/hpbar.png"), x=263, y=411, anchor="w")
        self.hp_spr.color((255, 255, 0, 255))
        # Set l'HP
        self.setHP(self.hp)

    # Dommager le player
    def hurt(self, amount, override_iframes=False, shake=True, shakeIntensity=3):
        # Est-ce que le player peut être dommagé?
        canhurt = (override_iframes and self.iframes) or (self.iframes == 0)

        # Prévenir un setHP(0) (crash)
        if self.hp - amount > 0 and canhurt:
            # Change l'HP
            self.setHP(self.hp - amount)

            # Commence le 'blink' et l'invulnérabilité
            self.iframes = 30

            # Jouer un son
            s = mixer.Sound("sons/hurtsound.wav")
            s.set_volume(0.125)
            s.play()

            # L'effet qui "shake" l'écran
            if shake:
                # Sélectionner deux offsets
                val = [-shakeIntensity, shakeIntensity]
                nx = val[randrange(0, len(val))]
                ny = val[randrange(0, len(val))]

                # Bouge le canvas relatif à son parent
                self.parent.parent.move(self.parent.id, nx, ny)

                # Apres quelques instants, retourne le canvas à sa position normal
                self.root.after(40, lambda: self.parent.parent.move(self.parent.id, -nx, -ny))

        # Si on atteint 0 HP, gameOver
        elif self.hp - amount <= 0:
            # set les iframes
            self.iframes = 8

            # Jouer un son
            s = mixer.Sound("sons/hurtsound.wav")
            s.set_volume(0.125)
            s.play()

            # gameOver
            gameOver(self)

    # Soigner le player
    def heal(self, amount, bypass_max=False):
        # Garder l'HP au maxhp à moins qu'on spécifie autrement
        if self.hp + amount <= self.maxhp or bypass_max:
            # Changer l'HP
            self.setHP(self.hp + amount)

            # Jouer un son
            s = mixer.Sound("sons/healsound.wav")
            s.set_volume(0.125)
            s.play()

        else:
            # Si il y aura un overflow,
            if self.hp < self.maxhp:
                # Max l'HP
                self.setHP(self.maxhp)

                # Jouer un son
                s = mixer.Sound("sons/healsound.wav")
                s.set_volume(0.125)
                s.play()

    # Fonction qui modifie l'HP du player
    def setHP(self, newhp):
        # L'équation pour la longueur du bar d'HP
        # Il faut être un non-zero integer positif puisque ce sont les limites de Pillow
        newscale = int((newhp/4)*5)

        # Modifier l'image du HP bar
        self.hp_spr.scale(newscale, 1, replacebase=False)

        # Il faut le déplacer un peu puisque Tkinter et Pillow intéragissent d'un façon bizarre
        self.hp_spr.moveTo(263 + 12 - newscale/2, self.hp_spr.y)

        # Changer la valeur de self.hp et le text de l'indicateur
        self.hp = newhp
        self.parent.itemconfig(self.hp_txt, text="{:0>2} / {:0>2}".format(self.hp, self.maxhp))

    # Fonction qui modifie le max HP du player
    def setMaxHP(self, newhp):
        # Même chose qu'avant
        newscale = int((newhp / 4) * 5)
        self.maxhp_spr.scale(newscale, 1, replacebase=False)
        self.maxhp_spr.moveTo(263 + 12 - newscale / 2, self.maxhp_spr.y)
        self.maxhp = newhp
        self.parent.itemconfig(self.hp_txt, text="{:0>2} / {:0>2}".format(self.hp, self.maxhp))

        # Bouger le text un peu pour garder sa distance du bar
        self.parent.coords(self.hp_txt, 263 + newscale + 26, 412)

    # Modifier self.lv et tous les valeurs reliés
    def setLV(self, newLV):
        # Le son
        s = mixer.Sound("sons/levelup.wav")
        s.set_volume(0.125)

        # Calculer le nouveau maxhp et joue le son
        if newLV < 20:
            if newLV > self.lv: s.play()
            self.lv = newLV
            self.setMaxHP(4 * self.lv + 16)

        # Arrête à lv20, avec 99 HP
        elif newLV == 20:
            if newLV > self.lv: s.play()
            self.lv = newLV
            self.setMaxHP(99)

        # Change l'indicateur
        self.parent.itemconfig(self.lv_text, text=f"LV {self.lv}")

    # Fonction utilisé par les keybinds pour commencer et arrêter le mouvement
    def setDir(self, index, val):
        self.direction[index] = val

    def Update(self):
        # Le mouvement, souvient: [L, R, U, D]
        # On peut facilement garder le coeur dans l'aréna en utilisant max() ou min() quand on lui bouge pour vérifier si qu'il va rester dans la boîte ou non
        if self.direction[0]:
            new_x = max(self.x - self.speed, self.arena.x - self.arena.width/2 + 11)
            self.moveTo(new_x, self.y)
        if self.direction[1]:
            new_x = min(self.x + self.speed, self.arena.x + self.arena.width / 2 - 10)
            self.moveTo(new_x, self.y)
        if self.direction[2]:
            # Ça me frustre que tkinter utilise des valeurs négatives pour monter dans l'axe vertical, mais il y a très peu que je peux faire pour changer cela.
            new_y = max(self.y - self.speed, self.arena.y - self.arena.height / 2 + 11)
            self.moveTo(self.x, new_y)
        if self.direction[3]:
            new_y = min(self.y + self.speed, self.arena.y + self.arena.height / 2 - 10)
            self.moveTo(self.x, new_y)

        # Utilise canvas.tag_raise pour mettre le player au layer maximal
        self.parent.tag_raise(self.image)

        # Vérifier pour une collision
        for obj in self.collidables:
            # Si le player est entre les borders d'un objet, exécute sa fonction onCollide()
            if obj.borders[0] < self.x < obj.borders[1] and obj.borders[2] < self.y < obj.borders[3]:
                obj.onCollide()

        # Cause le player à faire un effet de 'blink'
        if self.iframes > 0:
            # Réduire self.iframes jusqu'à 0
            self.iframes -= 1

            # À chaque troisième frame, blink (divise le couleur de base par 2)
            if self.iframes%3 == 0:
                if self._color == (255, 0, 0, 255): self.color((128, 0, 0, 255))
                else: self.color((255, 0, 0, 255))

        # Lorsque les iframes sont fini, assure que le couleur retourne à normal
        else:
            if self._color != (255, 0, 0, 255): self.color((255, 0, 0, 255))

    # Connecter les arrow keys à la fonction de mouvement
    def bindInput(self, mode=""):
        # Unbind tous les clés utilisés par l'objet de player pour assurer tout va bien
        self.root.unbind("<Left>")
        self.root.unbind("<KeyRelease-Left>")
        self.root.unbind("<Right>")
        self.root.unbind("<KeyRelease-Right>")
        self.root.unbind("<Up>")
        self.root.unbind("<KeyRelease-Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<KeyRelease-Down>")

        # Annuler le mouvement pour prévenir un glissement à l'infini
        for i in range(len(self.direction)):
            self.setDir(i, False)

        # Quand le coeur est dans le rectangle:
        if mode == "arena":
            self.root.bind("<Left>", lambda k: self.setDir(0, True))
            self.root.bind("<KeyRelease-Left>", lambda e: self.setDir(0, False))

            self.root.bind("<Right>", lambda k: self.setDir(1, True))
            self.root.bind("<KeyRelease-Right>", lambda e: self.setDir(1, False))

            self.root.bind("<Up>", lambda k: self.setDir(2, True))
            self.root.bind("<KeyRelease-Up>", lambda e: self.setDir(2, False))

            self.root.bind("<Down>", lambda k: self.setDir(3, True))
            self.root.bind("<KeyRelease-Down>", lambda e: self.setDir(3, False))

        # Sélectionnement de "prochain" ou "quitter"
        elif mode == "buttons":
            self.root.bind("<Left>", lambda k: self.moveTo(203, 454))
            self.root.bind("<Right>", lambda k: self.moveTo(363, 454))