import multiprocessing
import subprocess

N_PROCESSES = 2

def run_process():
    subprocess.run(["python", "process.py"])

if __name__ == "__main__":
    processes = []

    for _ in range(N_PROCESSES):
        process = multiprocessing.Process(target=run_process)
        processes.append(process)
        process.start()

    for process in processes:
        process.join()
