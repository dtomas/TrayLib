import gtk


def scale_pixbuf_to_size(pixbuf, size, scale_up = True):
    """
    Returns a pixbuf scaled to the given size. 
    
    @param size: The size of the scaled pixbuf.
    @param scale_up: If False, it is only scaled down if too large and not 
        scaled up.
    @return: A pixbuf scaled to the given size.
    """
    size = int(size)
    width = pixbuf.get_width()
    height = pixbuf.get_height()
    if width > height:
        ratio = float(height)/float(width)
        if width > size or (width < size and scale_up):
            pixbuf = pixbuf.scale_simple(size, max(1, int(size*ratio)), 
                                        gtk.gdk.INTERP_TILES)
    else:
        ratio = float(width)/float(height)
        if height > size or (height < size and scale_up):
            pixbuf = pixbuf.scale_simple(max(1, int(size*ratio)), size,
                                            gtk.gdk.INTERP_TILES)
    return pixbuf

