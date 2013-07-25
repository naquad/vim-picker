"""
Implementation of own ColorButton and ColorSelectionDialog
for working with palette (approximation, indexing, etc...)
"""
import gtk
import gobject
from math import ceil
from color import Color

class PaletteButton(gtk.Button):

    def __init__(self, color=None):
        gtk.Button.__init__(self)
        if color is not None:
            self.set_color(color)

    def set_color(self, color):
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

    def set_color(self, color):
        self.selector.set_previous_color(self.color.gtk)

        if self.palette:
            self.index, self.color = self.palette.approximate(color)
            self.current.set_color(self.color.gtk)
        else:
            self.color = color

        self.selector.set_current_color(self.color.gtk)
        self.color_change(self.color, self.index, True)

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
            self.current = self.make_button(self.color.gtk)
            container.pack_start(self.current)
        else:
            self.current = None

        container.show_all()

    def make_grid(self):
        rows = int(ceil(len(self.palette) / float(self.COLS)))
        grid = gtk.Table(rows, self.COLS)
        row, col = 0, 0
        for index, color in enumerate(self.palette):
            btn = self.make_button(color.gtk)
            btn.connect('clicked', self.palette_color, index)
            grid.attach(btn, col, col + 1, row, row + 1)
            col += 1
            if col > self.COLS:
                row += 1
                col = 0

        return grid

    def make_button(self, color):
        btn = PaletteButton(color)
        btn.set_size_request(20, 20)
        return btn

    def selector_color(self, selector):
        new_color = Color(selector.get_current_color())

        if self.palette:
            i, c = self.palette.approximate(new_color)
            self.current.set_color(c.gtk)
            self.color_change(c, i)
        else:
            self.color_change(new_color)

    def palette_color(self, btn, color_index):
        color = self.palette[color_index]
        self.selector.set_current_color(color.gtk)
        self.current.set_color(color.gtk)
        self.color_change(color, color_index)

    def color_change(self, color, index=None, final=False):
        if color == self.new_color and not final:
            return

        self.new_index = index
        self.new_color = color
        self.emit('color-changed', color, index)

    def on_response(self, dlg, rid):
        if rid == gtk.RESPONSE_ACCEPT:
            self.index = self.new_index
            self.color = self.new_color
            self.selector.set_previous_color(self.color.gtk)
            self.selector.set_current_color(self.color.gtk)

        self.color_change(self.color, self.index, True)

class PaletteColorButton(PaletteButton):

    DD_TARGETS = [('picker-color-type-0xC0102', gtk.TARGET_SAME_APP, 0xC0102)]

    __gsignals__ = {
        'color-changed': (gobject.SIGNAL_RUN_LAST, None, (object, object))
    }

    def __init__(self, palette, color=None, title=None):
        super(PaletteColorButton, self).__init__(color and color.gtk)
        self.dialog = PaletteColorDialog(palette, color, title, flags=gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.dialog.connect('color-changed', self.color_changed)
        self.dialog.connect('delete-event', self.hide_dialog)
        self.dialog.connect('response', self.hide_dialog)
        self.set_color(self.dialog.color.gtk)
        self.set_size_request(30, 20)
        self.connect('clicked', self.show_dialog)

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
        color = Color(sdata.data)
        self.dialog.set_color(color)
        self.set_color(self.dialog.color.gtk)

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
        self.set_color(self.dialog.color.gtk)
        return True

    def color_changed(self, dlg, color, index):
        self.emit('color-changed', color, index)
