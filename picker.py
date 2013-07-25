import gtk
from palettes import CTERM_COLORS, TERM_COLORS
from color import Color, Palette
from paletteui import PaletteColorButton
from preview import PreviewEntry

class Picker(gtk.Window):

    CONTROLS = [
        ['GUI', None, 'guifg="%s" guibg="%s"', 'color'],
        ['CTERM', Palette(CTERM_COLORS), 'ctermfg=%d ctermbg=%d', 'index'],
        ['TERM', Palette(TERM_COLORS), 'termbg=%d termfg=%d', 'index']
    ]

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('Color Picker')

        self.default_bg = Color('#eeeeee')
        self.default_fg = Color('#000000')

        self.colors = []

        icon = self.render_icon(gtk.STOCK_COLOR_PICKER, gtk.ICON_SIZE_MENU)
        self.set_icon(icon)

        self.set_size_request(670, -1)
        self.set_resizable(False)
        self.set_border_width(10)

        self.make_ui()

    def make_label(self, text, alignment=0, markup=False):
        label = gtk.Label()
        label.set_alignment(alignment, 0.5)

        if markup:
            label.set_markup(text)
        else:
            label.set_text(text)

        return label

    def make_ui(self):
        container = gtk.Table(len(self.CONTROLS) * 2 + 3, 3)

        for index, group in enumerate(self.CONTROLS):
            row = index * 2

            container.attach(self.make_label('%s FG' % group[0]), 0, 1, row, row + 1, gtk.FILL, 0, 10)
            container.attach(self.make_label('%s BG' % group[0]), 0, 1, row + 1, row + 2, gtk.FILL, 0, 10)

            preview = PreviewEntry()
            preview.set_bg_color(self.default_bg.gtk)
            preview.set_fg_color(self.default_fg.gtk)

            fg_button = PaletteColorButton(group[1], self.default_fg)
            bg_button = PaletteColorButton(group[1], self.default_bg)

            fg_button.connect('color-changed', self.fg_changed, preview)
            bg_button.connect('color-changed', self.bg_changed, preview)

            container.attach(fg_button, 1, 2, row, row + 1, 0, gtk.FILL, 5)
            container.attach(bg_button, 1, 2, row + 1, row + 2, 0, gtk.FILL, 5)
            container.attach(preview, 2, 3, row, row + 2)
            container.set_row_spacing(row + 1, 15)

            self.colors.append(group[2:] + [fg_button, bg_button])

        last_row = len(container)

        container.attach(self.make_label('<b>Result:</b>', 0.5, True), 0, 3, last_row, last_row + 1)
        last_row += 1

        self.result = gtk.Entry()
        self.result.set_property('editable', False)
        self.result.set_alignment(0.5)
        self.set_can_focus(False)

        container.attach(self.result, 0, 3, last_row, last_row + 1, gtk.FILL | gtk.EXPAND, gtk.FILL, 0, 10)
        last_row += 1

        container.attach(
            self.make_label("<i>Hint: you can drag &amp; drop color buttons. Their colors be approximized as needed.</i>", 0.5, True),
            0, 3,
            last_row,
            last_row + 1,
            gtk.FILL | gtk.EXPAND,
            gtk.FILL
        )

        container.show_all()
        self.add(container)
        self.make_result()

    def fg_changed(self, btn, color, index, preview):
        preview.set_fg_color(color.gtk)
        self.make_result()

    def bg_changed(self, btn, color, index, preview):
        preview.set_bg_color(color.gtk)
        self.make_result()

    def make_result(self):
        text = 'hl Example ' + " ".join([
            group[0] % tuple([getattr(color, group[1]) for color in group[2:]])
            for group in self.colors
        ])

        self.result.set_text(text)

if __name__ == '__main__':
    window = Picker()
    window.connect('delete-event', gtk.main_quit)
    window.show()
    gtk.main()
