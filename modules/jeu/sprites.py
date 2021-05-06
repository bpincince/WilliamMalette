# --------------------------------------------------------
# Nom : William Mallette
# Titre : Sprite/Collider/Gif
# Description : Module général d'images, contrôle la plupart des images dans le projet
# --------------------------------------------------------

# - Importation des modules ------------------------------

from tkinter import *
from PIL import Image, ImageTk

# - Variables globales -----------------------------------

# Cette liste garde les images à un niveau global, qui les permet de montrer dans le fenetre.
sprites = []

# - Déclaration des fonctions ----------------------------

# Le class des sprites
class Sprite:
    def __init__(self, parent, sprite, x=320, y=240, adjust=False, anchor="center"):
        # Établir le couleur du sprite comme étant une blanche opaque
        self._color = (255, 255, 255, 255)

        # Garder le canvas
        self.parent = parent

        # Les dimensions de l'image
        self.width, self.height = sprite.size

        # Le rotation
        self.rotation = 0

        # Le sprite initial (il faut spécifier qu'on veut des pixels transparentes)
        self.basespr = sprite.convert('RGBA')

        # Garder l'image pillow courant
        self.spr = self.basespr

        # Garder l'image tkinter (souviens qu'il faut garder un référence global à l'image ou il n'apparetera pas)
        self.spr_img = ImageTk.PhotoImage(self.spr)

        # Créer et garder l'objet sur le canvas
        self.image = parent.create_image(x, y, anchor=anchor)

        # La position du sprite
        self.x = x
        self.y = y

        # Ajoute le sprite à la liste
        sprites.append(self)

        # Faire certain que le sprite fonctionne correctement
        self.set(self.spr, adjust=adjust)

    # Tkinter aime couper un parti d'un image en mouvement sur un canvas, donc j'ai décidé d'ajouter d'autres pixels aux images
    # Sans ceci, le coeur du player démontrait des glitch visuels bizarres lors du mouvement
    # Pas entièrement nécessaire hors du player, mais utile.
    def adjust(self):
        # Créer un image transparente, deux fois la grandeur de l'image courant
        bg = Image.new('RGBA', (self.width*2, self.height*2), (0, 0, 0, 0,))

        # Ajoute l'image courant à cette image
        bg.paste(self.spr, (self.width//2, self.height//2))

        # Retourne le résultat
        return bg

    # Fonction qui offset l'objet par un montant de pixels
    def move(self, x=0, y=0):
        self.parent.move(self.image, x, y)
        self.x += x
        self.y += y

    # Déplace l'objet aux coordonnées exactes spécifiées
    def moveTo(self, x=0, y=0):
        self.parent.coords(self.image, x, y)
        self.x = x
        self.y = y

    # Fonction qui change le sprite de l'objet
    def set(self, newspr, adjust=True, replacebase=False):
        # Adjust si nécessaire
        if adjust:
            self.width, self.height = newspr.size
            newer_spr = self.adjust()
        else:
            newer_spr = newspr

        # Changer des variables
        self.spr = newer_spr
        self.spr_img = ImageTk.PhotoImage(self.spr)
        if replacebase: self.basespr = newspr

        # Set le sprite
        self.parent.itemconfig(self.image, image=self.spr_img)

    # Remplacer un couleur par un autre
    def color(self, color, color_to_replace=None):
        # Si un couleur autre que le couleur actif est spécifiée, utilise-la
        if color_to_replace: oldcolor = color_to_replace
        else: oldcolor = self._color

        # Une liste des pixels de l'image
        data = self.spr.getdata()
        new = []
        for pixel in data:
            # Détecter un match
            if pixel[0:4] == oldcolor:
                new.append(color)
            else:
                new.append(pixel[0:4])
        # Assembler le nouveau liste comme image et remplace self.spr
        self.spr.putdata(new)

        # Changer self._color
        self._color = color

        # Mettre le sprite à jour
        # Si adjust == True, l'image deviendra encore plus grand, et après quelques itérations, causer un crash.
        self.set(self.spr, adjust=False, replacebase=True)

    # Effectuer une rotation de 'rotation' degrés par rapport à 0 degrés
    def rotate(self, rotation):
        # Garder en note la rotation
        self.rotation = rotation

        # Effectue les changements
        self.spr = self.basespr.rotate(rotation, resample=Image.NEAREST, expand=True)

        # Si adjust == True, l'image deviendra encore plus grand, et après quelques itérations, causer un crash.
        self.set(self.spr, adjust=False)

    # Pour multiplier la grandeur de l'image
    def scale(self, hor, ver, replacebase=True):
        # À partir de l'image de base, multiplie la grandeur
        w, h = self.basespr.size
        self.spr = self.basespr.resize((w*hor, h*ver), resample=Image.NEAREST)

        # Appliquer les changements
        self.set(self.spr, replacebase=replacebase)

# Un class séparé pour les objets de collision
class Collider(Sprite):
    def __init__(self, parent, sprite, player, x=320, y=240, adjust=False, func=None, oneshot=True):
        # Initier le sprite
        Sprite.__init__(self, parent, sprite, x, y, adjust)

        # Obtenir les bords du sprite
        self.getBorders()

        # Garder le player
        self.player = player

        # Ajouter l'objet à la liste d'objets qui collident
        player.collidables.append(self)

        # Garder en note quel position à lequel l'objet est dans la liste
        self.id = len(player.collidables) - 1

        # Permettre le collision
        self.cancollide = True

        # Garder le fonction
        self.func = func

        # Garder le mode du fonction (si True, le fonction s'exécutera un fois seulement)
        self.oneshot = oneshot

    # Garde les côtés du sprite dans self.borders
    def getBorders(self):
        self.borders = [self.x - self.width / 2,   # L
                        self.x + self.width / 2,   # R
                        self.y - self.height / 2,  # U
                        self.y + self.height / 2,  # D
                        ]

    # Fonction exécuté quand l'objet est en collision avec le player
    def onCollide(self):
        if self.cancollide and self.func:
            if self.oneshot: self.cancollide = False
            self.func()

    # Enlève l'objet de la liste, enlève le sprite du canvas
    def destroy(self):
        self.cancollide = False
        self.player.collidables.pop(self.id)
        # On doit remplacer les indexes de chaque objet après celui en référence.
        for obj in self.player.collidables:
            if obj.id > self.id:
                obj.id -= 1
        self.parent.delete(self.image)

# Un class pour les gifs (utilisé pour le confetti)
# J'ai pris un peu d'inspiration de https://stackoverflow.com/questions/7960600/python-tkinter-display-animated-gif-using-pil
# Cependant, j'ai modifié beaucoup pour pouvoir fonctionner.
class Gif:
    def __init__(self, root, parent, image, x=320, y=240, rate=50, frameLimit=50, fade_after=10):
        # Garder le fenetre et le canvas
        self.root = root
        self.parent = parent

        # Un variable qui garde l'image courant
        self.mainframe = ImageTk.PhotoImage(image)

        # Les frames
        self.frames = []

        # L'opacité
        self.alpha = 255

        # Extraire les frames
        for i in range(frameLimit):
            try:
                image.seek(i)
            except:
                # Arrête quand on arrive au fin du gif
                break
            # En diminuant la grandeur de l'image, nous diminuons aussi le difficulté de la prochain opération
            newframe = image.convert("RGBA").resize((300, 250), resample=Image.NEAREST)
            # Si le frame est après "fade_after," diminue l'opacité
            # Image.putalpha remplace les pixels déjà transparents aussi, qui est ennuiyant. Alors, il faut remplacer
            # ces pixels encore. Il y a probablement une meilleure façon de faire ceci, mais je ne peut pas la trouver.
            # Il faut seulement faire ceci une fois, puisque c'est tellement une grande opération.
            if i - 1 >= fade_after and fade_after > 0:
                self.alpha -= 15
                newframe.putalpha(self.alpha)
                newdata = []
                for pixel in newframe.getdata():
                    if pixel == (255, 255, 255, self.alpha):
                        newdata.append((0, 0, 0, 0))
                    else:
                        newdata.append(pixel)
                newframe.putdata(newdata)

            # Ajouter le frame à la liste
            self.frames.append(newframe)

            # Avancer au prochain frame
            image.seek(i)

        # La vitesse de progression
        self.rate = rate

        # L'index du frame
        self.index = 0

        # L'objet
        self.img_obj = parent.create_image(x, y)

    # Jouer le gif, ne devrais pas être exécuté en succession rapide.
    def Play(self, reset=False):
        # Reset le gif
        if reset: self.index = 0

        # Avance au prochain frame
        if self.index < len(self.frames) - 1:
            self.mainframe = ImageTk.PhotoImage(self.frames[self.index])
            self.parent.itemconfig(self.img_obj, image=self.mainframe)
            self.index += 1

            # Recommence
            self.root.after(self.rate, self.Play)