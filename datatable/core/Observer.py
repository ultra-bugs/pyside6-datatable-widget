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
import inspect
from functools import wraps
from types import MethodType
from typing import Any, List, Optional


def singleton(cls):
    """Singleton decorator"""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class Publisher:
    """Publisher (Subject) in Observer pattern"""

    def __init__(self):
        self.global_subscribers = []
        self.event_specific_subscribers = {}

    def subscribe(self, subscriber, event: Optional[str] = None):
        """Subscribe to all events or a specific event"""
        if event is None:
            self.global_subscribers.append(subscriber)
        else:
            if event not in self.event_specific_subscribers:
                self.event_specific_subscribers[event] = []
            if subscriber not in self.event_specific_subscribers[event]:
                self.event_specific_subscribers[event].append(subscriber)

    def unsubscribe(self, subscriber):
        """Unsubscribe from all events"""
        if subscriber in self.global_subscribers:
            self.global_subscribers.remove(subscriber)
        for subscribers in self.event_specific_subscribers.values():
            if subscriber in subscribers:
                subscribers.remove(subscriber)

    def notify(self, event: str, *args, **kwargs):
        """Notify subscribers of an event"""
        # Notify global subscribers
        for subscriber in self.global_subscribers:
            subscriber.update(event, *args, **kwargs)

        # Notify event-specific subscribers
        if event in self.event_specific_subscribers:
            for subscriber in self.event_specific_subscribers[event]:
                subscriber.update(event, *args, **kwargs)

    def connect(self, widget, signal_name: str, event: str, data: Any = None, **kwargs):
        """Connect a Qt signal to an event"""
        slot = getattr(widget, signal_name, None)
        if slot is None:
            return
        if data:
            kwargs['data'] = data
        slot.connect(
            lambda *args, **signal_kwargs: self.notify(
                event, *args, **{**kwargs, **signal_kwargs}
            )
        )


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
        """Handle an event"""
        method_name = f'on_{event}'
        if hasattr(self, method_name):
            method = getattr(self, method_name)

            # First approach: Try to inspect the signature
            try:
                sig = inspect.signature(method)
                params = list(sig.parameters.values())
                is_bound_method = isinstance(method, MethodType)

                # Determine parameter count, accounting for 'self' in bound methods
                if is_bound_method and params and params[0].name == 'self':
                    # If it's a normal method with visible self parameter
                    params = params[1:]

                if not params:
                    # Method takes no parameters beyond self
                    method()
                    return
                elif len(params) == 1:
                    # Method takes one parameter
                    method(args[0] if args else None)
                    return
                else:
                    # Method takes multiple parameters
                    method(*args, **kwargs)
                    return

            except (ValueError, TypeError):
                # Inspection failed (can happen with some decorators)
                # Fall back to the try/except approach
                pass
                # Second approach: Try calling with different argument patterns
                try:
                    # Try with data first
                    if args[0] is not None:
                        method(args[0], *[args[1:]], **kwargs)
                    else:
                        method(*args, **kwargs)
                except TypeError as e:
                    error_msg = str(e)
                    if 'positional argument' in error_msg and 'but' in error_msg:
                        # Try with no arguments (just self)
                        try:
                            method()
                        except TypeError:
                            # Try with just data
                            try:
                                method(args[0] if args else None)
                            except TypeError:
                                # If all attempts fail, raise the original error
                                raise e
                    else:
                        # Some other TypeError, re-raise
                        raise
