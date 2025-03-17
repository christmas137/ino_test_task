import subprocess
import os
import threading
import time
import json
import queue

CONFIG_FILE = "config_file.json"
DEFAULT_TIMEOUT = 8

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

def run_program(command, timeout, log_file, process_name, output_storage):
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
        error_msg = f"ОШИБКА: Невозможно запустить {process_name} ({' '.join(command)}): {str(e)}"
        print(error_msg)
        with open(log_file, "a", encoding='utf-8') as f:
            f.write(f"=== Вывод {process_name} ===\n")
            f.write(error_msg + "\n")
        return None

    stdout_queue = queue.Queue()
    stderr_queue = queue.Queue()
    
    stop_threads = threading.Event()
    
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
                if time.time() - start_time > timeout:
                    print(f"\nПревышен тайм-аут ({timeout} секунд), принудительно завершаем {process_name}.")
                    stop_threads.set()
                    process.kill()
                    break
                
                if process.poll() is not None:
                    print(f"Процесс {process_name} завершен.")
                    break
                
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

    stop_threads.set()
    process.wait()
    
    if "Процесс" in process_name:
        output_storage.append(output)

    return process.returncode

def main():
    create_config()
    timeout = read_timeout()
    log_file = "program_output.log"

    # Раскомментируйте строку ниже, если хотите очищать лог при каждом запуске
    # if os.path.exists(log_file):
    #     os.remove(log_file)

    try:
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
    
    except KeyboardInterrupt:
        print("\nПрограмма прервана пользователем. Завершаем процессы...")

        for thread in threading.enumerate():
            if thread != threading.main_thread(): 
                print(f"Завершаем поток {thread.name}")
                thread.join(timeout=2) 
        os._exit(1)  

if __name__ == "__main__":
    main()
