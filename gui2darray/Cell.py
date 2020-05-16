from tkinter import *
import gui2darray


# Metaclass for Cell 
# Implement static class properties
class CellProperties(type):
    @property
    def width(cls):
        """
        Gets cell width
        """
        return cls.size[0]

    @property
    def height(cls):
        """
        Gets cell height
        """
        return cls.size[1]

class Cell(object, metaclass=CellProperties):  
    size = (50, 50)                 # (w, h: px) Same size for all cells, so it's a static class member 
    def __init__(self, parent, x, y):
        self._image_id = None       # tkinter id from create_image
        self._value = None          # this value
        self._parent = parent  
        self._x = x  
        self._y = y
        self._bgcolor = "white"
        self._id = parent.create_rectangle(
            x,
            y,
            x+Cell.width,
            y+Cell.height,
            width=0
        )
    
    @property
    def id(self):
        """
        Gets the rectangle id
        """
        return self._id

    @property
    def value(self):
        """
        Gets or sets the cell value.
        """
        return self._value
    
    @value.setter
    def value(self, v):
        if self._value != v:        # Only update when value change
            self._value = v
            if self._image_id:
                self._parent.delete(self._image_id)    # clear current image
            if not v is None:   
                img = gui2darray.ImageMap.get_instance()[v]
                hc = self._x + Cell.width // 2     # horizontal center
                vc = self._y + Cell.height // 2    # vertical center
                # Show image @ canvas center
                self._image_id = self._parent.create_image(hc, vc, anchor=CENTER, image=img)

    @property
    def bgcolor(self):
        """
        Gets or sets the background color.
        """
        return self._bgcolor

    @bgcolor.setter
    def bgcolor(self, value):
        self._bgcolor = value
        self._parent.itemconfig(self._id, fill=value)
    
    @property
    def x(self):
        """
        Gets x coordinate.
        """
        return self._x

    @property
    def y(self):
        """
        Gets y coordinate.
        """
        return self._y

