import math
import re
import sqlite3
import time

from flask import url_for


class FDataBase:
    def __init__(self, db):
        """Создание БД"""
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        """Получение меню для шапки"""
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res:
                return res
        except:
            print("Ошибка чтения из БД")
        return []

    def addCar(self, title, text, url):
        """Добавлене авто в БД"""
        try:
            self.__cur.execute(
                f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Такой авто уже существует!')
                return False

            base = url_for('static', filename='images_html')
            text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>", "\\g<tag>"+base+"/\\g<url>>", res['text'])

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)",
                               (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления авто в БД "+str(e))
            return False

        return True

    def getCar(self, alias):
        """Получение объекта авто"""
        try:
            self.__cur.execute(
                f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                base = url_for('static', filename='images_html')
                text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>", "\\g<tag>"+base+"/\\g<url>>", res['text'])
                return (res['title'], text)
        except sqlite3.Error as e:
            print("Ошибка получения авто из БД " + str(e))

        return (False, False)

    def getCarsAnonce(self):
        """Получение свежих объектов авто для главной страницы"""
        try:
            self.__cur.execute(
                f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения авто из БД "+str(e))

        return []

    def addUser(self, name, email, hpsw):
        """Добавление объекта пользователь в БД"""
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute(
                "INSERT INTO users VALUES(NULL, ?, ?, ?, NULL, ?)",
                (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False

        return True

    def getUser(self, user_id):
        """Получение объекта пользователь"""
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД в getUser " + str(e))

        return False

    def getUserByEmail(self, email):
        """Поиск пользователя по email"""
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД в getUserByEmail " + str(e))

        return False

    def updateUserAvatar(self, avatar, user_id):
        """Обновление аватара пользователя"""
        if not avatar:
            return False

        try:
            binary = sqlite3.Binary(avatar)
            self.__cur.execute(f"UPDATE users SET avatar = ? WHERE id = ?", (binary, user_id))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка обновления аватара в БД: "+str(e))
            return False
        return True
