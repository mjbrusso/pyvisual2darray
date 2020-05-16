from tkinter import *
import gui2darray
import random
from collections import UserList

# TODO:  messageBox, rezize(r, c)


class Board(UserList):
    def __init__(self, nrows, ncols):
        UserList.__init__(self)             # Initialize parent class
        # Create list [ncols][nrows]
        self.extend([self.BoardRow(ncols, self) for _ in range(nrows)])

        self._isrunning = False
        self._nrows = nrows
        self._ncols = ncols
        # Array used to store cells elements (rectangles)
        self._cells = [[None] * ncols for _ in range(nrows)]
        self._title = "GUI2DArray"            # Default window title
        self._cursor = "hand1"                # Default mouse cursor
        self._margin = 5                      # board margin (px)
        self._cell_spacing = 1                # grid cell_spacing (px)
        self._margin_color = "light grey"     # default border color
        self._cell_color = "white"            # default cell color
        self._grid_color = "black"            # default grid color
        self._root = Tk()
        # cell's container
        self._canvas = Canvas(self._root, highlightthickness=0)
        # event bindings
        self._on_key_press = None
        self._on_mouse_click = None
        self._timer_interval = 0
        self._on_timer = None
        self._root.bind("<Key>", self._key_press_clbk)
        self._canvas.bind("<ButtonPress>", self._mouse_click_clbk)
        self._msgbar = None

    def __getitem__(self, row):           # subscript getter
        self.BoardRow.current_i = row       # Store last accessed row
        return super().__getitem__(row)   # return a BoardRow

    # Properties

    @property
    def title(self):
        """
        Gets or sets the window title.
        """
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self._root.title(value)

    @property
    def cursor(self):
        """
        Gets or sets the mouse cursor shape.
        """
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value
        self._canvas.configure(cursor=value)

    @property
    def margin(self):
        """
        Gets or sets the board margin.
        """
        return self._margin

    @margin.setter
    def margin(self, value):
        if self._isrunning:
            raise Exception("Can't update margin after run()")
        self._margin = value
        self._root.configure(padx=value, pady=value)

    @property
    def cell_spacing(self):
        """
        Gets or sets the space between cells.
        """
        return self._cell_spacing

    @cell_spacing.setter
    def cell_spacing(self, value):
        if self._isrunning:
            raise Exception("Can't update cell_spacing after run()")
        self._cell_spacing = value
        self._resize()

    @property
    def margin_color(self):
        """
        Gets or sets the margin_color.
        """
        return self._margin_color

    @margin_color.setter
    def margin_color(self, value):
        self._margin_color = value
        self._root.configure(bg=value)

    @property
    def cell_color(self):
        """
        Gets or sets cells color
        """
        return self._cell_color

    @cell_color.setter
    def cell_color(self, value):
        self._cell_color = value
        # Update bgcolor for all cells
        if self._isrunning:
            for row in self._cells:
                for cell in row:
                    cell.bg = value

    @property
    def grid_color(self):
        """
        Gets or sets grid color
        """
        return self._grid_color

    @grid_color.setter
    def grid_color(self, value):
        self._grid_color = value
        self._canvas.configure(bg=value)

    @property
    def cell_size(self):
        """
        Gets or sets the cells dimension
        """
        return gui2darray.Cell.size

    @cell_size.setter
    def cell_size(self, value):
        if self._isrunning:
            raise Exception("Can't resize cells after run()")
        # size is a tuple (width, height)
        if not type(value) is tuple:
            v = int(value)
            value = (v, v)
        gui2darray.Cell.size = value    # All cells has same size (class field)
        self._resize()

    # Methods

    def run(self):              # Show and start running
        self.setupUI()
        self._isrunning = True
        self._root.mainloop()

    # Random shuffle
    # Copy all values to an array, random.shuffle it, then copy back
    def shuffle(self):
        a = []
        for r in self:
            a.extend(r)
        random.shuffle(a)
        for row in self:
            for c in range(self._ncols):
                row[c] = a.pop()

    # Fill the board (or a row, or a collumn) whith a value
    def fill(self, value, row=None, col=None):
        if row is None and col is None:
            for r in range(self._nrows):
                for c in range(self._ncols):
                    self[r][c] = value
        elif not row is None and col is None:
            for c in range(self._ncols):
                self[row][c] = value
        elif row is None and not col is None:
            for r in range(self._nrows):
                self[r][col] = value
        else:
            raise Exception("Invalid argument supplied (row= AND col=)")

    # Clear board
    def clear(self):
        self.fill(None)

    def _resize(self):
        self._canvas.config(width=self._ncols*(gui2darray.Cell.width+self.cell_spacing)-1,
                            height=self._nrows*(gui2darray.Cell.height+self.cell_spacing))

    # Translate [row][col] to canvas coordinates
    def _rc2xy(self, row, col):
        x = col*(gui2darray.Cell.width+self.cell_spacing)
        y = row*(gui2darray.Cell.height+self.cell_spacing)
        return (x, y)

    # Translate canvas coordinates to (row, col)
    def _xy2rc(self, x, y):
        # how can i optimize it ???? May be _self.canvas.find_withtag(CURRENT)
        for r in range(self._nrows):
            for c in range(self._ncols):
                cell = self._cells[r][c]
                if cell.x < x < cell.x + gui2darray.Cell.width \
                        and cell.y < y < cell.y + gui2darray.Cell.height:
                    return (r, c)
        return None

    def setupUI(self):
        self._root.resizable(False, False)            # Window is not resizable
        self.margin_color = self._margin_color        # Paint background
        self.grid_color = self._grid_color            # Table inner lines
        self.cell_color = self._cell_color            # Cells background
        self.margin = self._margin                    # Change root's margin
        self.cell_spacing = self._cell_spacing        # Change root's padx/y
        self.title = self._title                      # Update window's title
        self.cursor = self._cursor
        # Create all cells
        for r in range(self._nrows):
            for c in range(self._ncols):
                x, y = self._rc2xy(r, c)
                newcell = gui2darray.Cell(self._canvas, x, y)
                newcell.bgcolor = self._cell_color
                self._cells[r][c] = newcell
                if self[r][c] != None:                      # Cell already has a value
                    self.notify_change(r, c, self[r][c])    # show it

        self._canvas.pack()
        self._root.update()

    def close(self):
        self._root.quit()

    def create_output(self, **kwargs):
        if self._msgbar is None:
            self._msgbar = gui2darray.OutputBar(self._root, **kwargs)

    def print(self, *objects, sep=' ', end=''):
        if self._msgbar:
            s =  sep.join(str(obj) for obj in objects) + end
            self._msgbar.show(s)

    # Events

    def notify_change(self, row, col, new_value):
        if self._cells[row][col] != None:
            self._cells[row][col].value = new_value

    # Keyboard events
    @property
    def on_key_press(self):
        return self._on_key_press

    @on_key_press.setter
    def on_key_press(self, value):
        self._on_key_press = value

    def _key_press_clbk(self, ev):
        if callable(self._on_key_press):
            self._on_key_press(ev.keysym)

    # Mouse click events
    @property
    def on_mouse_click(self):
        return self._on_mouse_click

    @on_mouse_click.setter
    def on_mouse_click(self, value):
        self._on_mouse_click = value

    def _mouse_click_clbk(self, ev):
        # print(self._canvas.find_withtag(CURRENT))
        if callable(self._on_mouse_click):
            rc = self._xy2rc(ev.x, ev.y)
            if rc:
                self._on_mouse_click(ev.num, rc[0], rc[1])

    # Timer events
    @property
    def timer_interval(self):
        return self._timer_interval

    @timer_interval.setter
    def timer_interval(self, value):
        if value != self._timer_interval:       # changed
            self._timer_interval = value
            if value > 0:
                self._root.after(value, self._timer_clbk)

    @property
    def on_timer(self):
        return self._on_timer

    @on_timer.setter
    def on_timer(self, value):
        self._on_timer = value

    def _timer_clbk(self):
        intv = self._timer_interval or 0
        if intv > 0:
            if callable(self._on_timer):
                self._on_timer()
            self._root.after(intv, self._timer_clbk)

    # Inner class
    # A row is a list, so I can use the magic function __setitem__(board[i][j])
    class BoardRow(UserList):
        # Last acessed row (class member).
        # Yes, its not thread safe!
        # Maybe in the future I will use a proxy class
        current_i = None

        def __init__(self, length, parent):
            UserList.__init__(self)
            self.extend([None] * length)         # Initialize the row
            self._parent = parent           # the board

        def __setitem__(self, j, value):
            self._parent.notify_change(self.__class__.current_i, j, value)
            return super().__setitem__(j, value)
