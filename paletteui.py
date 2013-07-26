"""
Implementation of own ColorButton and ColorSelectionDialog
for working with palette (approximation, indexing, etc...)
"""
import gtk
import gobject
from math import ceil
from color import Color
from colorop import opposite_rgb

class PaletteButton(gtk.Button):

    def __init__(self, color=None):
        gtk.Button.__init__(self)
        if color is not None:
            self.set_color(color)

        self.active = False
        self.set_border_width(2)
        self.connect('expose-event', self.expose)

    def expose(self, widget, evt):
        if self.active:
            cr = self.window.cairo_create()
            cr.set_line_width(3)
            cr.set_source_rgb(*self.complement)

            w = self.allocation.width
            h = self.allocation.height
            cr.rectangle(self.allocation.x, self.allocation.y, w, h)
            cr.clip_preserve()
            cr.close_path()
            cr.stroke()

        return False

    def set_active(self, active):
        self.active = active
        self.queue_draw()

    def set_color(self, color):
        self.complement = opposite_rgb(
            255 - color.red / 256,
            255 - color.green / 256,
            255 - color.blue / 256
        )

        for state in [gtk.STATE_NORMAL, gtk.STATE_ACTIVE, gtk.STATE_PRELIGHT, gtk.STATE_SELECTED, gtk.STATE_INSENSITIVE]:
            self.modify_bg(state, color)

class PaletteColorDialog(gtk.Dialog):

    __gsignals__ = {
        'color-changed': (gobject.SIGNAL_RUN_LAST, None, (object, object))
    }

    COLS = 16

    def __init__(self, palette, current=None, title=None, parent=None, flags=gtk.DIALOG_MODAL):
        gtk.Dialog.__init__(self,
                            title or 'Color Chooser',
                            parent,
                            flags,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.set_position(gtk.WIN_POS_NONE)

        self.palette = palette

        if current:
            if self.palette:
                self.index, self.color = self.palette.approximate(current)
            else:
                self.color = current
                self.index = None
        elif self.palette:
            self.color = self.palette[0]
            self.index = 0
        else:
            self.color = Color('#000000')
            self.index = None

        self.new_color = self.color
        self.new_index = self.index

        self.connect('response', self.on_response)
        self.connect('realize', self.on_visibility)
        self.connect('show', self.on_visibility)

        self.make_ui()

    def on_visibility(self, me):
        rootwin = self.get_screen().get_root_window()
        x, y, mods = rootwin.get_pointer()
        w, h = self.size_request()
        self.move(x - w - 20, y - (h / 2))

    def make_ui(self):
        container = self.get_content_area()

        self.selector = gtk.ColorSelection()
        self.selector.set_has_opacity_control(False)
        self.selector.connect('color-changed', self.selector_color)

        container.pack_start(self.selector)

        if self.palette:
            container.pack_start(self.make_grid())

            label = gtk.Label()
            label.set_markup('<b>Currently selected (with approximation to palette):</b>')
            container.pack_start(label)

            hbox = gtk.HBox()

            self.current = self.make_button(self.color.gtk)
            hbox.pack_start(self.current)

            self.current_index = gtk.Entry()
            self.current_index.set_text(str(self.index))
            self.current_index.connect('focus-out-event', self.current_index_change)
            self.current_index.connect('key-press-event', self.catch_enter)
            hbox.pack_start(self.current_index, False, 10)

            container.pack_start(hbox)
        else:
            self.current = None

        container.show_all()

    def make_grid(self):
        self.buttons = []

        rows = int(ceil(len(self.palette) / float(self.COLS)))
        grid = gtk.Table(rows, self.COLS)
        row, col = 0, 0
        for index, color in enumerate(self.palette):
            btn = self.make_button(color.gtk)
            btn.connect('clicked', self.palette_color, index)
            grid.attach(btn, col, col + 1, row, row + 1)
            self.buttons.append(btn)
            col += 1
            if col > self.COLS:
                row += 1
                col = 0

        self.buttons[self.index].set_active(True)
        return grid

    def make_button(self, color):
        btn = PaletteButton(color)
        btn.set_size_request(20, 20)
        return btn

    def catch_enter(self, entry, evt):
        if evt.keyval == gtk.keysyms.Return or evt.keyval == gtk.keysyms.KP_Enter:
            self.current_index_change(None, None)

    def current_index_change(self, entry, evt):
        index = self.current_index.get_text()

        valid = index.isdigit()
        if valid:
            index = int(index)
            valid = index > 0 and index < len(self.palette)

            if valid and self.new_index != index:
                self.sync_selectors(index=index)

        if not valid:
            self.current_index.set_text(str(self.new_index or self.index))

    def selector_color(self, selector):
        self.sync_selectors(from_selector=True)

    def palette_color(self, btn, color_index):
        self.sync_selectors(index=color_index)

    def set_color(self, color):
        self.sync_selectors(color, final=True)

    def set_index(self, index):
        self.sync_selectors(index=index, final=True)

    def sync_selectors(self, color=None, index=None, final=False, from_selector=False):
        if color is None and index is None:
            color = Color(self.selector.get_current_color())

        if color is None and index is not None:
            color = self.palette[index]

        if not isinstance(color, Color):
            color = Color(color)

        if index is None and self.palette is not None:
            index, color = self.palette.approximate(color)

        emit = self.new_color != color or final

        self.new_color = color
        if not from_selector:
            self.selector.set_current_color(color.gtk)

        if index is not None:
            if self.new_index:
                self.buttons[self.new_index].set_active(False)
            if self.index is not None:
                self.buttons[self.index].set_active(False)
            self.new_index = index
            self.buttons[self.new_index].set_active(True)
            self.current_index.set_text(str(self.new_index))
            self.current.set_color(self.new_color.gtk)

        if final:
            self.color = self.new_color
            self.index = self.new_index
            self.selector.set_previous_color(self.color.gtk)

        if emit:
            self.emit('color-changed', self.new_color, self.new_index)

    def on_response(self, dlg, rid):
        if rid == gtk.RESPONSE_ACCEPT:
            self.sync_selectors(None, None, True)

class PaletteColorButton(PaletteButton):

    DD_TARGETS = [('picker-color-type-0xC0102', gtk.TARGET_SAME_APP, 0xC0102)]

    __gsignals__ = {
        'color-changed': (gobject.SIGNAL_RUN_LAST, None, (object, object))
    }

    def __init__(self, palette, color=None, title=None):
        super(PaletteColorButton, self).__init__()
        self.dialog = PaletteColorDialog(palette, color, title, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.dialog.connect('color-changed', self.color_changed)
        self.dialog.connect('delete-event', self.hide_dialog)
        self.dialog.connect('response', self.hide_dialog)
        self.set_size_request(30, 20)
        self.connect('clicked', self.show_dialog)
        self._set_btn_color(self.color.gtk)
        self.set_border_width(0)

        self.drag_source_set(
            gtk.gdk.BUTTON1_MASK,
            self.DD_TARGETS,
            gtk.gdk.ACTION_COPY
        )

        self.connect('drag-motion', self.dd_motion)
        self.connect('drag-drop', self.dd_drop)

        self.drag_dest_set(
            gtk.DEST_DEFAULT_ALL,
            self.DD_TARGETS,
            gtk.gdk.ACTION_COPY
        )

        self.connect('drag-data-received', self.dd_received)
        self.connect('drag-data-get', self.dd_get)

    def dd_motion(self, me, context, x, y, time):
        context.drag_status(gtk.gdk.ACTION_COPY, time)
        return True

    def dd_drop(self, me, context, x, y, time):
        context.finish(True, False, time)
        return True

    def dd_get(self, me, context, selection, tt, time):
        selection.set(selection.target, 0xC0102, str(self.color))

    def dd_received(self, me, context, x, y, sdata, info, time):
        self.dialog.set_color(sdata.data)
        self._set_btn_color(self.dialog.color.gtk)

    def _set_btn_color(self, color):
        super(PaletteColorButton, self).set_color(color)

    def set_color(self, color):
        self.dialog.set_color(color)
        self.set_color(self.color.gtk)

    def set_index(self, index):
        self.dialog.set_index(index)
        self._set_btn_color(self.color.gtk)

    @property
    def color(self):
        return self.dialog.color

    @property
    def index(self):
        return self.dialog.index

    def show_dialog(self, btn):
        self.dialog.show()

    def hide_dialog(self, dlg, evt):
        self.dialog.hide()
        self._set_btn_color(self.color.gtk)
        return True

    def color_changed(self, dlg, color, index):
        self.emit('color-changed', color, index)
