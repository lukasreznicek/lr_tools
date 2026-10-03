import os
from bpy.utils import previews

collection = None


def register():
    global collection
    icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")
    collection = previews.new()
    for name in ("red", "green", "blue", "white", "black"):
        collection.load(f"ico_{name}", os.path.join(icons_dir, f"lr_ico_{name}.png"), 'IMAGE')


def unregister():
    previews.remove(collection)
