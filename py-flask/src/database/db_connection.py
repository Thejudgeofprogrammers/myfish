import os # Импортируем os для того чтобы взять данные из env от докера
from motor.motor_asyncio import AsyncIOMotorClient # импортируем модуль для асинхронного поведения функциии

async def get_db(): # Функция для подключение к бд mongodb
    try:
        uri = os.getenv('ME_CONFIG_MONGODB_URL') or 'mongodb://root:example@mongo:27017/' # адрес подключения
        client = AsyncIOMotorClient(uri) # создание клиента для взаимодействия с бд
        await client.admin.command('ping') # Проверяем, что подключение установлено
        print('Подключение к MongoDB успешно установлено')
        return client # Возвращаем client
    except Exception as err: # Отлавливаем ошибку Exception
        print('Ошибка при подключении к MongoDB:', err)
        raise err