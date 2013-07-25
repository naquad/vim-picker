VIM Color Picker
================

Why?
----

When you're editing VIMs syntax files you have dozens of `hl` statements.
Each statement has 6 color parameters:

* guifg - for gVIM text color
* guibg - for gVIM text background color
* ctermbg - text color for 256-colored terminal
* ctermfg - text background color for 256-colored terminal
* termfg - 8-color terminal text color
* termbg - 8-color terminal background color

And they all must look alike. Well, thats the plan at least.

The problem is that you should not just make up your color scheme,
but also code it, test it and make all types of terminals look alike.
This is daunting. Very daunting.

Recently I've been trying to do that and came to conclusion that I'm doing it wrong
and made this project.

Features
--------

* Implements [CIEDE2000](http://en.wikipedia.org/wiki/Color_difference#CIEDE2000) algorithm
  for automatically matching your colors (especially useful for 256-GUI hex matching).
* Nicely previews of result.
* Generates `hl` like so you won't have to type colors yourself. 
* Drag and drop colors around. After you've chosen one color you can just drag & drop it to others.
  Color will be approximated as needed.

Screenshots
----------

![GUI chooser](http://i.imgur.com/jRP7Nlyh.jpg "gui-chooser")

![CTERM chooser](http://i.imgur.com/qdvBXhoh.jpg "256-color-chooser")

![TERM chooser](http://i.imgur.com/5FvegPZh.jpg "8-color-chooser")

Don't be afraid of that huge palette, you can still use color wheel. Its value will
be used to find nearest color.

Requirements
------------

Requires Python 2.7 and Gtk2 Python bindings.

Usage
-----

```
$ git clone https://github.com/naquad/vim-picker.git
$ cd vim-picker
$ ./picker.py
```

You may have to change first line of `picker.py` to make sure
it points to right Python interpreter.

Credits
-------
Thanks to [EasyRGB](http://www.easyrgb.com) for CIEDE2000 implementation. 

Bugs & Features
---------------

All goes to [issues](https://github.com/naquad/vim-picker/issues).
