# django-cbrf

Приложение для удобной работы с валютами и курсами валют от ЦБ РФ

[![Build Status](https://github.com/egregors/django-cbrf/actions/workflows/test.yml/badge.svg)](https://github.com/egregors/django-cbrf/actions/workflows/test.yml)
[![PyPI version](https://badge.fury.io/py/django-cbrf.svg)](https://badge.fury.io/py/django-cbrf)

[Сайт](http://www.cbr.ru/) and [API](http://www.cbr.ru/scripts/Root.asp?PrtId=SXML) Центробанка.

## Установка

Для запуска необходимы:

* Python >= 3
* Django >= 3.8
* [cbrf](https://github.com/egregors/cbrf)

Установка из PyPI:
```
    pip install django-cbrf
```

Версия для разработчиков:
```
    git clone https://github.com/egregors/django-cbrf.git
    cd django-cbrf
    pip install -e .
```

Запуск тестов:
```
    cd django-cbrf/tests
    python manage.py test test_app
```

## Настройки

Добавить приложение в `INSTALLED_APPS`:

```
INSTALLED_APPS = (
    # ...
    'django_cbrf',
)
```

Доступные настройки:

```
# your settings.py

# приложение, где находятся собственные модели
# (опционально, по умолчанию "django_cbrf")
CBRF_APP_NAME = 'test_app'

# количество дней, для заполнения БД (будут получены котировки за последние CBRF_DAYS_FOR_POPULATE дней
# (опционально, по умолчанию 60 дней)
CBRF_DAYS_FOR_POPULATE = 30 
```

Пакет содержит готовые для использования модели `Currency` и `Record` в модуле `django_cbrf.models`, но вы можите
также использовать свои собственные модели, наследовав их от `AbstractCurrency` и `AbstractRecord` из `django_cbrf.abstract_models`.

Для использования собственных моделей необходимо в настройках указать приложение, в моделях которого находятся модели для 
валют и курсов:

Важно!

**Ваши собственные модели для валют и курсов должны называться точно `Currency` и `Record`**

## Команды manage.py

### Загрузка валют

Для того, что бы загрузить перечень существующих валют можно выполнить команду:

```
    python manage.py load_currency
```

в случае, если в БД нет ни одной записи модели `Currency`, эти записи будут загружены через API ЦБ.

Для загружки валют независимо от условий, используйте флаг `--force`

### Загрузка курсов

Чтобы загрузить историю курсов за указанное время необходимо выолнить команду `load_rates`.
В качестве параметров команда принимает перечень ISO кодов нужных валют, и опционально, количество 
дней за которые необходимо получить курсы. Например, для загрузки в БД историии курсов Доллара США и Евро
за последние 90 дней необходимо выполнить: 

```
    python manage.py load_rates usd eur --days 90
```

## Контрибьютинг

Сообщения об ошибках, исправления и новый функционал всегда преветствуются.
Открывайте issues, пуште пул реквесты.