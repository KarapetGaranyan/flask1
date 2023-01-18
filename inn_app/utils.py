import random
import os
import re

from flask import session
import fitz
import sqlite3
from pytrovich.enums import NamePart, Gender, Case
from pytrovich.maker import PetrovichDeclinationMaker
from pytrovich.detector import PetrovichGenderDetector
from docxtpl import DocxTemplate
import openpyxl

def allowed_file(filename, ALLOWED_EXTENSIONS):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def getClassByFilPreifx(prefix):
    type_o = None
    if prefix == 'fl':
        return IP
    elif prefix == 'ul':
        return UL
    else:
        return N

def get_pdf(filename, save_path):
    # Сохранение в текст
    file = fitz.open(filename)
    text = ''
    hash_name = ("%032x" % random.getrandbits(128))
    session['hash'] = hash_name
    save_file_path = f'{os.path.join(save_path, "")}{hash_name}.txt'
    for page in file:
        text += page.get_text()
        txt = open(save_file_path, 'w')  # открытие файла
        txt.writelines(text)  # запись в файл
        txt.close()  # закрытие файла
    file.close()


    # Нормализация текста
    text_document = open(save_file_path, 'r')
    text = text_document.read()
    text = text.replace('', '')
    text_document.close()
    text_document = open(save_file_path, 'w')
    text_document.write(text)
    text_document.close()


    # Тип файла
    type_o = None
    if 'fl-' in filename:
        type_o = 'fl'
    elif 'ul-' in filename:
        type_o = 'ul'
    else:
        type_o = 'n'

    # Создание БД
    try:
        connection = sqlite3.connect('text.sqlite')  # Создание или подключение к БД
        q = connection.cursor()  # Создание курсора для работы с БД
        q.execute('''CREATE TABLE if not exists UL (id int auto_increment primary key, Полное_наименование varchar, Сокращенное_наименование varchar, Полное_наименование_анг varchar,
        Сокращенное_наименование_анг varchar, ИНН int UNIQUE ON CONFLICT REPLACE, ОГРН int, Руководитель varchar, ИНН_директора varchar, Должность varchar, Телефон varchar, Дата varchar, Индекс varchar, КПП varchar, ОКПО varchar,
        ОКВЭД varchar, ДОП_ОКВЭДЫ varchar, Эл_почта varchar, Адрес_устав text, Адрес text, Участники varchar, Капитал varchar, Адрес_сайта varchar, Банк varchar, Вид_Л varchar, Номер_Л varchar, Дата_Л varchar, Орган_Л varchar)''')
        q.execute('''CREATE TABLE if not exists IP (id int auto_increment primary key, Наименование varchar, ИНН int UNIQUE ON CONFLICT REPLACE, ОГРНИП int,
        Телефон varchar, Дата varchar, ОКВЭД varchar, ДОП_ОКВЭДЫ varchar, Эл_почта varchar, Адрес text, Адрес_сайта varchar, Банк varchar )''')
        q.execute(
            '''CREATE TABLE if not exists PS (id int auto_increment primary key, sotrudnik varchar, dolzhnost_bank varchar, dolzhnost_bank_poln varchar, dover varchar )''')
        connection.commit()  # сохраняем изменения
    except BaseException as e:
        raise RuntimeError("Ошибка создания БД")
    session['cl'] = type_o
    session['tmp_file'] = save_file_path


def RKO(inn, podpisant, templates_path, treaties_path, hash ):
    try:
        connection = sqlite3.connect('text.sqlite')  # Подключение к БД
        q = connection.cursor()  # Создание курсора для работы с БД
    except BaseException as e:
        raise RuntimeError("Ошибка подключения к БД")
    poisk_inn = inn
    sql = "SELECT * FROM UL WHERE ИНН=?"
    q.execute(sql, (poisk_inn,))
    res = q.fetchall()
    sql = "SELECT * FROM IP WHERE ИНН=?"
    q.execute(sql, (poisk_inn,))
    res_ip = q.fetchall()
    if not res_ip and not res:
        raise BaseException("Данный ИНН отсутствует в БД")

    # Юридическое лиц
    if len(str(poisk_inn)) == 10 and res != []:
        try:
            sql = "SELECT * FROM UL WHERE ИНН=?"
            q.execute(sql, (poisk_inn,))
            res = q.fetchall()
            list_data = list(res[0])

            name = list_data[1]
            name_sokr = list_data[2]
            name_en = list_data[3]
            name_en_sokr = list_data[4]
            inn = list_data[5]
            ogrn = list_data[6]
            director = list_data[7]
            inn_dir = list_data[8]
            dolzhnost = list_data[9]
            telephone = list_data[10]
            date = list_data[11]
            index_p = list_data[12]
            kpp = list_data[13]
            okpo = list_data[14]
            okved = list_data[15]
            dop_okved = list_data[16]
            email = list_data[17]
            address_ustav = list_data[18]
            address = list_data[19]
            uchastnik_d1 = list_data[20]
            capital = list_data[21]
            domen = list_data[22]
            bank = list_data[23]
            vid_L = list_data[24]
            nomer_L = list_data[25]
            data_L = list_data[26]
            organ_L = list_data[27]
        except BaseException as e:
            raise BaseException("Ошибка поиска ЮЛ")

        try:
            dolzhnost_bank_poln = dolzhnost_bank = sotrudnik = dover = ""
            res_ps = []
            poisk_ps =  podpisant
            sql = "SELECT * FROM PS WHERE id=?"
            q.execute(sql, (poisk_ps,))
            res_ps = q.fetchall()
            list_data_ps = list(res_ps[0])
            sotrudnik = list_data_ps[1]
            dolzhnost_bank = list_data_ps[2]
            dolzhnost_bank_poln = list_data_ps[3]
            dover = list_data_ps[4]
        except BaseException as e:
            raise BaseException("Ошибка введенных данных")

        try:
            if dolzhnost == "ГЕНЕРАЛЬНЫЙ ДИРЕКТОР":
                dolzhnost = "Генеральный директор"
                dolzhnost_r = "Генерального директора"
            elif dolzhnost == "ДИРЕКТОР":
                dolzhnost = "Директор"
                dolzhnost_r = "Директора"
        except BaseException as e:
            raise BaseException("Ошибка перевода должности в РП")

        try:
            director_r = director.lower().split(' ')
            director_r[0] = director_r[0].capitalize()
            director_r[1] = director_r[1].capitalize()
            director_r[2] = director_r[2].capitalize()
        except BaseException as e:
            raise BaseException("Ошибка перевода ФИО в заглавные буквы")
        # morph = pymorphy2.MorphAnalyzer()
        # director_r[1] = morph.parse(director_r[1])[0]
        # gent = director_r[1].inflect({'gent'})
        # director_r[1] = gent.word.capitalize()
        # director_r[0] = morph.parse(director_r[0])[1]
        # gent = director_r[0].inflect({'gent'})
        # director_r[0] = gent.word.capitalize()
        # director_r[2] = morph.parse(director_r[2])[0]
        # gent = director_r[2].inflect({'gent'})
        # director_r[2] = gent.word.capitalize()
        # director_r = ' '.join(director_r)

        try:
            detector = PetrovichGenderDetector()
            Gender = detector.detect(firstname=director_r[1])
            maker = PetrovichDeclinationMaker()
            director_r[0] = maker.make(NamePart.LASTNAME, Gender, Case.GENITIVE, director_r[0])
            director_r[1] = maker.make(NamePart.FIRSTNAME, Gender, Case.GENITIVE, director_r[1])
            director_r[2] = maker.make(NamePart.MIDDLENAME, Gender, Case.GENITIVE, director_r[2])
            director_r = ' '.join(director_r)
        except BaseException as e:
            raise BaseException("Ошибка перевода ФИО директора в РП")

        dirname = templates_path # директория с шаблонами
        os.mkdir(f'{os.path.join(treaties_path, "")}{hash}')   # директория с договорами
        dirname_UL = f'{os.path.join(treaties_path, "")}{hash}'

        try:
            # Карточка с образцами подписей
            doc = DocxTemplate(dirname + "/КОП.docx")
            context = {'Полное_наименование': name, 'Сокращенное_наименование': name_sokr, 'Должность': dolzhnost,
                       'Руководитель': director, 'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank}
            doc.render(context)
            doc.save(dirname_UL + "/КОП.docx")

            # Анкета

            doc1 = DocxTemplate(dirname + "/Анкета ЮЛ.docx")
            context = {'Полное_наименование': name, 'Сокращенное_наименование': name_sokr,
                       'Полное_наименование_анг': name_en, 'Сокращенное_наименование_анг': name_en_sokr,
                       'Адрес_устав': address_ustav, 'Адрес': address, 'Дата': date, 'ОКВЭД': okved, 'ИНН': inn, 'ОГРН': ogrn, 'ОКПО': okpo,
                       'Участники': uchastnik_d1, 'Должность': dolzhnost, 'Руководитель': director,
                       'Адрес_сайта': domen, 'Телефон': telephone, 'Эл_почта': email, 'ИНН_директора': inn_dir,
                       'Вид_Л': vid_L, 'Номер_Л': nomer_L, 'Дата_Л': data_L, 'Орган_Л': organ_L,
                       }
            doc1.render(context)
            doc1.save(dirname_UL + "/Анкета ЮЛ.docx")

            # Оферта
            doc2 = DocxTemplate(dirname + "/Оферта.docx")
            context = {'Полное_наименование': name, 'Сокращенное_наименование': name_sokr,
                       'Адрес_устав': address_ustav, 'Адрес': address, 'ИНН': inn, 'ОГРН': ogrn, 'КПП': kpp,
                       'Должность1': dolzhnost_r, 'Руководитель': director, 'Руководитель_рп': director_r,
                       'Телефон': telephone, 'Эл_почта': email}
            doc2.render(context)
            doc2.save(dirname_UL + "/Оферта.docx")

            # ДС
            doc3 = DocxTemplate(dirname + "/ДС_КОП.docx")
            context = {'Полное_наименование': name, 'Должность': dolzhnost, 'Должность1': dolzhnost_r,
                       'Руководитель': director, 'Руководитель_рп': director_r,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln}
            doc3.render(context)
            doc3.save(dirname_UL + "/ДС_КОП.docx")

            # Заявление на пакет
            doc4 = DocxTemplate(dirname + "/Заявление_пакет.docx")
            context = {'Полное_наименование': name, 'Должность1': dolzhnost_r, 'Руководитель': director,
                       'Руководитель_рп': director_r, 'Телефон': telephone, 'ИНН': inn}
            doc4.render(context)
            doc4.save(dirname_UL + "/Заявление_пакет.docx")

            # Протокол НН
            doc5 = DocxTemplate(dirname + "/Протокол.docx")
            context = {'Сокращенное_наименование': name_sokr, 'Руководитель': director, 'Должность': dolzhnost,
                       'ФИО_сотрудника': sotrudnik}
            doc5.render(context)
            doc5.save(dirname_UL + "/Протокол.docx")

            # Приказ на печать
            doc6 = DocxTemplate(dirname + "/Приказ_печать.docx")
            context = {'Сокращенное_наименование': name_sokr, 'Руководитель': director, 'Должность': dolzhnost}
            doc6.render(context)
            doc6.save(dirname_UL + "/Приказ_печать.docx")

            # ДС валюта
            doc7 = DocxTemplate(dirname + "/ДС_валюта.docx")
            context = {'Полное_наименование': name, 'Должность': dolzhnost, 'Руководитель': director,
                       'Руководитель_рп': director_r,
                       'Адрес_устав': address_ustav, 'Адрес': address, 'ИНН': inn, 'ОГРН': ogrn, 'КПП': kpp,
                       'Телефон': telephone, 'Эл_почта': email,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln, 'Должность1': dolzhnost_r, }
            doc7.render(context)
            doc7.save(dirname_UL + "/ДС_валюта.docx")

            # Сообщение
            doc8 = DocxTemplate(dirname + "/Сообщение.docx")
            context = {'Полное_наименование': name, 'Должность': dolzhnost, 'Руководитель': director,
                       'Адрес_устав': address_ustav, 'Адрес': address, 'Доверенность': dover,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln}
            doc8.render(context)
            doc8.save(dirname_UL + "/Сообщение.docx")

            # Заявка ЭБ
            doc9 = DocxTemplate(dirname + "/Заявка_ЭБ.docx")
            context = {'Полное_наименование': name, 'Руководитель': director, 'ИНН': inn}
            doc9.render(context)
            doc9.save(dirname_UL + "/Заявка_ЭБ.docx")

            # FATCA
            wb = openpyxl.load_workbook(dirname + "/FATCA.xlsx")
            sheet = wb.active
            sheet['F5'] = name
            sheet['F6'] = inn
            sheet['F8'] = address_ustav
            sheet['F9'] = address
            sheet['G14'] = inn
            wb.save(dirname_UL + "/FATCA.xlsx")
            wb.close
        except BaseException as e:
            raise BaseException("Ошибка обработки данных")

    # Индивидуальный предприниматель
    elif len(str(poisk_inn)) == 12 and res_ip != []:
        try:
            sql = "SELECT * FROM IP WHERE ИНН=?"
            q.execute(sql, (poisk_inn,))
            res_ip = q.fetchall()
            list_data = list(res_ip[0])

            name = list_data[1]
            name = name.replace('Индивидуальный предприниматель ', '')
            fullname = list_data[1]
            inn = list_data[2]
            ogrnip = list_data[3]
            telephone = list_data[4]
            date = list_data[5]
            okved = list_data[6]
            dop_okved = list_data[7]
            email = list_data[8]
            address = list_data[9]
            domen = list_data[10]
            bank = list_data[11]
        except BaseException as e:
            raise BaseException("Ошибка поиска ИП")

        dirname = templates_path # директория с шаблонами
        os.mkdir(f'{os.path.join(treaties_path, "")}{hash}')   # директория с договорами
        dirname_IP = f'{os.path.join(treaties_path, "")}{hash}'

        try:
            dolzhnost_bank_poln = dolzhnost_bank = sotrudnik = dover = ""
            res_ps = []
            poisk_ps = podpisant
            sql = "SELECT * FROM PS WHERE id=?"
            q.execute(sql, (poisk_ps,))
            res_ps = q.fetchall()
            list_data_ps = list(res_ps[0])
            sotrudnik = list_data_ps[1]
            dolzhnost_bank = list_data_ps[2]
            dolzhnost_bank_poln = list_data_ps[3]
            dover = list_data_ps[4]
        except BaseException as e:
           raise BaseException("Ошибка введенных данных")

        try:
            # Карточка с образцами подписей
            doc = DocxTemplate(dirname + "/КОП_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'ФИО_сотрудника': sotrudnik,
                       'Должность_банк': dolzhnost_bank}
            doc.render(context)
            doc.save(dirname_IP + "/КОП_ИП.docx")

            # Анкета
            doc1 = DocxTemplate(dirname + "/Анкета ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'Адрес': address, 'ИНН': inn,
                       'ОГРНИП': ogrnip, 'Руководитель': name,
                       'Адрес_сайта': domen, 'Телефон': telephone, 'Эл_почта': email, 'Реквизиты': bank}
            doc1.render(context)
            doc1.save(dirname_IP + "/Анкета ИП.docx")

            # Оферта
            doc2 = DocxTemplate(dirname + "/Оферта_ИП.docx")
            context = {'Полное_наименование': fullname, 'Адрес': address, 'ИНН': inn, 'ОГРНИП': ogrnip,
                       'Руководитель': name, 'Дата': date,
                       'Телефон': telephone, 'Эл_почта': email}
            doc2.render(context)
            doc2.save(dirname_IP + "/Оферта_ИП.docx")

            # ДС
            doc3 = DocxTemplate(dirname + "/ДС_КОП_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'Дата': date, 'ОГРНИП': ogrnip,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln}
            doc3.render(context)
            doc3.save(dirname_IP + "/ДС_КОП_ИП.docx")

            # Заявление на пакет
            doc4 = DocxTemplate(dirname + "/Заявление_пакет_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'ИНН': inn, 'ОГРНИП': ogrnip,
                       'Телефон': telephone, 'Дата': date}
            doc4.render(context)
            doc4.save(dirname_IP + "/Заявление_пакет_ИП.docx")

            # Протокол НН
            doc5 = DocxTemplate(dirname + "/Протокол_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'ФИО_сотрудника': sotrudnik}
            doc5.render(context)
            doc5.save(dirname_IP + "/Протокол_ИП.docx")

            # Приказ на печать
            doc6 = DocxTemplate(dirname + "/Приказ_печать_ИП.docx")
            context = {'Полное_наименование': fullname}
            doc6.render(context)
            doc6.save(dirname_IP + "/Приказ_печать_ИП.docx")

            # ДС валюта
            doc7 = DocxTemplate(dirname + "/ДС_валюта_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name,
                       'Адрес': address, 'ИНН': inn, 'ОГРНИП': ogrnip, 'Телефон': telephone, 'Эл_почта': email,
                       'Дата': date,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln}
            doc7.render(context)
            doc7.save(dirname_IP + "/ДС_валюта_ИП.docx")

            # Сообщение
            doc8 = DocxTemplate(dirname + "/Сообщение_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name,
                       'Адрес': address, 'Доверенность': dover,
                       'ФИО_сотрудника': sotrudnik, 'Должность_банк': dolzhnost_bank,
                       'Должность_банк_полн': dolzhnost_bank_poln, 'Дата': date, }
            doc8.render(context)
            doc8.save(dirname_IP + "/Сообщение_ИП.docx")

            # Заявка ЭБ
            doc9 = DocxTemplate(dirname + "/Заявка_ЭБ_ИП.docx")
            context = {'Полное_наименование': fullname, 'Руководитель': name, 'ИНН': inn}
            doc9.render(context)
            doc9.save(dirname_IP + "/Заявка_ЭБ_ИП.docx")

            # # FATCA
            # wb = openpyxl.load_workbook(dirname + "\\\FATCA.xlsx")
            # sheet = wb.active
            # wb.save(dirname_IP + "\\\FATCA.xlsx")
            # wb.close
        except BaseException as e:
            raise  BaseException("Ошибка обрабтки данных")

class N:
    def get_data(self, text):
        raise FileExistsError("Ошибка выбора файла")


class UL:  # класс для юридического лица
    def __init__(self):
        self.name = '???'
        self.name_sokr = '???'
        self.name_en = '???'
        self.name_en_sokr = '???'
        self.inn = '???'
        self.ogrn = '???'
        self.director = '???'
        self.dolzhnost = '???'
        self.telephone = '???'
        self.date = '???'
        self.index_p = '???'
        self.kpp = '???'
        self.okpo = '???'
        self.okved = '???'
        self.dop_okved = '???'
        self.email = '???'
        self.address_ustav = '???'
        self.address = '???'
        self.uchastnik = '???'
        self.uchastnik_d1 = '???'
        self.l_date = '???'
        self.l_nomer = '???'
        self.l_vid = '???'
        self.l_vid_shablon = '???'
        self.l_organ = '???'
        self.capital = '???'
        self.inn_dir = '???'
        self.domen = '???'
        self.bank = '???'

        self.res = ''
        self.list_data = ''

    def get_data(self, text):  # поиск значений в тексте
        try:
            self.name = re.search('(?<=Полное наименование на русском языке\n)(.|\n)+?(?=\n\d+\n)', text)[0]
            self.name = self.name.replace('\n', ' ')
            self.name = self.name.replace('ОБЩЕСТВО С ОГРАНИЧЕННОЙ ОТВЕТСТВЕННОСТЬЮ', 'Общество с ограниченной ответственностью')
            self.name_sokr = re.search('(?<=Сокращенное наименование на русском\nязыке\n)(.|\n)+?(?=\n\d+\n)', text)[0]
            self.name_en = ""  # значение по умолчанию
            if re.search('(?<=Полное наименование на английском языке )(.|\n)+?(?=\n\d+\n)', text) is not None:
                self.name_en = re.search('(?<=Полное наименование на английском языке )(.|\n)+?(?=\n\d+\n)', text)[0]
                self.name_en = self.name_en.replace('\n', ' ')
            self.name_en_sokr = ""  # значение по умолчанию
            if re.search('(?<=Сокращенное наименование на английском\nязыке\n)(.|\n)+?(?=\n\d+\n)',
                         text) is not None:
                self.name_en_sokr = \
                re.search('(?<=Сокращенное наименование на английском\nязыке\n)(.|\n)+?(?=\n\d+\n)', text)[0]
                self.name_en_sokr = self.name_en_sokr.replace('\n', ' ')

            self.inn = re.findall('ИНН юридического лица\n+(.+)', text)[0]
            self.ogrn = re.findall('ОГРН\n+(.+)', text)[0]

            self.director = re.findall('Фамилия\n+(.+)+\n+(.+)+\n+(.+)', text)[0]
            self.director = ' '.join(self.director)
            self.director = self.director.lower().split(' ')
            self.director[0] = self.director[0].capitalize()
            self.director[1] = self.director[1].capitalize()
            self.director[2] = self.director[2].capitalize()
            self.director = ' '.join(self.director)
            self.dolzhnost = re.findall('Должность\n+(.+)', text)[0]
            self.inn_dir = re.findall('ИНН\n+(.+)', text)[0]

            self.date = re.findall('Дата регистрации\n+(.+)', text)[0]
            # self.index_p = re.findall('Адрес юридического лица\n+(\d{6})', text)[0]
            self.kpp = re.findall('КПП юридического лица\n+(.+)', text)[0]

            self.okved = ""  # значение по умолчанию
            if match := re.search('(?<=Код и наименование вида деятельности\n)(.|\n)+?(?=\n\d+\n)', text):
                self.okved = match[0].replace('\n', ' ')
            self.dop_okved = ""  # значение по умолчанию
            dop_okved_shablon = re.findall(r'(?<=Код и наименование вида деятельности\n).+\n?\D+(?=\n\d+\n)', text)
            self.dop_okved = '\n'.join(i.replace('\n', ' ') for i in dop_okved_shablon)
            self.address_ustav = ""  # значение по умолчанию
            if match := re.search('(?<=Место нахождения юридического лица\n)(.|\n)+?(?=\n\d+\n)', text):
                self.address_ustav = match[0].replace('\n', ' ')
            self.address = ""  # значение по умолчанию
            if match := re.search('(?<=Адрес юридического лица\n)(.|\n)+?(?=\n\d+\n)', text):
                self.address = match[0].replace('\n', ' ')
            self.capital = re.findall('Размер \(в рублях\)\n+(.+)', text)[0]

            self.uchastnik = ""  # значение по умолчанию
            uchastnik_shablon = re.compile('Фамилия\n+(.+)\n+(.+)\n+(.+)\n')
            self.uchastnik = (uchastnik_shablon.findall(text))
            a = []
            for i in range(1, len(self.uchastnik)):
                self.uchastnik = (uchastnik_shablon.findall(text)[i])
                a.append(' '.join(self.uchastnik))

            self.uchastnik_d = ""  # значение по умолчанию
            uchastnik_d_shablon = re.compile('Размер доли \(в процентах\)\n+(.+)')
            self.uchastnik_d = (uchastnik_d_shablon.findall(text))
            b = []  # список со значениями долей участников
            for j in range(len(self.uchastnik_d)):
                self.uchastnik_d = (uchastnik_d_shablon.findall(text)[j])
                b.append(''.join(self.uchastnik_d))

            self.uchastnik_d1 = [' - '.join(x) for x in zip(a, b)]  # Объединение 2 строк в список
            self.uchastnik_d1 = (" ".join(self.uchastnik_d1))

            self.l_date = ""  # значение по умолчанию
            self.l_nomer = ""  # значение по умолчанию
            self.l_vid = ""  # значение по умолчанию
            self.l_organ = ""  # значение по умолчанию
            if re.search('(?<=Наименование лицензирующего органа\n)[a-zA-Zа-яёА-ЯЁ ,\n]*(?=\n\d+\n)',text) is not None:
                self.l_organ = re.search('(?<=Наименование лицензирующего органа\n)[a-zA-Zа-яёА-ЯЁ ,\n]*(?=\n\d+\n)', text)[0]
                self.l_organ = self.l_organ.replace('\n', ' ')
            if re.search('(?<=деятельности, на который выдана лицензия\n)[a-zA-Zа-яёА-ЯЁ\(-\),\n]*(?=\n\d+\n)',text) is not None:
                self.l_vid = re.search('(?<=деятельности, на который выдана лицензия\n)[a-zA-Zа-яёА-ЯЁ ,\n]*(?=\n\d+\n)', text)[0]
                self.l_vid = self.l_vid.replace('\n', ' ')
            if re.search('(?<=Серия и номер лицензии\n)+(.+)', text) is not None:
                self.l_nomer = re.search('(?<=Серия и номер лицензии\n)+(.+)', text)[0]
            if re.search('(?<=Дата лицензии\n)+(.+)', text) is not None:
                self.l_date = re.search('(?<=Дата лицензии\n)+(.+)', text)[0]
        except BaseException as e:
            raise RuntimeError("Ошибка получения данных ЮЛ")

    def save_to_db(self):
        # Сохранение данных в БД
        try:
            connection = sqlite3.connect('text.sqlite')  # Создание или подключение к БД
            q = connection.cursor()  # Создание курсора для работы с БД
        except BaseException as e:
            raise RuntimeError("Ошибка подключения к БД ЮЛ")
        sql = "SELECT EXISTS(SELECT * FROM UL where ИНН = ?)"
        q.execute(sql, (self.inn,))
        self.res = q.fetchall()
        self.list_data = list(self.res[0])[0]
        connection.close()

    def checkIfExist(self):
        if self.list_data == 1:
            conn = sqlite3.connect('text.sqlite')
            q = conn.cursor()
            sql = f'SELECT * FROM UL where ИНН={self.inn}'
            q.execute(sql)
            res = q.fetchall()[0]
            q.close()
            self.telephone = res[10]
            self.email = res[17]
            self.domen = res[22]
            self.bank = res[23]
            self.okpo = res[14]
            return [self.telephone, self.email, self.domen, self.bank, self.okpo]
        return False

    def update(self, data):
        self.telephone = data['telephone']
        self.email = data['email']
        self.domen = data['domen']
        self.bank = data['bank']
        self.okpo = data['okpo']

        try:
            connection = sqlite3.connect('text.sqlite')  # Создание или подключение к БД
            q = connection.cursor()  # Создание курсора для работы с БД
        except BaseException as e:
            raise RuntimeError("Ошибка подключения к БД ЮЛ")
        sql = "SELECT EXISTS(SELECT * FROM UL where ИНН = ?)"
        q.execute(sql, (self.inn,))
        q.execute("INSERT INTO UL (Полное_наименование, Сокращенное_наименование, Полное_наименование_анг, Сокращенное_наименование_анг, ИНН, ОГРН, Руководитель, ИНН_директора, Должность, Телефон, Дата, Индекс, КПП, ОКПО, ОКВЭД, ДОП_ОКВЭДЫ, Эл_почта, Адрес_устав, Адрес, Участники, Капитал, Адрес_сайта, Банк, Вид_Л, Номер_Л, Дата_Л, Орган_Л) "
            "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
            % (self.name, self.name_sokr, self.name_en, self.name_en_sokr, self.inn, self.ogrn, self.director, self.inn_dir, self.dolzhnost,
            self.telephone, self.date, self.index_p, self.kpp, self.okpo, self.okved, self.dop_okved, self.email, self.address_ustav, self.address,
            self.uchastnik_d1, self.capital, self.domen, self.bank, self.l_vid, self.l_nomer, self.l_date, self.l_organ))
        connection.commit()

class IP:  # класс для индивидуального предпринимателя
    def __init__(self):
        self.name = '???'
        self.fullname = '???'
        self.inn = '???'
        self.ogrnip = '???'
        self.telephone = '???'
        self.date = '???'
        self.okved = '???'
        self.dop_okved = '???'
        self.email = '???'
        self.address = '???'
        self.domen = '???'
        self.bank = '???'

    def get_data(self, text):  # поиск значений в тексте
        try:
            self.name = re.search(r'(?<=Отчество\n).+\n?\D+(?=\n\d+\n)', text)[0]
            self.name = self.name.replace('\n', ' ')

            self.name = self.name.lower().split(' ')
            self.name[0] = self.name[0].capitalize()
            self.name[1] = self.name[1].capitalize()
            self.name[2] = self.name[2].capitalize()
            self.name = ' '.join(self.name)
            self.fullname = 'Индивидуальный предприниматель ' + self.name
            self.inn = re.findall('ИНН\)\n+(.+)', text)[0]
            self.ogrnip = re.findall('ОГРНИП\n+(.+)', text)[0]
            self.date = re.findall('Дата регистрации\n+(.+)', text)[0]
            self.okved = ""  # значение по умолчанию
            if match := re.search('(?<=Код и наименование вида деятельности\n)(.|\n)+?(?=\n\d+\n)', text):
                self.okved = match[0].replace('\n', ' ')
            dop_okved_shablon = re.findall(r'(?<=Код и наименование вида деятельности\n).+\n?\D+(?=\n\d+\n)', text)
            self.dop_okved = '\n'.join(i.replace('\n', '') for i in dop_okved_shablon)
        except BaseException as e:
            raise BaseException("Ошибка получения данных ИП")

    def save_to_db(self):
        # Сохранение данных в БД
        try:
            connection = sqlite3.connect('text.sqlite')  # Создание или подключение к БД
            q = connection.cursor()  # Создание курсора для работы с БД
        except BaseException as e:
            raise BaseException("Ошибка подключения к БД ИП")
        sql = "SELECT EXISTS(SELECT * FROM IP where ИНН = ?)"
        q.execute(sql, (self.inn,))
        self.res = q.fetchall()
        self.list_data = list(self.res[0])[0]

    def checkIfExist(self):
        if self.list_data == 1:
            conn = sqlite3.connect('text.sqlite')
            q = conn.cursor()
            sql = f'SELECT * FROM IP where ИНН={self.inn}'
            q.execute(sql)
            res = q.fetchall()[0]
            q.close()
            self.address = res[9]
            self.telephone = res[4]
            self.email = res[8]
            self.domen = res[10]
            self.bank = res[11]
            return [self.address, self.telephone, self.email, self.domen, self.bank]
        return False

    def update(self, data):
        self.address = data['adress']
        self.telephone = data['telephone']
        self.email = data['email']
        self.domen = data['domen']
        self.bank = data['bank']

        try:
            connection = sqlite3.connect('text.sqlite')  # Создание или подключение к БД
            q = connection.cursor()  # Создание курсора для работы с БД
        except BaseException as e:
            raise RuntimeError("Ошибка подключения к БД ИП")
        sql = "SELECT EXISTS(SELECT * FROM IP where ИНН = ?)"
        q.execute(sql, (self.inn,))
        q.execute("INSERT INTO IP (Наименование, ИНН, ОГРНИП, Телефон, Дата, ОКВЭД, ДОП_ОКВЭДЫ, Эл_почта, Адрес, Адрес_сайта, Банк) "
                "VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')"
                % (self.fullname, self.inn, self.ogrnip, self.telephone, self.date, self.okved, self.dop_okved,
                   self.email, self.address, self.domen, self.bank))
        connection.commit()
