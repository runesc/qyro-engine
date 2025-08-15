from qyro_engine.exceptions import EngineError


class PPGStore:
    _instance = None
    _store = {}
    _observers = []

    def __new__(cls, *args, **kwargs):
        EngineError(
            "PPGStore is deprecated and will be removed in a future release. Use Pydux instead."
        )
        if not cls._instance:
            cls._instance = super(PPGStore, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def add_to_store(self, obj: dict):
        if obj and isinstance(obj, dict):
            self._store.update(obj)
        else:
            raise ValueError(
                "Provide either a key and value or a dictionary object")

        self._notify_observers()

    def remove_from_store(self, key):
        if key in self._store:
            del self._store[key]
            self._notify_observers()
        else:
            raise KeyError(f"Key '{key}' not found in store")

    def _notify_observers(self):
        for observer in self._observers:
            # Llama al método `update_store` de cada observador
            observer.update_store(self._store)

    def subscribe_to_store(self, observer):
        if hasattr(observer, 'update_store') and callable(observer.update_store):
            self._observers.append(observer)
        else:
            raise ValueError("Observer must have an 'update_store' method")

    def unsubscribe_from_store(self, observer):
        """
        Unsubscribe an observer from the store.
        Raises ValueError if the observer is not found.
        """
        if observer in self._observers:
            self._observers.remove(observer)
        else:
            raise ValueError("Observer not found in store")

    def update_store(self, store):
        pass

    def remove_observer(self, observer):
        if observer in self._observers:
            self._observers.remove(observer)
        else:
            raise ValueError("Observer not found")

    @property
    def store(self):
        return self._store

    @store.setter
    def store(self, value):
        if isinstance(value, dict):
            self._store.update(value)
            self._notify_observers()
        else:
            raise ValueError("store must be a dictionary")