import os
import sys
from pathlib import Path
from threading import Event, Thread, Lock

from watchdog.observers import Observer

from watcher.FolderHandler import FolderHandler


class Watcher(Thread):

    def __init__(self, folder_path, owners):
        if not os.path.exists(folder_path):
            print(f"Configuration error: {folder_path} does not exist.")
            sys.exit(1)

        Thread.__init__(self)
        self.folder_path = folder_path
        self.owners = owners
        self.folder_name = Path(self.folder_path).name
        self.start_observer(folder_path)
        self.stop_required = False
        self.lock = Lock()
        self.something_happened = Event()
        self.modified_paths = []

    def start_observer(self, folder_path):
        print(f"Initiate observer for {folder_path}")
        observer = Observer()
        folder_handler = FolderHandler(self)
        observer.schedule(folder_handler, folder_path, recursive=True)
        observer.start()
        print("Observer initiated correctly.")

    def wake_up(self, new_path: str):
        with self.lock:
            found = False
            for i, path in enumerate(self.modified_paths):
                if new_path == path:
                    found = True
                elif new_path in path:
                    self.modified_paths[i] = new_path
                    found = True
                elif path in new_path:
                    found = True
            if not found:
                self.modified_paths.append(new_path)
        self.something_happened.set()

    def stop(self):
        self.stop_required = True

    def __scan_and_index(self):
        to_update = []
        with self.lock:
            if len(self.modified_paths) != 0:
                to_update = self.modified_paths
                self.modified_paths = []

        for modified_path in to_update:
            print(f"Update after changes in path {modified_path}")
            for nc_prefix, user in self.owners.items():
                # - scan files
                occ_cmd = f"occ files:scan {user} --path=/{user}/files/{self.folder_name}"
                cmd = f"docker exec -u www-data {nc_prefix}-nc-1 php {occ_cmd}"
                print(f"Execute: {cmd}")
                os.system(cmd)

                # - memories index files
                occ_cmd = f"occ memories:index --user={user} --folder=/{self.folder_name}"
                cmd = f"docker exec -u www-data {nc_prefix}-nc-1 php {occ_cmd}"
                print(f"Execute: {cmd}")
                os.system(cmd)
        return True

    def run(self):
        print("Start thread in charge of watching changes")
        self.something_happened.wait()
        self.something_happened.clear()

        while True:
            if self.stop_required:
                print("Stop thread in charge of watching changes")
                return
            sync_delay = 10
            print(f"Watcher has been alerted of at least one change. Wait {sync_delay} seconds and update.")
            if not self.something_happened.wait(sync_delay):
                if self.__scan_and_index():
                    print("Wait for next modification...")
                    self.something_happened.wait()
                else:
                    print("Call failed. Wait another iteration before retrying to call it.")
                    continue
            self.something_happened.clear()
