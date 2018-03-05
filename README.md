# semrush-test-task
simple TCP server

# Задание
Задание состоит из двух частей.

1. Нужно написать tcp сервер, который при старте открывает и слушает указанный порт.
В данный порт можно прислать сообщение вида $header$body, где header это структура вида (в python: Q 16s I I)
```
struct header {
   uint64_t size;
   char key[16];
   uint32_t magic;
   uint32_t rsv;
} __attribute__((packed));
```

а $body это bson размером, который указан в header (поле size), в bson должны быть 2 поля a1 (int64) и b (int64).
Сервер должен отвечать таким же сообщением, только bson должен содеражть поле sum (int64), в котором соответсвенно результат a + b.
В запросе key должен быть "sum", а в ответе "result", magic = 0xAA34529A, а rsv всегда равно 0.
Соответсвенно, сервер на каждое сообщение должен отвечать, сообщений можно слать сколько угодно в одно соединение.

2. Нужно написать тесты для этого сервера. Как, что, какие случаи проверять, сколько тестов, на ваше усмотрение.


# Реализация
Для реализации tcp-сервера использован python3.6 с модулем asyncio. Для проверки проверки работы сделан простой клиент содержащий тестовые данные.

#Запуск
Активировать виртуальное окружение:
```
source venv/bin/activate
```

Запустить сервер
```
python server.py
```
так же возможно запустить сервер с указанием порта (по умолчанию 8888):
```
python server.py 7777
```

Запустить клиент
```
python client.py
```

#Тестирование
В клиенте находится список тестовых данных test_data, сначала идут успешные случаи, затем неуспешные.
В консоли запущенного сервиса видно все входящие, исходящие данные, а так же возникающие ошибки.

Поскольку в задании отстутствуют требования по нагрузке, реализацию нагрузочного тестирования я опустил.
(можно реализовать с помощью Jmeter или написать специальный клиент, для реализации я бы выбрал concurrent.futures который позволил бы асинхронно и многопоточно отправлять запросы)



