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
#              * -  Copyright © 2025 (Z) Programing  - *z
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

#
import importlib
from abc import ABC, abstractmethod
from typing import Dict, List, Any

from PySide6.QtWidgets import QWidget

from .Observer import Publisher
from .WidgetManager import WidgetManager


class ControllerMeta(type(QWidget), type(ABC)):
    required_attrs = ['slot_map']

    def __new__(cls, name, bases, dct):
        required_attrs = cls.required_attrs
        for attr in required_attrs:
            if attr not in dct:
                raise ValueError(f'Attribute: {attr} is required but not defined in {name}')
        return super().__new__(cls, name, bases, dct)


class BaseController(QWidget, ABC, metaclass=ControllerMeta):
    """Base class for all controllers in datatable package"""

    slot_map: Dict[str, List[str]] = {}
    signal_connected = False
    is_auto_connect_signal = True

    def __init__(self, parent=None):
        super().__init__(parent)
        self.widget_manager = WidgetManager(self)
        self.controller_name = self.__class__.__name__
        self.publisher = Publisher()
        self.handler = None

        # Setup UI
        self.setupUi(self)

        if not self.is_auto_connect_signal:
            return

        # Auto-loading handler
        module_path = self.__module__
        module_parts = module_path.split('.')
        if len(module_parts) > 1:
            # Try to find handler in the same package
            base_module = '.'.join(module_parts[:-1])
            handler_module_name = f'{base_module}.handlers.{self.controller_name}Handler'
            print(handler_module_name)
            try:
                handler_module = importlib.import_module(handler_module_name)
                handler_class = getattr(handler_module, f'{self.controller_name}Handler')
                self.handler = handler_class(widget_manager=self.widget_manager, events=list(self.slot_map.keys()))
            except (ImportError, AttributeError):
                # If not found, try alternative locations
                pass

        if self.is_auto_connect_signal and self.handler:
            self._connect_signals()

    @abstractmethod
    def setupUi(self, widget):
        """Set up the UI components"""
        pass

    def _connect_signals(self):
        """Connect signals to slots based on slot_map"""
        if not hasattr(self, 'slot_map'):
            raise ValueError(f'{self.__class__.__name__} must define slot_map to use auto connect signals')

        subscriber = self.handler
        for event in self.handler.events:
            if event in self.slot_map:
                signal_info = self.slot_map.get(event)
                if signal_info is None:
                    continue

                if callable(signal_info):
                    signal_info(self.handler, self.publisher)
                    continue

                try:
                    widget = self.widget_manager.get(signal_info[0])
                    self.publisher.connect(widget, signal_info[1], event, data={'widget': widget})
                    print(f'Connected {signal_info[1]} signal to {event} event')
                    print(widget, event, signal_info)
                except (AttributeError, Exception) as e:
                    print(f'Error connecting signal: {e}')
                    print(event, signal_info)
                    continue

                self.publisher.subscribe(subscriber=subscriber, event=event)

        self.signal_connected = True
