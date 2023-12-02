import multiprocessing
import subprocess
from process import FILENAME

N_PROCESSES = 4

def run_process():
    subprocess.run(["python", "process.py"])

def erase_content_from_critical_section_file():
    with open(FILENAME, "w") as file:
        file.write("")

if __name__ == "__main__":
    erase_content_from_critical_section_file()

    processes = []

    for _ in range(N_PROCESSES):
        process = multiprocessing.Process(target=run_process)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
