#                      M""""""""`M            dP
#                      Mmmmmm   .M            88
#                      MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                      MMP  .MMMMM  88    88  88888"    88'  `88
#                      M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                      M         M  `88888P'  dP   `YP  `88888P'
#                      MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                      * * * * * * * * * * * * * * * * * * * * *
#                      * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                      * -  Copyright © 2026 (Z) Programing  - *
#                      *    -  -  All Rights Reserved  -  -    *
#                      * * * * * * * * * * * * * * * * * * * * *

#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2025 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
#
import inspect
from functools import wraps
from typing import List, Optional

from PySide6.QtCore import QMutex, QMutexLocker


def singleton(cls):
    """Singleton decorator"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


class PythonHelper:
    @staticmethod
    def is_type_compatible(value, annotation):
        try:
            return isinstance(value, annotation)
        except TypeError:
            # Handle generic types like List[str], Dict[str, int], etc.
            if hasattr(annotation, '__origin__'):
                origin = annotation.__origin__
                return isinstance(value, origin)
            return False


@singleton
class Publisher:
    """Publisher (Subject) in Observer pattern"""

    def __init__(self):
        self.global_subscribers = []
        self.event_specific_subscribers = {}
        self._lock = QMutex()

    def subscribe(self, subscriber, event: Optional[str] = None):
        """Subscribe to all events or a specific event"""
        locker = QMutexLocker(self._lock)
        if event is None:
            self.global_subscribers.append(subscriber)
        else:
            if event not in self.event_specific_subscribers:
                self.event_specific_subscribers[event] = []
            if subscriber not in self.event_specific_subscribers[event]:
                self.event_specific_subscribers[event].append(subscriber)

    def unsubscribe(self, subscriber):
        """Unsubscribe from all events"""
        locker = QMutexLocker(self._lock)
        if subscriber in self.global_subscribers:
            self.global_subscribers.remove(subscriber)
        for subscribers in self.event_specific_subscribers.values():
            if subscriber in subscribers:
                subscribers.remove(subscriber)

    def notify(self, event: str, *args, **kwargs):
        """Notify subscribers of an event"""
        # Make a copy of subscribers to avoid race conditions during iteration
        locker = QMutexLocker(self._lock)
        global_subscribers = self.global_subscribers.copy()
        event_subscribers = self.event_specific_subscribers.get(event, []).copy()
        locker.unlock()  # Unlock before notifying to avoid deadlocks

        # Notify global subscribers
        for subscriber in global_subscribers:
            subscriber.update(event, *args, **kwargs)

        # Notify event-specific subscribers
        for subscriber in event_subscribers:
            subscriber.update(event, *args, **kwargs)

    def connect(self, widget, signal_name: str, event: str, *args, **kwargs):
        """Connect a Qt signal to an event"""
        slot = getattr(widget, signal_name, None)
        if slot is None:
            return

        slot.connect(lambda *s_args, **signal_kwargs: self.notify(event, *[*args, *s_args], **{**kwargs, **signal_kwargs}))


class Subscriber:
    """Base class for subscribers (observers)"""

    def __init__(self, events: List[str]):
        self.events = events
        self.is_global_subscriber = False

        # Auto-subscribe to events
        publisher = Publisher()
        for event in events:
            publisher.subscribe(self, event)

    def update(self, event: str, *args, **kwargs):
        """Handle an event using smart parameter injection with type hint priority"""
        method_name = f'on_{event}'
        sig = None
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            try:
                # Get method signature
                sig = inspect.signature(method)
                # Create parameter dictionary
                params_dict = {}

                # Track used arguments
                used_args = set()
                used_kwargs = set()

                # Get all available parameters from args and kwargs
                all_params = {}
                # Add individual positional args by index
                for i, arg in enumerate(args):
                    all_params[f'arg{i}'] = arg
                # Add kwargs
                for k, v in kwargs.items():
                    if not k.startswith('*'):
                        all_params[k] = v

                # Map available parameters to method parameters
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue  # Skip self parameter

                    matched = False

                    # First priority: exact name match in kwargs
                    if param_name in kwargs and param_name not in used_kwargs:
                        params_dict[param_name] = kwargs[param_name]
                        used_kwargs.add(param_name)
                        matched = True
                        continue

                    # Second priority: type hint matching
                    if param.annotation != inspect.Parameter.empty:
                        # Helper function to check type compatibility

                        # Try to match by type hint in args first
                        for i, arg in enumerate(args):
                            if i not in used_args and PythonHelper.is_type_compatible(arg, param.annotation):
                                params_dict[param_name] = arg
                                used_args.add(i)
                                matched = True
                                break

                        # If not found in args, try kwargs
                        if not matched:
                            for key, value in kwargs.items():
                                if key not in used_kwargs and PythonHelper.is_type_compatible(value, param.annotation):
                                    params_dict[param_name] = value
                                    used_kwargs.add(key)
                                    matched = True
                                    break

                    # Third priority: positional argument matching (for required params)
                    if not matched and param.default is inspect.Parameter.empty:
                        # Try to find first unused positional argument
                        for i, arg in enumerate(args):
                            if i not in used_args:
                                params_dict[param_name] = arg
                                used_args.add(i)
                                matched = True
                                break

                        # If still no match, try unused kwargs
                        if not matched:
                            for key, value in kwargs.items():
                                if key not in used_kwargs:
                                    params_dict[param_name] = value
                                    used_kwargs.add(key)
                                    matched = True
                                    break

                # Call the method with the matched parameters
                return method(**params_dict)

            except (TypeError, AttributeError) as e:
                # Fallback logic remains the same
                if not sig:
                    sig = inspect.signature(method)
                error_msg = str(e)
                if 'argument' in error_msg and ('got an unexpected' in error_msg or 'missing' in error_msg):
                    try:
                        param_count = len(sig.parameters)
                        has_self = 'self' in sig.parameters
                        if has_self:
                            param_count -= 1
                        if param_count == 0:
                            return method()
                        elif param_count == 1 and args:
                            return method(args[0])
                        elif param_count == 2 and len(args) >= 2:
                            return method(args[0], args[1])
                        elif args:
                            return method(*args)
                        else:
                            raise TypeError(f'Could not match parameters for {method_name}. Original error: {error_msg}')
                    except TypeError:
                        raise TypeError(f'Could not match parameters for {method_name}. Original error: {error_msg}')
                else:
                    raise
            except Exception as e:
                raise e
