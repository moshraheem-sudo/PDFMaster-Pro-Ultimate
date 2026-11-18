"""
PDF Master Pro - Background Task Manager
Asynchronous worker threads to keep the UI silky smooth during heavy PDF/Image processing.
"""
from typing import Callable, Any, Dict, Optional
from PySide6.QtCore import QObject, QThread, Signal

class WorkerSignals(QObject):
    started = Signal(str)
    progress = Signal(int, int, str) # current, total, status_text
    finished = Signal(bool, str, object) # success, message, result_data
    error = Signal(str)

class TaskWorker(QThread):
    def __init__(self, task_name: str, fn: Callable, *args, **kwargs):
        super().__init__()
        self.task_name = task_name
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def is_cancelled(self) -> bool:
        return self._is_cancelled

    def run(self):
        self.signals.started.emit(self.task_name)
        
        def progress_callback(cur: int, tot: int, msg: str):
            if self._is_cancelled:
                raise InterruptedError("تم إلغاء العملية بواسطة المستخدم")
            self.signals.progress.emit(cur, tot, msg)
            
        # Inject progress_callback if function accepts it
        kwargs = dict(self.kwargs)
        import inspect
        sig = inspect.signature(self.fn)
        if "progress_callback" in sig.parameters:
            kwargs["progress_callback"] = progress_callback
            
        try:
            result = self.fn(*self.args, **kwargs)
            self.signals.finished.emit(True, "اكتملت العملية بنجاح", result)
        except InterruptedError:
            self.signals.finished.emit(False, "تم إلغاء العملية", None)
        except Exception as e:
            self.signals.error.emit(str(e))
            self.signals.finished.emit(False, f"خطأ: {str(e)}", None)

class TaskManager(QObject):
    task_added = Signal(str)
    task_progress = Signal(str, int, int, str)
    task_done = Signal(str, bool, str)

    def __init__(self):
        super().__init__()
        self.active_tasks: Dict[str, TaskWorker] = {}
        self.history: list = []

    def start_task(self, task_name: str, fn: Callable, on_success=None, on_error=None, on_progress=None, *args, **kwargs) -> TaskWorker:
        worker = TaskWorker(task_name, fn, *args, **kwargs)
        self.active_tasks[task_name] = worker
        self.task_added.emit(task_name)

        if on_progress:
            worker.signals.progress.connect(on_progress)
        worker.signals.progress.connect(lambda cur, tot, msg: self.task_progress.emit(task_name, cur, tot, msg))

        def handle_finished(success, msg, res):
            if task_name in self.active_tasks:
                del self.active_tasks[task_name]
            self.history.append({"name": task_name, "success": success, "msg": msg})
            self.task_done.emit(task_name, success, msg)
            if success and on_success:
                on_success(res)
            elif not success and on_error:
                on_error(msg)

        worker.signals.finished.connect(handle_finished)
        if on_error:
            worker.signals.error.connect(on_error)

        worker.start()
        return worker

    def cancel_task(self, task_name: str):
        if task_name in self.active_tasks:
            self.active_tasks[task_name].cancel()
