import json


class Config:
    """
    Dane konfiguracujne programu
    """

    def __init__(self):
        self.__read_config()

    def __read_config(self):
        """Odczyt konfiguracji"""
        with open("config.json", "r") as f:
            cfg = json.load(f)
            self.__tres_path = cfg['tres_path']
            self.__results = cfg['results']
            self.__email_box = cfg['email_box']
            self.__email_address = cfg['email_address']

    def tres_path(self):
        """Ścieżka z danymi programu"""
        return self.__tres_path

    def results(self):
        """Ścieżka z wynikami programu"""
        return self.__results

    def email_box(self):
        """Dane skrzynki nadawczej e-mail"""
        return self.__email_box

    def email_address(self):
        """Dane rodzajów raportów i adresów e-mail odbiorców"""
        return self.__email_address
