import sqlite3

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.connection.isolation_level = None
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status = True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscribers` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscribers` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_subscriber(self, user_id, latitude, longitude, status = True):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscribers` (`user_id`, `status`, 'latitude', 'longitude') VALUES(?,?,?,?)", (user_id,status, latitude, longitude))

    def update_subscription(self, user_id, status):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `subscribers` SET `status` = ? WHERE `user_id` = ?", (status, user_id,))

    def coord_exists(self, latitude, longitude):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscribers` WHERE `latitude` = ? AND `longitude` = ?', (latitude,longitude,)).fetchall()
            return bool(len(result))    

    def coord_give(self, user_id):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscribers` WHERE `user_id` = ?', (user_id,)).fetchall()
            return result
        
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()