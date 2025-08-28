import aiosqlite
from datetime import datetime

class PromoCode:
    path = 'data/base/base.db'  # Путь к базе данных

    def __init__(self, promo_id, data=None):
        self.promo_id = promo_id
        self.data = data  # Данные промокода
        if data:
            self.promo_name = data['promo_name']
            self.discount_percent = data['discount_percent']
            self.expiration_date = data['expiration_date']
        else:
            # Устанавливаем значения по умолчанию, если данные отсутствуют
            self.promo_name = None
            self.discount_percent = 0.0
            self.expiration_date = None

    @classmethod
    async def create(cls, promo_name, discount_percent, expiration_date):
        """
        Создает новый промокод в базе данных.
        
        :param promo_name: Название промокода.
        :param discount_percent: Процент скидки.
        :param expiration_date: Дата истечения срока действия (в формате YYYY-MM-DD).
        :return: Объект PromoCode.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                INSERT INTO promo_codes (promo_name, discount_percent, expiration_date)
                VALUES (?, ?, ?)
            '''
            try:
                await db.execute(query, (promo_name, discount_percent, expiration_date))
                await db.commit()

                # Получаем ID созданного промокода
                cursor = await db.execute("SELECT last_insert_rowid()")
                row = await cursor.fetchone()
                promo_id = row[0]  # Извлекаем ID из результата

                return cls(promo_id, {
                    "promo_name": promo_name,
                    "discount_percent": discount_percent,
                    "expiration_date": expiration_date
                })
            except aiosqlite.IntegrityError:
                raise Exception("Промокод с таким именем уже существует.")
            except Exception as e:
                raise Exception(f"Ошибка при создании промокода: {e}")

    @classmethod
    async def get_by_name(cls, promo_name):
        """
        Получает информацию о промокоде по его названию.
        
        :param promo_name: Название промокода.
        :return: Объект PromoCode или None, если промокод не найден.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                SELECT promo_id, promo_name, discount_percent, expiration_date
                FROM promo_codes
                WHERE promo_name = ?
            '''
            async with db.execute(query, (promo_name,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return cls(row[0], {
                        "promo_name": row[1],
                        "discount_percent": row[2],
                        "expiration_date": row[3]
                    })
                return None

    async def activate(self):
        """
        Активирует промокод. Проверяет, не просрочен ли он.
        
        :return: Процент скидки, если промокод активен.
        :raises: Exception, если промокод просрочен.
        """
        expiration_date = datetime.strptime(self.expiration_date, "%Y-%m-%d")
        current_date = datetime.now()

        if current_date > expiration_date:
            raise Exception("Промокод просрочен.")

        return self.discount_percent

    @classmethod
    async def delete(cls, promo_name):
        """
        Удаляет промокод из базы данных по его названию.
        
        :param promo_name: Название промокода.
        :return: True, если промокод удален, иначе False.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                DELETE FROM promo_codes
                WHERE promo_name = ?
            '''
            async with db.execute(query, (promo_name,)) as cursor:
                await db.commit()
                return cursor.rowcount > 0

    @classmethod
    async def get_all(cls):
        """
        Получает все промокоды из базы данных.
        
        :return: Список объектов PromoCode.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                SELECT promo_id, promo_name, discount_percent, expiration_date
                FROM promo_codes
            '''
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                return [cls(row[0], {
                    "promo_name": row[1],
                    "discount_percent": row[2],
                    "expiration_date": row[3]
                }) for row in rows]
            

