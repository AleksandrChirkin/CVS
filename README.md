# CVS
Версия 1.0
Автор: Чиркин Александр(chirkin2001@list.ru)

## Описание
Данное приложение является реализацией базовых команд системы одновременных версий (Concurrent Versions System, CVS).
Позволяет хранить предыдущие версии файлов и, в случае необходимости, восстанавливать их.

## Требования
* Python версии не ниже 3.7

## Состав
* Точка входа: 'cvs.py'
* Команды: 'commands/#имя_команды'
* Репозиторий, где хранятся версии файлов и журнал('history.rcs'): 'repos/'. Изначально не имеется
* Тесты: 'testing/test_cvs.py'
* Файл покрытия: '.coverage'

## Запуск
* 'python3 cvs.py [аргументы CVS] команда CVS [аргументы команды]'
* Для запуска тестов введите 'python3 -m pytest --tb=line --cov=. .'

## Команды
* 'init' - создаёт репозиторий, если его нет
** 'init -r' - удаляет старый репозиторий и создает новый
* 'add' - добавляет файл в список на закрепление в репозиторий
* 'commit' - закрепление в репозиторий
* 'reset' - восстанавливает определенную версию файла из репозитория
* 'log' - выводит данные из журнала

## Подробности реализации
Репозиторий повторяет структуру текущей директории, но каждый файл представлен директорией, где лежат предыдущие версии этого файла.
Файл 'repos/history.rcs' содержит информацию о фактах создания файлов, добавления их в очередь на закрепление,
закрепления в репозиторий или восстановления из репозитория с указанием времени.

При вызове команды с ключом '-h' или '--help' открывается справка по соответствующей команде.