import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sass

class SCSSHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith('.scss'):
            print(f"Recompilando {event.src_path}...")
            sass.compile(dirname=('static/scss', 'static/css'), output_style='compressed')

if __name__ == "__main__":
    path = "static/scss"
    event_handler = SCSSHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"Monitoreando cambios en {path}...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
