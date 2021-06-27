from __future__ import annotations

from typing import TYPE_CHECKING

import ba
import _ba
import random
import weakref
from bastd.ui import popup
from bastd.ui.popup import PopupWindow

if TYPE_CHECKING: pass

class NewPopupMenuWindow(PopupWindow):
    def __init__(self,
                 position: Tuple[float, float],
                 choices: Sequence[str],
                 current_choice: str,
                 delegate: Any = None,
                 width: float = 230.0,
                 maxwidth: float = None,
                 scale: float = 1.0,
                 choices_disabled: Sequence[str] = None,
                 choices_display: Sequence[str] = None):

        if choices_disabled is None:
            choices_disabled = []
        if choices_display is None:
            choices_display = []

        choices_display_fin: List[str] = []
        
        if maxwidth is None:
            maxwidth = width * 1.5

        self._transitioning_out = False
        self._choices = list(choices)
        self._choices_display = list(choices_display_fin)
        self._current_choice = current_choice
        self._choices_disabled = list(choices_disabled)
        self._done_building = False
        if not choices:
            raise TypeError('Must pass at least one choice')
        self._width = width
        self._scale = scale
        if len(choices) > 8:
            self._height = 280
            self._use_scroll = True
        else:
            self._height = 20 + len(choices) * 33
            self._use_scroll = False
        self._delegate = None

        for index, choice in enumerate(choices):
            if len(choices_display_fin) == len(choices):
                choice_display_name = choices_display_fin[index]
            else:
                choice_display_name = choice
            if self._use_scroll:
                self._width = max(
                    self._width,
                    min(
                        maxwidth,
                        _ba.get_string_width(choice_display_name,
                                             suppress_warning=True)) + 75)
            else:
                self._width = max(
                    self._width,
                    min(
                        maxwidth,
                        _ba.get_string_width(choice_display_name,
                                             suppress_warning=True)) + 60)

        PopupWindow.__init__(self,
                             position,
                             size=(self._width, self._height),
                             scale=self._scale)

        if self._use_scroll:
            self._scrollwidget = ba.scrollwidget(parent=self.root_widget,
                                                 position=(20, 20),
                                                 highlight=False,
                                                 color=(0.35, 0.55, 0.15),
                                                 size=(self._width - 40,
                                                       self._height - 40))
            self._columnwidget = ba.columnwidget(parent=self._scrollwidget,
                                                 border=2,
                                                 margin=0)
        else:
            self._offset_widget = ba.containerwidget(parent=self.root_widget,
                                                     position=(30, 15),
                                                     size=(self._width - 40,
                                                           self._height),
                                                     background=False)
            self._columnwidget = ba.columnwidget(parent=self._offset_widget,
                                                 border=2,
                                                 margin=0)
        for index, choice in enumerate(choices):
            if len(choices_display_fin) == len(choices):
                choice_display_name = choices_display_fin[index]
            else:
                choice_display_name = choice
            inactive = (choice in self._choices_disabled)
            wdg = ba.textwidget(parent=self._columnwidget,
                                size=(self._width - 40, 28),
                                on_select_call=ba.Call(self._select, index),
                                click_activate=True,
                                color=(0.5, 0.5, 0.5, 0.5) if inactive else
                                ((0.5, 1, 0.5,
                                  1) if choice == self._current_choice else
                                 (0.8, 0.8, 0.8, 1.0)),
                                padding=0,
                                maxwidth=maxwidth,
                                text=choice_display_name,
                                on_activate_call=self._activate,
                                v_align='center',
                                selectable=(not inactive))
            if choice == self._current_choice:
                ba.containerwidget(edit=self._columnwidget,
                                   selected_child=wdg,
                                   visible_child=wdg)

        self._delegate = weakref.ref(delegate)
        self._done_building = True

    def _select(self, index: int) -> None:
        if self._done_building:
            self._current_choice = self._choices[index]

    def _activate(self) -> None:
        ba.playsound(ba.getsound('swish'))
        ba.timer(0.05, self._transition_out, timetype=ba.TimeType.REAL)
        delegate = self._getdelegate()
        if delegate is not None:
            call = ba.Call(delegate.popup_menu_selected_choice, self,
                           self._current_choice)
            ba.timer(0, call, timetype=ba.TimeType.REAL)

    def _getdelegate(self) -> Any:
        return None if self._delegate is None else self._delegate()

    def _transition_out(self) -> None:
        if not self.root_widget:
            return
        if not self._transitioning_out:
            self._transitioning_out = True
            delegate = self._getdelegate()
            if delegate is not None:
                delegate.popup_menu_closing(self)
            ba.containerwidget(edit=self.root_widget, transition='out_scale')

    def on_popup_cancel(self) -> None:
        if not self._transitioning_out:
            ba.playsound(ba.getsound('swish'))
        self._transition_out()

class NewPopupMenu:
    def __init__(self,
                 parent: ba.Widget,
                 position: Tuple[float, float],
                 choices: Sequence[str],
                 current_choice: str = None,
                 on_value_change_call: Callable[[str], Any] = None,
                 opening_call: Callable[[], Any] = None,
                 closing_call: Callable[[], Any] = None,
                 width: float = 230.0,
                 maxwidth: float = None,
                 scale: float = None,
                 choices_disabled: Sequence[str] = None,
                 choices_display: Sequence[str] = None,
                 button_size: Tuple[float, float] = (160.0, 50.0),
                 autoselect: bool = True):
        if choices_disabled is None:
            choices_disabled = []
        if choices_display is None:
            choices_display = []
        uiscale = ba.app.ui.uiscale
        if scale is None:
            scale = (2.3 if uiscale is ba.UIScale.SMALL else
                     1.65 if uiscale is ba.UIScale.MEDIUM else 1.23)
        if current_choice not in choices:
            current_choice = None
        self._choices = list(choices)
        if not choices:
            raise TypeError('no choices given')
        self._choices_display = list(choices_display)
        self._choices_disabled = list(choices_disabled)
        self._width = width
        self._maxwidth = maxwidth
        self._scale = scale
        self._current_choice = (current_choice if current_choice is not None
                                else self._choices[0])
        self._position = position
        self._parent = parent
        if not choices:
            raise TypeError('Must pass at least one choice')
        self._parent = parent
        self._button_size = button_size

        self._button = ba.buttonwidget(
            parent=self._parent,
            position=(self._position[0], self._position[1]),
            autoselect=autoselect,
            size=self._button_size,
            scale=1.0,
            label='',
            on_activate_call=lambda: ba.timer(
                0, self._make_popup, timetype=ba.TimeType.REAL))
        self._on_value_change_call = None
        self._opening_call = opening_call
        self._autoselect = autoselect
        self._closing_call = closing_call
        self.set_choice(self._current_choice)
        self._on_value_change_call = on_value_change_call
        self._window_widget: Optional[ba.Widget] = None

        ba.uicleanupcheck(self, self._button)

    def _make_popup(self) -> None:
        if not self._button:
            return
        if self._opening_call:
            self._opening_call()
        self._window_widget = NewPopupMenuWindow(
            position=self._button.get_screen_space_center(),
            delegate=self,
            width=self._width,
            maxwidth=self._maxwidth,
            scale=self._scale,
            choices=self._choices,
            current_choice=self._current_choice,
            choices_disabled=self._choices_disabled,
            choices_display=self._choices_display).root_widget

    def get_button(self) -> ba.Widget:
        return self._button

    def get_window_widget(self) -> Optional[ba.Widget]:
        return self._window_widget

    def popup_menu_selected_choice(self, popup_window: PopupWindow,
                                   choice: str) -> None:
        del popup_window
        self.set_choice(choice)
        if self._on_value_change_call:
            self._on_value_change_call(choice)

    def popup_menu_closing(self, popup_window: PopupWindow) -> None:
        del popup_window
        if self._button:
            ba.containerwidget(edit=self._parent, selected_child=self._button)
        self._window_widget = None
        if self._closing_call:
            self._closing_call()

    def set_choice(self, choice: str) -> None:      
        self._current_choice = choice
        displayname: Union[str, ba.Lstr]
        if len(self._choices_display) == len(self._choices):
            displayname = self._choices_display[self._choices.index(choice)]
        else:
            displayname = choice
        if self._button:
            ba.buttonwidget(edit=self._button, label=displayname)