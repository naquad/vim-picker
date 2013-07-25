"""
Color wrapper and palette implementation.
"""
import gtk
from colorop import rgb_to_xyz, xyz_to_laab, color_diff_laab

class Color:
    def __init__(self, string):
        if isinstance(string, str):
            self.gtk = gtk.gdk.color_parse(string)
        elif isinstance(string, gtk.gdk.Color):
            self.gtk = string

        # because CIEDE2000 works with L*ab to save some CPU time
        # L*ab version of color is stored too
        self.laab = xyz_to_laab(*rgb_to_xyz(self.red, self.green, self.blue))

    def __rsub__(self, other):
        return color_diff_laab(self.laab, other.laab)

    def __eq__(self, other):
        return self.gtk == other.gtk

    def __ne__(self, other):
        return self.gtk != other.gtk

    def __lt__(self, other):
        return self.gtk < other.gtk

    def __gt__(self, other):
        return self.gtk > other.gtk

    def __le__(self, other):
        return self.gtk <= other.gtk

    def __ge__(self, other):
        return self.gtk >= other.gtk

    @property
    def red(self):
        return self.gtk.red / 256

    @property
    def green(self):
        return self.gtk.green / 256

    @property
    def blue(self):
        return self.gtk.blue / 256

    def __str__(self):
        return '#%02x%02x%02x' % (self.red, self.green, self.blue)

    def full_str(self):
        return self.gtk.to_string()

    def __repr__(self):
        return '<Color: %s>' % str(self)

    @classmethod
    def parse(self, string):
        return self(string)

class Palette(list):
    def __init__(self, colors):
        super(Palette, self).__init__(map(Color.parse, colors))

    def approximate(self, target):
        matched_color = self[0]
        matched_index = 0
        matched_diff = 10000

        for index, color in enumerate(self):
            diff = color - target
            if matched_diff > diff:
                matched_diff, matched_color, matched_index = diff, color, index

        return matched_index, matched_color
