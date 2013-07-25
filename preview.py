import gtk
import pango

class PreviewEntry(gtk.Entry):
    def __init__(self, text='Example Preview'):
        gtk.Entry.__init__(self)
        self.set_text(text)
        self.set_inner_border(gtk.Border(15, 15, 15, 15))
        self.set_alignment(0.5)

        self.font = self.get_style().font_desc.copy()
        self.font.set_size(16 * pango.SCALE)
        self.bg_color = None
        self.fg_color = None
        self.change_style()

    def alloc_color(self, color):
        return self.get_colormap().alloc_color(color)

    def set_bg_color(self, color):
        self.bg_color = color
        self.change_style()

    def set_fg_color(self, color):
        self.fg_color = color
        self.change_style()

    def change_style(self):
        style = gtk.RcStyle()
        style.font_desc = self.font
        style.xthickness = 0
        style.ythickness = 0

        for state in [gtk.STATE_NORMAL, gtk.STATE_ACTIVE, gtk.STATE_PRELIGHT, gtk.STATE_INSENSITIVE]:
            if self.bg_color is not None:
                style.bg[state] = self.bg_color
                style.base[state] = self.bg_color

            if self.fg_color is not None:
                style.fg[state] = self.fg_color
                style.text[state] = self.fg_color

        self.modify_style(style)
