from pathlib import Path
from typing import TYPE_CHECKING

from watchdog.events import FileSystemEventHandler, FileSystemEvent

if TYPE_CHECKING:
    from watcher.Watcher import Watcher


class FolderHandler(FileSystemEventHandler):

    def __init__(self, watcher: "Watcher"):
        self.watcher = watcher

    def on_moved(self, event: FileSystemEvent):
        if not event.is_directory:
            self.watcher.wake_up(Path(event.src_path).parent.as_posix())
        else:
            self.watcher.wake_up(Path(event.src_path).as_posix())

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.watcher.wake_up(Path(event.src_path).parent.as_posix())
        else:
            self.watcher.wake_up(Path(event.src_path).as_posix())

    def on_deleted(self, event: FileSystemEvent):
        if not event.is_directory:
            self.watcher.wake_up(Path(event.src_path).parent.as_posix())
        else:
            self.watcher.wake_up(Path(event.src_path).as_posix())
