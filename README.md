Этот проект представляет собой веб-приложение для управления задачами, созданное с использованием Django. 
Для запуска проекта в Docker-контейнере следуйте этим инструкциям.

## Требования

- Docker
- Docker Compose

1. Клонируйте репозиторий на вашу локальную машину:

git clone https://github.com/ushakovda/task_manager <br>
cd <папка-с-проектом>

2. Запустите проект с помощью docker compose up:

* docker compose down

Проект будет доступен по адресу http://localhost:8000. Откройте браузер на весь экран.
Ради примера сохранена БД sqlite, при необходимости файл db.sqlite3 можно удалить.

*Дата завершения отображается после обновления страницы/повторного открытия страницы описания конкретной задачи
