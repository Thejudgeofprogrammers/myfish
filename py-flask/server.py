from quart import Quart, render_template, request, redirect, url_for, abort # импорт функций и класса для асинхронной работы сервера
from bson import ObjectId # импорт ObjectId для работы с mongodb
import json # импорт json

from src.database.db_connection import get_db # Импорт функции для подключения к базе данных mongodb

app = Quart(__name__, static_url_path='/static') # Подключение статических файлов

class JSONEncoder(json.JSONEncoder): # создаём класс, который наследуется от json.JSONEncoder
    """Преобразования ObjectId в строку"""
    def default(self, item):
        if isinstance(item, ObjectId): # проверка на то что является ли item экземпляром класса ObjectId
            return str(item) # возвращаем строкой ObjectId
        return super(JSONEncoder, self).default(item) # Преобразовываем в ObjectId
    
    
app.json_encoder = JSONEncoder # Ставим кодировку всему нажему серверу для работы с json, и ObjectId


@app.errorhandler(404) # роут для перенаправления в случае ошибки
async def page_not_found(error):
    return await render_template('error404.html'), 404 # рендер страницы со статус кодом 404


@app.route('/') # роут для главной страницы сайта
async def index():
    return await render_template('index.html') # рендер главной страницы


@app.route('/about') # роут для рендера страницы о нас
async def about():
    return await render_template('about.html')


@app.route('/contact') # роут для рендера контактов
async def contact():
    return await render_template('contact.html') # роут для рендера страницы контактов


@app.route('/create', methods=['GET', 'POST']) # роут для рендера и принятия данных POST, для создания записи
async def create_item(): # Функция создания записи
    if request.method == 'POST': # Если мы нажимаем Кнопку submit на фронтенде, то данные идут по методу POST
        try:
            data = await request.form # берём данные из формы после нажатия submit кнопки
            name = data.get('name')  # Берём поле name из формы
            price = data.get('price') # Берём поле price из формы
            desc = data.get('desc') # Берём поле desc из формы

            client = await get_db() # Обращаемся к базе данных mongo через функцию, в другом файле
            db = client['myFish'] # обращаемся к базе данных с названием myFish
            collection = db['myFish'] # обращаемся к коллекции myFish, которая находится в бд myFish

            new_product = {  # Заполняем данные по форме
                'name': name,
                'price': price,
                'desc': desc
            }
            await collection.insert_one(new_product) # Добавляем в базу данных сформированную запись

            return redirect(url_for('content')) # И перенаправляем пользователя на content.html
        except Exception as err: # Отлавливаем ошибку Exception
            print(err) # выводим ошибку
            return abort(404) # Переадресация на error404.html если ошибка есть

    return await render_template('create.html') # если метод GET то рендерим страницу create.html


# Я не успел реализовать эту часть кода
@app.route('/registry', methods=['GET', 'POST'])
async def registry():
    if request.method == 'POST':
        username = (await request.form)['username']
        email = (await request.form)['email']
        password = (await request.form)['password']
        return redirect(url_for('login'))
    return await render_template('registry.html')


# Я не успел реализовать эту часть кода
@app.route('/login', methods=['GET', 'POST'])
async def login():
    if request.method == 'POST':
        username = (await request.form)['username']
        password = (await request.form)['password']
        return redirect(url_for('index'))
    return await render_template('login.html')


@app.route('/content') # url всех записей
async def content(): # Функция для выведения записей на сайте
    try:
        client = await get_db() # Обращаемся к базе данных mongo через функцию, в другом файле
        db = client['myFish'] # обращаемся к базе данных с названием myFish
        collection = db['myFish'] # обращаемся к коллекции myFish, которая находится в бд myFish

        cursor = collection.find({}) # Находим все записи в коллекции без фильтра
        products = await cursor.to_list(length=None) # итерируем коллекцию, для получения всех записей

        return await render_template('content.html', products=products) # рендерим страницу и передаём products

    except Exception as err: # Отлавливаем ошибку Exception
        print(f"Error: {err}")  # Выводим ошибку для отладки
        return await abort(404) # Переадресация на error404.html
    

@app.route('/update/<string:_id>', methods=['GET', 'POST']) # url для изменения записи по ObjectId, с методами GET POST
async def update_item(_id): # Изменяем запись по ObjectId
    try:
        client = await get_db() # Обращаемся к базе данных mongo через функцию, в другом файле
        db = client['myFish'] # обращаемся к базе данных с названием myFish
        collection = db['myFish'] # обращаемся к коллекции myFish, которая находится в бд myFish

        if request.method == 'POST': # метод пост означает что бы получаем данные с клиенсткой части на сервер
            data = await request.form # берём данные из формы после нажатия submit кнопки
            name = data.get('name')  # Берём поле name из формы
            price = data.get('price') # Берём поле price из формы
            desc = data.get('desc') # Берём поле desc из формы

            updated_product = { # Заполняем данные по форме
                'name': name,
                'price': price,
                'desc': desc
            }
            # изменяем запись по ObjectId а данные которые мы изменили $set: updated_product
            await collection.update_one({'_id': ObjectId(_id)}, {'$set': updated_product})
            return redirect(url_for('content')) # Перенаправляет на content.html

        product = await collection.find_one({'_id': ObjectId(_id)}) # ищет запись по ObjectId
        if not product: # Проверяем есть ли запись или нет
            return abort(404) # Переадресация на error404.html

        product['_id'] = str(product['_id']) # Преобразует ObjectId в строку
        return await render_template('update.html', product=product) # рендерим страницу передавая ей product
    except Exception as err: # Обработчик ошибки Exception
        print(f"Error: {err}") # вывод ошибки
        return abort(404) # Переадресация на error404.html


@app.route('/content/<string:_id>') # url для просмотра страницы по ObjectId
async def content_detail(_id): # Функция для просмотра записи по ObjectId
    try:
        client = await get_db() # Обращаемся к базе данных mongo через функцию, в другом файле
        db = client['myFish'] # обращаемся к базе данных с названием myFish
        collection = db['myFish'] # обращаемся к коллекции myFish, которая находится в бд myFish

        if not ObjectId.is_valid(_id): # проверяем валидацию то что это точно ObjectId
            return await abort(404) # Переадресация на error404.html

        product = await collection.find_one({"_id": ObjectId(_id)}) # находим запись в mongodb по ObjectId
        if product:
            product['_id'] = str(product['_id'])  # Преобразуем ObjectId в строку
            return await render_template('content_detail.html', product=product) # рендерим страницу передавая ей product
        else:
            return await abort(404) # Переадресация на error404.html
    except Exception as err: # Обработчик ошибки Exception
        print(f"Error: {err}")  # Выводим ошибку для отладки
        return await abort(404) # Переадресация на error404.html


@app.route('/delete/<string:_id>') # Url для удаление по ObjectId
async def delete_product(_id): # Функция удаление элемента, принимает ObjectId
    try:
        client = await get_db() # Обращаемся к базе данных mongo через функцию, в другом файле
        db = client['myFish'] # обращаемся к базе данных с названием myFish
        collection = db['myFish'] # обращаемся к коллекции myFish, которая находится в бд myFish
        
        if not ObjectId.is_valid(_id): # проверяем валидацию то что это точно ObjectId
            return await abort(404) # Переадресация на error404

        result = await collection.delete_one({'_id': ObjectId(_id)}) # обращается к коллекции и удаляет запись из базы данных

        if result.deleted_count == 1: # Проверяем, был ли удален продукт
            return redirect(url_for('content')) # Перенаправляем на content.html
        else:
            # Продукт не был найден, возможно, уже был удален
            return await abort(404) # Переадресация на error404
    except Exception as err: # Обработчик ошибки Exception
        print(f"Error: {err}")  # Выводим ошибку для отладки
        return await abort(404) # Переадресация на error404


# вообще это middleware функция, промежуточное ПО между выполнением запроса, как в Node.js
@app.after_request # Применяем ко всем роутам
async def add_header(response): # асинхронный вызов, принимаем ответ в качестве аргумента
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0' # Применяем к headers 
    response.headers['Pragma'] = 'no-cache' # Убираем кеширование с сайта
    response.headers['Expires'] = '0'
    return response # результат для кадого роута


if __name__ == "__main__": # выполняем код внутри этого условия
    app.run(debug=False, host='0.0.0.0') # запускаем локально приложение

