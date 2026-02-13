from abc import ABC


class Matiere(ABC):
    def __init__(self, fichier):
        self._fichier = fichier

    @property
    def fichier(self):
        return self._fichier

    @fichier.setter
    def fichier(self, fichier):
        self._fichier = fichier
