from traylib import LEFT
from traylib.main_item import MainItem
from traylib.item_box import ItemBox


def manage_main_box(tray, tray_config, create_main_item=MainItem):
    """
    Manages a box containing a main item.

    @param tray: The L{Tray} to manage.
    @param tray_config: The L{TrayConfig}.
    @param create_main_item: Callable creating a main item for the tray.
    """

    main_box = ItemBox("main")

    def reorder_main_box():
        if tray_config.menus == LEFT:
            tray.reorder_box(main_box, 0)
        else:
            tray.reorder_box(main_box, len(tray.boxes) - 1)

    def box_added(tray, box):
        reorder_main_box()

    tray_handlers = []

    def menus_changed(tray_config):
        reorder_main_box()

    tray_config_handlers = []

    def manage():
        main_box.add_item(create_main_item(tray))
        tray.add_box(main_box)
        reorder_main_box()
        tray_handlers.append(tray.connect("box-added", box_added))
        tray_config_handlers.append(
            tray_config.connect("menus-changed", menus_changed)
        )
        yield None

    def unmanage():
        tray.remove_box(main_box)
        for handler in tray_handlers:
            tray.disconnect(handler)
            tray_handlers.remove(handler)
            yield None
        for handler in tray_config_handlers:
            tray_config.disconnect(handler)
            tray_config_handlers.remove(handler)
            yield None

    return manage, unmanage
