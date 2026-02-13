from abc import ABC, abstractmethod


class Exercice(ABC):
    def __init__(self, fichier):
        self._fichier = fichier

    @property
    def fichier(self):
        return self._fichier

    @fichier.setter
    def fichier(self, fichier):
        self._fichier = fichier

    @abstractmethod
    def question(self):
        pass

    @abstractmethod
    def correction(self):
        pass
# Matrice pour savoir