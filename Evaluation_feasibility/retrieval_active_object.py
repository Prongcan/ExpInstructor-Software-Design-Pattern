import threading
import queue
import requests
import json
from concurrent.futures import Future


class RetrievalActiveObject:
    """
    Active Object Pattern Implementation [cite: 24, 55]
    Responsibility: Decouples method execution from method invocation for the retrieval service.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        """Thread-safe Singleton implementation"""
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RetrievalActiveObject, cls).__new__(cls)
        return cls._instance

    def __init__(self, api_url="http://127.0.0.1:9876/search_node_edge"):
        """
        Initialize the Active Object with a request queue and a background worker thread.
        """
        # Prevent re-initialization in Singleton
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.api_url = api_url
        self._queue = queue.Queue()
        self._running = True
        
        # Start the background worker (Servant wrapper) 
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        
        self._initialized = True
        print(f"[ActiveObject] Retrieval Service initialized via Active Object at {self.api_url}")

    def submit_task(self, payload: dict) -> Future:
        """
        [Proxy Method]
        Clients call this method. It constructs a request and returns a Future immediately.
        Does NOT block the caller. [cite: 25, 55]
        """
        future = Future()
        task = (payload, future)
        self._queue.put(task)
        return future

    def _run_loop(self):
        """
        [Scheduler / Dispatcher]
        Continuously monitors the queue and executes requests on the background thread.
        """
        while self._running:
            try:
                # Wait for a task (blocking here only blocks the worker thread, not the main thread)
                payload, future = self._queue.get(timeout=1)
                self._execute_request(payload, future)
                self._queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"[ActiveObject] Worker thread error: {e}")

    def _execute_request(self, payload: dict, future: Future):
        """
        [Servant Execution]
        Performs the actual synchronous HTTP request.
        """
        try:
            # This is the heavy lifting / blocking I/O
            response = requests.post(self.api_url, json=payload, timeout=3000)
            response.raise_for_status()
            data = response.json()
            
            # Pass the result back via Future
            future.set_result(data)
        except Exception as e:
            # Pass exception back via Future
            future.set_exception(e)

    def stop(self):
        self._running = False
        self._thread.join()