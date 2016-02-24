import gtk


def scale_pixbuf_to_size(pixbuf, size, scale_up=True):
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
        ratio = float(height) / float(width)
        if width > size or (width < size and scale_up):
            pixbuf = pixbuf.scale_simple(
                size, max(1, int(size*ratio)), gtk.gdk.INTERP_TILES
            )
    else:
        ratio = float(width) / float(height)
        if height > size or (height < size and scale_up):
            pixbuf = pixbuf.scale_simple(
                max(1, int(size*ratio)), size, gtk.gdk.INTERP_TILES
            )
    return pixbuf


def convert_to_greyscale(pixbuf):
    dest_pixbuf = gtk.gdk.Pixbuf(
        pixbuf.get_colorspace(),
        pixbuf.get_has_alpha(),
        pixbuf.get_bits_per_sample(),
        pixbuf.get_width(),
        pixbuf.get_height(),
    )
    pixbuf.saturate_and_pixelate(dest_pixbuf, 0.0, False)
    return dest_pixbuf


def change_alpha(pixbuf, alpha):
    dest_pixbuf = gtk.gdk.Pixbuf(
        pixbuf.get_colorspace(),
        pixbuf.get_has_alpha(),
        pixbuf.get_bits_per_sample(),
        pixbuf.get_width(),
        pixbuf.get_height(),
    )
    dest_pixbuf.fill(0)
    pixbuf.composite(
        dest_pixbuf, 0, 0, pixbuf.get_width(), pixbuf.get_height(),
        0, 0, 1, 1, gtk.gdk.INTERP_TILES, alpha
    )
    return dest_pixbuf
