from flask_login import UserMixin


class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        """При создании юзера в декораторе user_loader """
        self.__user = db.getUser(user_id)
        return self

    def create(self, user):
        """Когда юзер авторизуется на сайте"""
        self.__user = user
        return self

    def get_id(self):
        return str(self.__user['id'])
