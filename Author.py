class Author:
    surname: str
    name: str
    patronymic: str
    group: str

    def get_fullname(self):  # Получаем строку с ФИО
        fullname = " ".join([self.surname, self.name, self.patronymic])
        return fullname

    def get_initials(self):  # Получаем строку с фамилией и инициалами
        if self.patronymic == "":
            initials = f"{self.surname} {self.name[0]}."
        else:
            initials = f"{self.surname} {self.name[0]}.{self.patronymic[0]}."
        return initials

    def __init__(self, surname, name, patronymic="", group=""):
        self.surname = surname
        self.name = name
        self.patronymic = patronymic
        self.group = group