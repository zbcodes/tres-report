#!/usr/bin/env python3

import os

from config import Config
from tres import Tres
from excel import Excel
from mail import Email


def main():
    # utworzenie obiektu z danymi konfiguracujnymi programu
    cfg = Config()

    # opróżnienie katalogu z poprzednimi raportami
    os.chdir(cfg.results())
    os.system('rm *')

    # utworzenie obiektów: danych żródłowych, raportów, modułu wysyłania poczty
    t = Tres(cfg.tres_path())
    exl = Excel()
    eml = Email(cfg.email_box())

    # wysyłanie e-maili z raportami
    if t.is_sale():
        eml.send(cfg.email_address()['sale'], 'Raport dzienny sprzedaży', exl.sale(t.sale()))


if __name__ == '__main__':
    main()
