import os
import json

CONFIG_FILE = "config_file.json"
DEFAULT_TIMEOUT = 5

def create_config():
    if not os.path.exists(CONFIG_FILE):
        defoult_config = {"settings": {"timeout": DEFAULT_TIMEOUT}}
        with open("config_file.json", "w") as f:
            json.dump(defoult_config, f, indent=4)
        print(f"Конфигурационный файл '{CONFIG_FILE}' был создан с тайм-аутом по умолчанию: {DEFAULT_TIMEOUT} секунд.")

def read_timeout():
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
        timeout = config["settings"]["timeout"]
        
        if not isinstance(timeout, int) or timeout <= 0:
            print(f"Ошибка: timeout должен быть целым числом и больше нуля. "
                  f"Значение timeout было присвоено значение по умолчанию: {DEFAULT_TIMEOUT}")
            timeout = DEFAULT_TIMEOUT
        else:
            print(f"Таймаут: {timeout} секунд")
    
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Ошибка при чтении конфигурационного файла: {e}. "
              f"Значение timeout было присвоено значение по умолчанию: {DEFAULT_TIMEOUT}")
        timeout = DEFAULT_TIMEOUT
    
    except Exception as e:
        print(f"Непредвиденная ошибка: {e}. "
              f"Значение timeout было присвоено значение по умолчанию: {DEFAULT_TIMEOUT}")
        timeout = DEFAULT_TIMEOUT
    return timeout