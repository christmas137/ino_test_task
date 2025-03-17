import subprocess
import threading
import queue
import time


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