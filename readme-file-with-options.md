# Руководство по настройке и использованию скрипта

## Описание

Данный скрипт позволяет запускать две пользовательские команды одновременно с заданным таймаутом и сохранять их вывод в лог-файл. Скрипт идеально подходит для автоматизации задач, которые требуют параллельного выполнения команд с ограничением по времени.

Скрипт доступен в двух вариантах реализации:
1. **Монолитный вариант** - весь код находится в одном файле
2. **Модульный вариант** - код разделен на три файла для лучшей структуризации

## Требования к окружению

1. **Python 3.6 или выше**
   - Убедитесь, что Python установлен на вашей системе. Проверить можно командой:
     ```
     python --version
     ```

2. **Стандартные библиотеки Python**
   - Скрипт использует только стандартные библиотеки Python, поэтому дополнительная установка пакетов не требуется:
     - `subprocess` - для запуска внешних процессов
     - `os` - для работы с файловой системой
     - `threading` - для многопоточности
     - `time` - для работы с таймаутами
     - `json` - для работы с конфигурационным файлом
     - `queue` - для безопасного взаимодействия между потоками

## Варианты установки

### Вариант 1: Монолитный скрипт

1. **Сохраните скрипт** в файл с расширением `.py`, например `run_commands.py`
2. **Запустите** скрипт напрямую (см. раздел "Запуск скрипта")

### Вариант 2: Модульный скрипт

Для этого варианта необходимо создать три файла в одной директории:

1. **config.py** - содержит функции для работы с конфигурацией
2. **process.py** - содержит функции для запуска и мониторинга процессов
3. **main.py** - основной файл, объединяющий функциональность

#### Структура проекта:
```
project_folder/
├── config.py
├── process.py
├── main.py
└── config_file.json (создается автоматически)
```

## Запуск скрипта

### Для монолитного варианта:
- В Windows: 
  ```
  python путь\к\скрипту\run_commands.py
  ```
- В Linux/MacOS: 
  ```
  python3 путь/к/скрипту/run_commands.py
  ```

### Для модульного варианта:
- В Windows: 
  ```
  cd путь\к\директории\проекта
  python main.py
  ```
- В Linux/MacOS: 
  ```
  cd путь/к/директории/проекта
  python3 main.py
  ```

## Использование скрипта

1. **Запустите скрипт** как описано выше

2. **Введите команды** по запросу:
   - Скрипт попросит ввести две команды
   - Вводите команды в том виде, в котором они выполняются в командной строке
   - Примеры команд:
     - `ping google.com`
     - `ipconfig`
     - `dir`
     - `ls -la`

3. **Мониторинг выполнения**
   - Скрипт будет отображать статус выполнения команд в реальном времени
   - Если выполнение превысит заданный таймаут, процесс будет принудительно завершен

4. **Результаты выполнения**
   - После завершения всех процессов, скрипт выведет результаты в консоль
   - Все результаты также сохраняются в файл `program_output.log` в той же директории, где запущен скрипт

## Настройка таймаута

1. **Автоматический способ**
   - При первом запуске скрипт создает файл `config_file.json` с таймаутом по умолчанию (5 секунд)

2. **Ручной способ**
   - Откройте файл `config_file.json` в любом текстовом редакторе
   - Измените значение параметра `timeout` на нужное количество секунд:
     ```json
     {
         "settings": {
             "timeout": 20
         }
     }
     ```
   - Сохраните файл

## Содержимое файлов для модульного варианта

### config.py
Этот файл содержит функции для создания и чтения конфигурационного файла:

```python
import json
import os

CONFIG_FILE = "config_file.json"
DEFAULT_TIMEOUT = 10

def create_config():
    """Создает конфигурационный файл, если он не существует."""
    if not os.path.exists(CONFIG_FILE):
        defoult_config = {"settings": {"timeout": DEFAULT_TIMEOUT}}
        with open(CONFIG_FILE, "w") as f:
            json.dump(defoult_config, f, indent=4)
        print(f"Конфигурационный файл '{CONFIG_FILE}' был создан с тайм-аутом по умолчанию: {DEFAULT_TIMEOUT} секунд.")

def read_timeout():
    """Читает значение таймаута из конфигурационного файла."""
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    timeout = config["settings"]["timeout"]
    print(f"Таймаут: {timeout} секунд")
    return timeout
```

### process.py
Этот файл содержит функции для запуска и мониторинга процессов:

```python
import subprocess
import threading
import time
import queue

def run_program(command, timeout, log_file, process_name, output_storage):
    """
    Запускает внешнюю команду с ограничением по времени.
    
    Args:
        command (str): Команда для выполнения
        timeout (int): Максимальное время выполнения в секундах
        log_file (str): Путь к файлу для записи вывода
        process_name (str): Имя процесса для отображения
        output_storage (list): Список для сохранения вывода
        
    Returns:
        int or None: Код возврата процесса или None при ошибке
    """
    output = ""
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            encoding='cp866'
        )
    except Exception as e:
        error_msg = f"ОШИБКА: Невозможно запустить {process_name} ({command}): {str(e)}"
        print(error_msg)
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"=== Вывод {process_name} ===\n")
            f.write(error_msg + "\n")
        return None

    # Очереди для хранения вывода
    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()
    
    # Флаг для остановки потоков чтения
    stop_threads = threading.Event()
    
    # Функции для чтения вывода в неблокирующем режиме
    def read_stdout():
        while not stop_threads.is_set():
            line = process.stdout.readline()
            if line:
                stdout_queue.put(line)
            else:
                time.sleep(0.1)
                if process.poll() is not None:
                    break
    
    def read_stderr():
        while not stop_threads.is_set():
            line = process.stderr.readline()
            if line:
                stderr_queue.put(line)
            else:
                time.sleep(0.1)
                if process.poll() is not None:
                    break
    
    # Запускаем потоки чтения
    stdout_thread = threading.Thread(target=read_stdout)
    stderr_thread = threading.Thread(target=read_stderr)
    stdout_thread.daemon = True
    stderr_thread.daemon = True
    stdout_thread.start()
    stderr_thread.start()

    try:
        start_time = time.time()
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"=== Вывод {process_name} ===\n")
            
            while True:
                # Проверяем таймаут
                if time.time() - start_time > timeout:
                    print(f"\nПревышен тайм-аут ({timeout} секунд), принудительно завершаем {process_name}.")
                    stop_threads.set()
                    process.kill()
                    break
                
                # Проверяем, завершился ли процесс
                if process.poll() is not None:
                    print(f"Процесс {process_name} завершен.")
                    break
                
                # Читаем весь доступный вывод
                while not stdout_queue.empty():
                    line = stdout_queue.get()
                    output += line
                    f.write(line)
                
                while not stderr_queue.empty():
                    line = stderr_queue.get()
                    output += line
                    f.write(line)
                
                print(f"Процесс {process_name} работает...")
                time.sleep(1)
            
            # Дочитываем оставшийся вывод
            while not stdout_queue.empty():
                line = stdout_queue.get()
                output += line
                f.write(line)
            
            while not stderr_queue.empty():
                line = stderr_queue.get()
                output += line
                f.write(line)

    except Exception as e:
        print(f"Ошибка при выполнении {process_name}: {e}")
        stop_threads.set()
        process.kill()
        process.wait()

    # Ждем завершения потоков чтения
    stop_threads.set()
    process.wait()
    
    # Сохраняем вывод
    if "Процесс" in process_name:
        output_storage.append(output)

    return process.returncode
```

### main.py
Основной файл, который импортирует функции из других модулей и запускает процесс:

```python
import threading
import os
from config import create_config, read_timeout
from process import run_program

def main():
    create_config()
    timeout = read_timeout()
    log_file = "program_output.log"

    # Раскомментируйте строку ниже, если хотите очищать лог при каждом запуске
    # if os.path.exists(log_file):
    #     os.remove(log_file)

    first_command = input("Введите первую команду: ")
    second_command = input("Введите вторую команду: ")

    print(f"Запуск программ с тайм-аутом {timeout} секунд.")

    output_storage = []

    ping_thread = threading.Thread(
        target=run_program, 
        args=(first_command, timeout, log_file, f"Процесс {first_command}", output_storage)
    )
    
    ipconfig_thread = threading.Thread(
        target=run_program, 
        args=(second_command, timeout, log_file, f"Процесс {second_command}", output_storage)
    )

    ping_thread.start()
    ipconfig_thread.start()

    ping_thread.join()
    ipconfig_thread.join()

    first_command_output = output_storage[0] if len(output_storage) > 0 else ""
    second_command_output = output_storage[1] if len(output_storage) > 1 else ""

    print("\nРезультаты выполнения процессов:")

    print(f"Результат первого процесса {first_command}:\n{first_command_output}")
    print(f"Результат второго процесса {second_command}:\n{second_command_output}")

    print("Работа скрипта завершена. Вывод сохранен в файл:", log_file)


if __name__ == "__main__":
    main()
```

## Примеры использования

### Пример 1: Проверка сетевого подключения
```
Введите первую команду: ping google.com
Введите вторую команду: ipconfig
```

### Пример 2: Мониторинг системы
```
Введите первую команду: tasklist
Введите вторую команду: systeminfo
```

### Пример 3: Тест таймаута
```
Введите первую команду: ping -t google.com
Введите вторую команду: timeout /t 30
```


## Дополнительная информация

- Лог-файл `program_output.log` будет дополняться при каждом запуске скрипта
- Если вы хотите очищать лог-файл перед каждым запуском, раскомментируйте соответствующие строки в коде `main.py`:
  ```python
  if os.path.exists(log_file):
      os.remove(log_file)
  ```
- При использовании модульного варианта рекомендуется создать виртуальное окружение Python для проекта
