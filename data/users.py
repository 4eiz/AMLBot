import aiosqlite
import random
import string

class User:
    path = 'data/base/base.db'

    def __init__(self, user_id, data=None):
        self.user_id = user_id
        self.data = data  # Данные пользователя
        if data:
            self.bought_checks = data['bought_checks']
            self.free_checks = data['free_checks']
            self.referrer_id = data['referrer_id']
            self.ref_code = data['ref_code']
            self.lang = data['lang'] if 'lang' in data else 'en'  # Пример значения по умолчанию
        else:
            # Устанавливаем значения по умолчанию, если данные отсутствуют
            self.bought_checks = 0
            self.free_checks = 0
            self.referrer_id = None
            self.ref_code = None
            self.lang = 'en'

    @classmethod
    async def create(cls, user_id, ref_code=None):
        """
        Асинхронный фабричный метод для создания объекта User с загруженными данными.
        Если пользователя нет в базе данных, он будет создан.
        
        :param user_id: ID пользователя.
        :param ref_code: Реферальный код (опционально).
        :return: Кортеж (объект User, ID реферера), если реферер найден, иначе только объект User.
        """
        data = await cls.get_user_data(user_id)
        if data is None:
            # Если пользователя нет, создаем его
            referrer_id = await cls.get_referrer_id_by_code(ref_code) if ref_code else None
            await cls.create_user_if_not_exists(user_id, referrer_id)
            data = await cls.get_user_data(user_id)  # Получаем данные после создания

        # Создаем объект User
        user = cls(user_id, data)

        # Если был указан реферальный код и найден реферер, возвращаем и объект User, и ID реферера
        if ref_code and 'referrer_id' in data and data['referrer_id']:
            return user, data['referrer_id']

        # Иначе возвращаем только объект User
        return user,

    @classmethod
    async def get_user_data(cls, user_id):
        """
        Возвращает словарь с данными пользователя из таблицы users.
        
        :param user_id: ID пользователя, данные которого нужно получить.
        :return: Словарь с данными пользователя.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                SELECT 
                    user_id, 
                    bought_checks, 
                    free_checks, 
                    referrer_id, 
                    ref_code,
                    lang
                FROM users
                WHERE user_id = ?
            '''
            async with db.execute(query, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return {
                        "user_id": row[0],          # ID пользователя
                        "bought_checks": row[1],    # Количество купленных проверок
                        "free_checks": row[2],      # Количество бесплатных проверок
                        "referrer_id": row[3],      # ID реферера
                        "ref_code": row[4],         # Реферальный код
                        "lang": row[5],            # Язык пользователя
                    }
                return None  # Если пользователь не найден

    @classmethod
    async def get_referrer_id_by_code(cls, ref_code):
        """
        Находит ID реферера по его реферальному коду.
        
        :param ref_code: Реферальный код.
        :return: ID реферера или None, если код не найден.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                SELECT user_id
                FROM users
                WHERE ref_code = ?
            '''
            async with db.execute(query, (ref_code,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return row[0]  # Возвращаем ID реферера
                return None  # Если код не найден


    @classmethod
    async def create_user_if_not_exists(cls, user_id, referrer_id=None):
        """
        Создает нового пользователя в базе данных, если его там нет.
        Также создает запись о скидках пользователя в таблице user_discounts.

        :param user_id: ID пользователя.
        :param referrer_id: ID реферера (опционально).
        :raises: Exception, если не удалось создать пользователя или скидку.
        """
        async with aiosqlite.connect(cls.path) as db:
            # Проверяем, существует ли пользователь
            query_check = '''
                SELECT user_id
                FROM users
                WHERE user_id = ?
            '''
            async with db.execute(query_check, (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return  # Пользователь уже существует

            # Генерируем уникальный реферальный код
            ref_code = cls.generate_ref_code()

            # Создаем нового пользователя
            query_insert_user = '''
                INSERT INTO users (
                    user_id, 
                    bought_checks, 
                    free_checks, 
                    referrer_id, 
                    ref_code,
                    lang
                )
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            try:
                await db.execute(query_insert_user, (user_id, 0, 0, referrer_id, ref_code, 'en'))
                await db.commit()
            except Exception as e:
                raise Exception(f"Ошибка при создании пользователя: {e}")

            # Создаем запись о скидках пользователя
            query_insert_discount = '''
                INSERT INTO user_discounts (
                    user_id, 
                    discount_percent
                )
                VALUES (?, ?)
            '''
            try:
                await db.execute(query_insert_discount, (user_id, 0.0))  # Начальная скидка 0%
                await db.commit()
            except Exception as e:
                raise Exception(f"Ошибка при создании записи о скидках: {e}")


    @staticmethod
    def generate_ref_code(length=8):
        """
        Генерирует уникальный реферальный код.
        
        :param length: Длина кода.
        :return: Уникальный реферальный код.
        """
        characters = string.ascii_letters + string.digits  # Буквы и цифры
        return ''.join(random.choice(characters) for _ in range(length))

    async def deduct_checks(self):
        """
        Списывает проверки у пользователя. Сначала списывает бесплатные, затем платные.
        
        :return: Кортеж (успех, сообщение). Если успех False, сообщение содержит ошибку.
        """
        async with aiosqlite.connect(self.path) as db:
            # Получаем текущие данные пользователя
            query = '''
                SELECT free_checks, bought_checks
                FROM users
                WHERE user_id = ?
            '''
            async with db.execute(query, (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return False, "Пользователь не найден."

                free_checks = row[0]
                bought_checks = row[1]

                # Если есть бесплатные проверки, списываем их
                if free_checks > 0:
                    new_free_checks = free_checks - 1
                    update_query = '''
                        UPDATE users
                        SET free_checks = ?
                        WHERE user_id = ?
                    '''
                    await db.execute(update_query, (new_free_checks, self.user_id))
                    await db.commit()
                    return True, "Списана 1 бесплатная проверка."

                # Если есть платные проверки, списываем их
                elif bought_checks > 0:
                    new_bought_checks = bought_checks - 1
                    update_query = '''
                        UPDATE users
                        SET bought_checks = ?
                        WHERE user_id = ?
                    '''
                    await db.execute(update_query, (new_bought_checks, self.user_id))
                    await db.commit()
                    return True, "Списана 1 платная проверка."

                # Если проверок нет, возвращаем ошибку
                else:
                    raise Exception("Недостаточно проверок для списания.")
                
    async def count_referrals(self):
        """
        Возвращает количество рефералов пользователя.
        
        :return: Количество рефералов.
        """
        async with aiosqlite.connect(self.path) as db:
            query = '''
                SELECT COUNT(*)
                FROM users
                WHERE referrer_id = ?
            '''
            async with db.execute(query, (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else 0

    async def give_free_check(self):
        """
        Выдает пользователю бесплатную проверку, если у него меньше 5 рефералов.
        
        :return: Кортеж (успех, сообщение). Если успех False, сообщение содержит ошибку.
        """
        async with aiosqlite.connect(self.path) as db:
            # Проверяем количество рефералов
            referral_count = await self.count_referrals()
            if referral_count >= 5:
                return False, "У пользователя уже 5 или более рефералов. Бесплатная проверка не выдана."

            # Выдаем бесплатную проверку
            update_query = '''
                UPDATE users
                SET free_checks = free_checks + 1
                WHERE user_id = ?
            '''
            await db.execute(update_query, (self.user_id,))
            await db.commit()
            return True, "Бесплатная проверка успешно выдана."


    async def update_language(self, new_lang):
        """
        Обновляет язык пользователя в базе данных.
        
        :param new_lang: Новый язык пользователя.
        :return: Кортеж (успех, сообщение). Если успех False, сообщение содержит ошибку.
        """
        async with aiosqlite.connect(self.path) as db:
            try:
                # Обновляем язык пользователя
                update_query = '''
                    UPDATE users
                    SET lang = ?
                    WHERE user_id = ?
                '''
                await db.execute(update_query, (new_lang, self.user_id))
                await db.commit()

                # Обновляем данные в объекте
                if self.data:
                    self.data['lang'] = new_lang
                    self.lang = new_lang

                return True, "Язык успешно обновлен."
            except Exception as e:
                return False, f"Ошибка при обновлении языка: {e}"
            

    async def update_balance(self, amount, balance_type="bought_checks"):
        """
        Обновляет баланс пользователя в базе данных.
        
        :param amount: Количество проверок для добавления или списания (может быть отрицательным).
        :param balance_type: Тип баланса ("bought_checks" или "free_checks").
        :return: Кортеж (успех, сообщение). Если успех False, сообщение содержит ошибку.
        """
        async with aiosqlite.connect(self.path) as db:
            try:
                # Проверяем, что тип баланса корректен
                if balance_type not in ["bought_checks", "free_checks"]:
                    return False, "Некорректный тип баланса."

                # Получаем текущий баланс
                query = f'''
                    SELECT {balance_type}
                    FROM users
                    WHERE user_id = ?
                '''
                async with db.execute(query, (self.user_id,)) as cursor:
                    row = await cursor.fetchone()
                    if not row:
                        return False, "Пользователь не найден."

                    current_balance = row[0]

                # Проверяем, достаточно ли средств для списания (если amount отрицательный)
                if amount < 0 and current_balance + amount < 0:
                    raise Exception('Недостаточно баланса')

                # Обновляем баланс
                update_query = f'''
                    UPDATE users
                    SET {balance_type} = {balance_type} + ?
                    WHERE user_id = ?
                '''
                await db.execute(update_query, (amount, self.user_id))
                await db.commit()

                # Обновляем данные в объекте
                if self.data:
                    self.data[balance_type] = current_balance + amount
                    if balance_type == "bought_checks":
                        self.bought_checks = current_balance + amount
                    elif balance_type == "free_checks":
                        self.free_checks = current_balance + amount

                return True, "Баланс успешно обновлен."
            except Exception as e:
                raise Exception('Недостаточно баланса')
            
    @classmethod
    async def user_exists(cls, user_id):
        """
        Проверяет, существует ли пользователь в базе данных.
        
        :param user_id: ID пользователя.
        :return: True, если пользователь существует, иначе False.
        """
        async with aiosqlite.connect(cls.path) as db:
            query = '''
                SELECT user_id
                FROM users
                WHERE user_id = ?
            '''
            async with db.execute(query, (user_id,)) as cursor:
                row = await cursor.fetchone()
                return row is not None
            

    async def calculate_price(self, amount, price, min_price, count_to_reduce, discount_for_wholesale, promo_discount=None):
        """
        Рассчитывает общую стоимость с учетом скидок:
        - Скидка пользователя (из таблицы user_discounts).
        - Скидка по промокоду (если указана).
        - Оптовая скидка (с учетом интервалов и минимальной цены).

        :param amount: Количество штук.
        :param price: Цена за одну штуку.
        :param min_price: Минимальная цена за одну штуку.
        :param count_to_reduce: Интервал, раз в сколько единиц товара уменьшается цена.
        :param discount_for_wholesale: На сколько уменьшается цена за единицу при прохождении интервала.
        :param promo_discount: Скидка по промокоду (в процентах, опционально).
        :return: Итоговая стоимость с учетом всех скидок.
        """
        # Получаем скидку пользователя
        async with aiosqlite.connect(self.path) as db:
            query = '''
                SELECT discount_percent
                FROM user_discounts
                WHERE user_id = ?
            '''
            async with db.execute(query, (self.user_id,)) as cursor:
                row = await cursor.fetchone()
                user_discount = row[0] if row else 0.0  # Скидка пользователя в процентах

        # Шаг 1: Рассчитываем цену за единицу с учетом оптовой скидки
        # Количество интервалов
        intervals = amount // count_to_reduce
        # Цена за единицу с учетом оптовой скидки
        price_with_wholesale = price - (intervals * discount_for_wholesale)
        # Не позволяем цене опуститься ниже min_price
        price_with_wholesale = max(price_with_wholesale, min_price)

        # Шаг 2: Рассчитываем общую стоимость без учета скидок пользователя и промокода
        total_price = amount * price_with_wholesale

        # Шаг 3: Применяем скидку пользователя (если есть)
        if user_discount > 0:
            total_price *= (1 - user_discount / 100)

        # Шаг 4: Применяем скидку по промокоду (если указана)
        if promo_discount:
            total_price *= (1 - promo_discount / 100)

        # Возвращаем итоговую стоимость
        return total_price