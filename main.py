import threading
from config import read_timeout, create_config
from process import run_program

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