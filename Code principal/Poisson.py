from abc import ABC, abstractmethod


class Poisson:

    def __init__(self, image: str, niveau: int, nom: str):
        self._image = image
        self._niveau = niveau
        self._nom = nom

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, image):
        self._image = image

    @property
    def niveau(self):
        return self._niveau

    @niveau.setter
    def niveau(self, niveau):
        self._niveau = niveau

    @property
    def nom(self):
        return self._nom

    @nom.setter
    def nom(self, nom):
        self._nom = nom


class AtaquePoisson:

    def __init__(self):
        pass

    def niveau_1(self):
        pass


class DefensePoisson:

    def __init__(self):
        pass

    def niveau_1(self):
        pass
