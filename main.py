import ast
import os
import time

from watcher.Watcher import Watcher

if __name__ == '__main__':
    print("Start nc-wef")
    watcher_list = []
    i = 0
    while os.getenv(f"SHARED_FOLDER_{i + 1}") is not None:
        i += 1
        if os.getenv(f"OWNERS_{i}") is None:
            print(f"Warning: OWNERS_{i} is not defined whereas SHARED_FOLDER_{i} is")
            continue
        shared_folder = os.getenv(f"SHARED_FOLDER_{i}")
        owners = ast.literal_eval(os.getenv(f"OWNERS_{i}"))
        watcher = Watcher(shared_folder, owners)
        watcher.start()
        watcher_list.append(watcher)
        time.sleep(1)

    if len(watcher_list) != 0:
        try:
            while True:
                watcher_list[0].join(60)
        finally:
            for watcher in watcher_list:
                watcher.stop()
                watcher.join()
    else:
        print("Nothing to do.")
