from pydantic import BaseModel, create_model, ValidationError, Field
from typing import Dict, Type, Any, Optional, Union, get_origin, get_args
from rich.console import Console
try:
    from PySide6.QtCore import QTimer


except ImportError:
    try:
        from PySide2.QtCore import QTimer
    except ImportError:
        try:
            from PyQt6.QtCore import QTimer
        except ImportError:
            try:

                from PyQt5.QtCore import QTimer
            except ImportError:
                raise ImportError(
                    "No se encontró PySide6, PySide2, PyQt6 ni PyQt5 instalado."
                    "Por favor, instala uno de estos: pip install PySide6 (o PySide2, PyQt6, PyQt5)"
                )


console = Console()

class Pydux:
    _instance = None
    _store = None
    _observers = []
    _schema = None

    def __new__(cls, *args, **kwargs):
        """
        Create a new instance of the class. If the class is Pydux, it will create a singleton instance.
        If the class is a subclass of Pydux, it will create a normal instance but use the shared store.

        Args:
            cls: The class to create an instance of.
            *args: Positional arguments to pass to the class constructor.
        """
        if cls is Pydux:
            if not cls._instance:
                cls._instance = super(Pydux, cls).__new__(cls, *args, **kwargs)
            return cls._instance
        else:
            # For subclasses, create a new instance but share the store
            return super(Pydux, cls).__new__(cls, *args, **kwargs)

    def _default_for_type(self, typ):
        """
            Gets a default value for a given type.
            For BaseModel, it returns the class itself to use as a factory.
        """
        if typ == int:
            return 0
        if typ == str:
            return ""
        if typ == bool:
            return True
        if typ == dict or get_origin(typ) == dict:
            return {}
        if typ == list or get_origin(typ) == list:
            return []
        if typ == float:
            return 0.0
        if typ == Any:
            return None
        if get_origin(typ) == Optional:
            inner_type = get_args(typ)[0]
            return self._default_for_type(inner_type)
        if get_origin(typ) == Union:
            first_type = get_args(typ)[0]
            return self._default_for_type(first_type)

        if isinstance(typ, type) and issubclass(typ, BaseModel):
            # Devolvemos la clase para que se use como default_factory
            return typ
        return None

    def set_schema(self, schema_dict: Dict[str, Type]) -> None:
        """
        Receives a dictionary {"field": type} and creates a dynamic Pydantic model.

        Args:
            schema_dict (Dict[str, Type]): Dictionary with field names and their types.
        """
        if Pydux._schema is not None:
            console.print(f"\n\n⚠️ [bold yellow]WARNING[/bold yellow]: Schema already set. This will reset the store.\n\n", highlight=False)

        fields = {}
        for key, typ in schema_dict.items():
            # Para BaseModel, usamos default_factory. Para otros, usamos el valor.
            if isinstance(typ, type) and issubclass(typ, BaseModel):
                fields[key] = (Optional[typ], Field(default_factory=typ))
            else:
                default = self._default_for_type(typ)
                fields[key] = (Optional[typ], default)

        Pydux._schema = create_model('DynamicStoreModel', **fields)
        Pydux._store = Pydux._schema()

    def update_store(self, obj: Dict[str, Any]) -> None:
        if Pydux._schema is None:
            # Sin esquema, actualizar dict simple
            if Pydux._store is None:
                Pydux._store = {}
            if isinstance(Pydux._store, dict):
                Pydux._store.update(obj)
            else:
                # Fallback si había un modelo antes
                Pydux._store = obj
        else:
            try:
                current_data = Pydux._store.model_dump() if Pydux._store else {}
                combined = {**current_data, **obj}
                validated = Pydux._schema(**combined)
                Pydux._store = validated
            except ValidationError as e:
                raise TypeError(f"Validation error: {e}")

        self._notify_observers()

    def update_nested_model(self, model_key: str, partial_data: Dict[str, Any]) -> None:
        """
        Allows partial updates on nested models.
        Example: store.update_nested_model("user", {"name": "New name"})

        Args:
            model_key (str): Model key in the store to update.
            partial_data (Dict[str, Any]): Partial data to update the model with.
        """
        if Pydux._schema is None:
            raise ValueError(
                "Schema must be set before using update_nested_model")

        if not Pydux._store:
            raise ValueError("Store is empty")

        current_data = Pydux._store.model_dump()
        if model_key not in current_data or current_data[model_key] is None:
            raise KeyError(f"Model key '{model_key}' not found in store or is None")

        current_model_data = current_data[model_key]
        if isinstance(current_model_data, dict):
            updated_model_data = {**current_model_data, **partial_data}
        else:
            # If it is a Pydantic model, convert it to a dict first
            updated_model_data = {**current_model_data.__dict__, **partial_data}

        # Update using the main method
        self.update_store({model_key: updated_model_data})

    def _notify_observers(self) -> None:
        for observer in Pydux._observers:
            if hasattr(observer, '_trigger_render') and callable(observer._trigger_render):
                QTimer.singleShot(0, observer._trigger_render)

            if Pydux._schema is None:
                # Without schema, pass dict directly
                observer.on_store_change(
                    Pydux._store if isinstance(Pydux._store, dict) else {})
            else:
                # With schema, use model_dump
                observer.on_store_change(
                    Pydux._store.model_dump() if Pydux._store else {})

    def subscribe_to_store(self, observer: Any) -> None:
        if hasattr(observer, 'on_store_change') and callable(observer.on_store_change):
            if observer not in Pydux._observers:  # Prevent duplicates
                Pydux._observers.append(observer)
        else:
            raise ValueError("Observer must have an 'on_store_change' method")

    def unsubscribe_from_store(self, observer: Any) -> None:
        if observer in Pydux._observers:
            Pydux._observers.remove(observer)
        else:
            raise ValueError("Observer not found in store")

    def get_nested(self, path: str) -> Any:
        """
        Get a nested value from the store using a dot-notated path.
        Example: get_nested("user.name") returns the name of the user.

        Args:
            path (str): The dot-notated path to the value in the store.
        """
        if not Pydux._store:
            return None

        keys = path.split('.')
        current = Pydux._store.model_dump() if Pydux._schema else Pydux._store

        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                else:
                    current = getattr(current, key)
            return current
        except (KeyError, AttributeError):
            return None

    @property
    def store(self) -> Dict[str, Any]:
        if Pydux._schema is None:
            return Pydux._store if isinstance(Pydux._store, dict) else {}
        return Pydux._store.model_dump() if Pydux._store else {}

    @store.setter
    def store(self, value: Dict[str, Any]) -> None:
        self.update_store(value)

    def clear_store(self) -> None:
        """Clear the store and reset it to an empty state."""
        if Pydux._schema:
            Pydux._store = Pydux._schema()
        else:
            Pydux._store = {}
        self._notify_observers()

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the store.

        Args:
            key (str): The key to check in the store.
        """
        store_dict = self.store
        return key in store_dict and store_dict[key] is not None

    def remove_from_store(self, key: str) -> None:
        """Remove a key from the store, setting it to None if schema is used."""
        if Pydux._schema is None:
            if isinstance(Pydux._store, dict) and key in Pydux._store:
                del Pydux._store[key]
                self._notify_observers()
            else:
                raise KeyError(f"Key '{key}' not found in store")
        else:
            current_data = Pydux._store.model_dump() if Pydux._store else {}
            if key in current_data:
                current_data[key] = None  # Set to None instead of deleting
                validated = Pydux._schema(**current_data)
                Pydux._store = validated
                self._notify_observers()
            else:
                raise KeyError(f"Key '{key}' not found in store")

    def on_store_change(self, store: Dict[str, Any]) -> None:
        """This is a placeholder method to be overridden by subclasses.
        It can be used to update the store with new data.

        Args:
            store (Dict[str, Any]): The new data to update the store with.
        """
        pass
