# YaTube :clapper:

## Описание:
_YaTube_ - социальная сеть, в которой пользователи могут писать посты, прикладывать фото к ним. Комментировать посты других пользователей. Подписываться на конкретных пользователей и просматривать посты авторов, на которых вы подписаны или посты всех пользователей. 

## Содержимое
* [Локальный запуск](#локальный-запуск)
* [Технологии](#технологии)
* [Авторы](#авторы)

## Локальный запуск
Клонировать репозиторий и перейти в него в командной строке:

```
git clone 
```

```
cd api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Использовать миграции:

```
python3 manage.py makemigrations
```

```
python3 manage.py migrate
```

Запуск:

```
python3 manage.py runserver
```

## Технологии:

 - Python 3.7 
 - Django 2.2.19
 - Djoser 2.1.0
 - Pillow 9.4.0

## Авторы
[Макаров Пётр](https://github.com/MakarovPetr2004)
