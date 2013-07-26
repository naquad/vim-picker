#!/usr/bin/python2
"""
Main window implementation.
"""
import gtk
from palettes import CTERM_COLORS, TERM_COLORS
from color import Color, Palette
from paletteui import PaletteColorButton
from preview import PreviewEntry
import re

class Parser(gtk.Dialog):

    NAMED_COLORS = {
        'GUI': {
            "black":        '#000000',
            "darkgray":     '#808080',
            "darkgrey":     '#808080',
            "gray":         '#c0c0c0',
            "grey":         '#c0c0c0',
            "lightgray":    '#e0e0e0',
            "lightgrey":    '#e0e0e0',
            "gray10":       '#1a1a1a',
            "grey10":       '#1a1a1a',
            "gray20":       '#333333',
            "grey20":       '#333333',
            "gray30":       '#4d4d4d',
            "grey30":       '#4d4d4d',
            "gray40":       '#666666',
            "grey40":       '#666666',
            "gray50":       '#7f7f7f',
            "grey50":       '#7f7f7f',
            "gray60":       '#999999',
            "grey60":       '#999999',
            "gray70":       '#b3b3b3',
            "grey70":       '#b3b3b3',
            "gray80":       '#cccccc',
            "grey80":       '#cccccc',
            "gray90":       '#e5e5e5',
            "grey90":       '#e5e5e5',
            "white":        '#ffffff',
            "darkred":      '#800000',
            "red":          '#ff0000',
            "lightred":     '#ffa0a0',
            "darkblue":     '#000080',
            "blue":         '#0000ff',
            "lightblue":    '#a0a0ff',
            "darkgreen":    '#008000',
            "green":        '#00ff00',
            "lightgreen":   '#a0ffa0',
            "darkcyan":     '#008080',
            "cyan":         '#00ffff',
            "lightcyan":    '#a0ffff',
            "darkmagenta":  '#800080',
            "magenta":      '#ff00ff',
            "lightmagenta": '#ffa0ff',
            "brown":        '#804040',
            "yellow":       '#ffff00',
            "lightyellow":  '#ffffa0',
            "darkyellow":   '#bbbb00',
            "seagreen":     '#2e8b57',
            "orange":       '#ffa500',
            "purple":       '#a020f0',
            "slateblue":    '#6a5acd',
            "violet":       '#ee82ee',
        },

        'CTERM': {
            'black':         0,
            'darkblue':      1,
            'darkgreen':     2,
            'darkcyan':      3,
            'darkred':       4,
            'darkmagenta':   5,
            'brown':         6,
            'darkyellow':    6,
            'lightgrey':     7,
            'lightgrey':     7,
            'lightgray':     7,
            'lightgray':     7,
            'gray':          7,
            'grey':          7,
            'darkgray':      8,
            'darkgrey':      8,
            'blue':          9,
            'lightblue':     9,
            'green':         10,
            'lightgreen':    10,
            'cyan':          11,
            'lightcyan':     11,
            'red':           12,
            'lightred':      12,
            'magenta':       13,
            'lightmagenta':  13,
            'yellow':        14,
            'lightyellow':   14,
            'white':         15
        },

        'TERM': {
            'black':         0,
            'darkgrey':      0,
            'darkgray':      0,
            'darkred':       1,
            'lightred':      1,
            'red':           1,
            'darkgreen':     2,
            'lightgreen':    2,
            'green':         2,
            'darkyellow':    3,
            'brown':         3,
            'lightyellow':   3,
            'yellow':        3,
            'lightblue':     4,
            'blue':          4,
            'darkblue':      4,
            'darkmagenta':   5,
            'lightmagenta':  5,
            'magenta':       5,
            'lightcyan':     6,
            'cyan':          6,
            'darkcyan':      6,
            'lightgrey':     7,
            'gray':          7,
            'grey':          7,
            'white':         7,
        }
    }

    MATCHERS = {
        'GUI':      [
                        re.compile(r'''\bguifg=(["']?)(#[\dA-Fa-f]{3,6}|\w+)\1'''),
                        re.compile(r'''\bguibg=(["']?)(#[\dA-Fa-f]{3,6}|\w+)\1''')
                    ],
        'CTERM':    [
                        re.compile(r'''\bctermfg=(["']?)(\d+|\w+)\1'''),
                        re.compile(r'''\bctermbg=(["']?)(\d+|\w+)\1''')
                    ],
        'TERM':     [
                        re.compile(r'''\btermfg=(["']?)(\d+|\w+)\1'''),
                        re.compile(r'''\btermbg=(["']?)(\d+|\w+)\1''')
                    ]
    }

    def __init__(self, parent):
        gtk.Dialog.__init__(self, 'Parse Line', parent, gtk.DIALOG_MODAL,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.main_window = parent

        self.set_border_width(5)

        self.entry = gtk.Entry()
        self.entry.connect('changed', self.parse_line_wrap)
        self.entry.connect('key-press-event', self.catch_enter)
        self.result_label = gtk.Label()
        self.result_label.set_alignment(0, 0.5)

        self.set_resizable(False)

        container = self.get_content_area()
        container.pack_start(gtk.Label('Enter the line:'))
        container.pack_start(self.entry, padding=10)
        container.pack_end(self.result_label)
        container.show_all()
        self.parse_line('')

        self.connect('response', self.on_response)

    def catch_enter(self, me, evt):
        if evt.keyval == gtk.keysyms.Return or evt.keyval == gtk.keysyms.KP_Enter:
            self.parse_line_wrap()
            self.response(gtk.RESPONSE_ACCEPT)

    def on_response(self, me, response):
        if response == gtk.RESPONSE_ACCEPT:
            self.main_window.set_colors(**self.result)
        self.destroy()

    def parse_line_wrap(self, *not_used):
        self.parse_line(self.entry.get_text())

    def parse_line(self, txt):
        self.result = {}
        result_text = ''

        for group, matchers in self.MATCHERS.iteritems():
            for suffix, matcher in zip(('FG', 'BG'), matchers):
                color = matcher.search(txt)

                if color:
                    color = color.group(2)
                    if (group == 'GUI' and not color.startswith('#')) or \
                       (group != 'GUI' and not color.isdigit()):
                        color = self.NAMED_COLORS[group].get(color.lower())

                result_text += "%s %s = %s\n" % (group, suffix, color or '<no match>')

                if isinstance(color, str) and color.isdigit():
                    color = int(color)

                self.result.setdefault(group, [])
                self.result[group].append(color)

        self.result_label.set_text(result_text)

class Picker(gtk.Window):

    CONTROLS = [
        ['GUI', None, 'guifg="%s" guibg="%s"', 'color'],
        ['CTERM', Palette(CTERM_COLORS), 'ctermfg=%d ctermbg=%d', 'index'],
        ['TERM', Palette(TERM_COLORS), 'termfg=%d termbg=%d', 'index']
    ]

    def __init__(self):
        gtk.Window.__init__(self)

        self.set_title('VIM Color Picker')

        self.default_bg = Color('#eeeeee')
        self.default_fg = Color('#000000')

        icon = self.render_icon(gtk.STOCK_COLOR_PICKER, gtk.ICON_SIZE_MENU)
        self.set_icon(icon)
        gtk.window_set_default_icon(icon)

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

            fg_label = '%s FG' % group[0]
            bg_label = '%s BG' % group[0]

            container.attach(self.make_label(fg_label), 0, 1, row, row + 1, gtk.FILL, 0, 10)
            container.attach(self.make_label(bg_label), 0, 1, row + 1, row + 2, gtk.FILL, 0, 10)

            preview = PreviewEntry()
            preview.set_bg_color(self.default_bg.gtk)
            preview.set_fg_color(self.default_fg.gtk)

            fg_button = PaletteColorButton(group[1], self.default_fg, 'Choose %s' % fg_label)
            bg_button = PaletteColorButton(group[1], self.default_bg, 'Choose %s' % bg_label)

            fg_button.connect('color-changed', self.fg_changed, preview)
            bg_button.connect('color-changed', self.bg_changed, preview)

            container.attach(fg_button, 1, 2, row, row + 1, 0, gtk.FILL, 5)
            container.attach(bg_button, 1, 2, row + 1, row + 2, 0, gtk.FILL, 5)
            container.attach(preview, 2, 3, row, row + 2)
            container.set_row_spacing(row + 1, 15)

            group.extend([fg_button, bg_button])

        last_row = len(container)

        container.attach(self.make_label('<b>Result:</b>', 0.5, True), 0, 3, last_row, last_row + 1)
        last_row += 1

        self.result = gtk.Entry()
        self.result.set_property('editable', False)
        self.result.set_alignment(0.5)
        self.set_can_focus(False)

        container.attach(self.result, 0, 3, last_row, last_row + 1, gtk.FILL | gtk.EXPAND, gtk.FILL, 0, 10)
        last_row += 1

        btn = gtk.Button('Parse line')
        btn.connect('clicked', self.parse_dialog)
        container.attach(btn, 0, 3, last_row, last_row + 1, gtk.FILL | gtk.EXPAND, gtk.FILL)
        last_row += 1

        container.attach(
            self.make_label("<i>Hint: you can drag &amp; drop color buttons. Their colors will be approximized as needed.</i>", 0.5, True),
            0, 3,
            last_row,
            last_row + 1,
            gtk.FILL | gtk.EXPAND,
            gtk.FILL
        )

        container.show_all()
        self.add(container)
        self.make_result()

    def parse_dialog(self, btn):
        Parser(self).show()

    def set_colors(self, **colors):
        for group in self.CONTROLS:
            if group[0] in colors:
                for idx, color in enumerate(colors[group[0]]):
                    if color:
                        getattr(group[idx + 4], 'set_%s' % group[3])(color)

    def fg_changed(self, btn, color, index, preview):
        preview.set_fg_color(color.gtk)
        self.make_result()

    def bg_changed(self, btn, color, index, preview):
        preview.set_bg_color(color.gtk)
        self.make_result()

    def make_result(self):
        text = 'hl Example ' + " ".join([
            group[2] % tuple([getattr(color, group[3]) for color in group[4:]])
            for group in self.CONTROLS
        ])

        self.result.set_text(text)

if __name__ == '__main__':
    window = Picker()
    window.connect('delete-event', gtk.main_quit)
    window.show()
    gtk.main()
