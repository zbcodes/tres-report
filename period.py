from datetime import date


class Period:
    """
    Bieżący okres obliczeniowy
    """

    def __init__(self):
        self.__month = ('styczeń', 'luty', 'marzec', 'kwiecień', 'maj', 'czerwiec',
                        'lipiec', 'sierpień', 'wrzesień', 'październik', 'listopad', 'grudzień')

    def today_date(self):
        """Zwraca bieżącą datę w formacie: RRRR-MM-DD"""
        return '{:%Y-%m-%d}'.format(date.today())

    def year_month(self):
        """Zwraca bieżącą datę w formacie: RRMM"""
        return '{:%y%m}'.format(date.today())

    def month_year_str(self):
        """Zwraca bieżącą datę w formacie: miesiąć RRRR"""
        return self.__month[date.today().month - 1] + ' ' + str(date.today().year)
