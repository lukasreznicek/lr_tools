# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "LR Tools",
    "author" : "Lukas Reznicek",
    "description" : "Set of tools for workflow simplification",
    "blender" : (2, 82, 0),
    "version" : (1, 1, 0),
    "location" : "",
    "warning" : "",
    "category" : "UV"
}

import bpy

from . import handlers, keymaps, preferences, properties
from .operators import classes as operator_classes
from .ui import classes as ui_classes, menus
from .utils import icons

classes = (
    preferences.AddonPreferences,
    properties.lr_tool_settings_object,
    properties.lr_tool_settings,
    *operator_classes,
    *ui_classes,
)


def register():
    icons.register()

    # load_post handler is needed to get scene access
    bpy.app.handlers.load_post.append(handlers.lr_palette)

    for cls in classes:
        bpy.utils.register_class(cls)

    menus.register()

    bpy.types.Scene.lr_tools_object = bpy.props.PointerProperty(type=properties.lr_tool_settings_object)
    bpy.types.Scene.lr_tools = bpy.props.PointerProperty(type=properties.lr_tool_settings)

    keymaps.register_keymaps()


def unregister():
    bpy.app.handlers.load_post.remove(handlers.lr_palette)
    menus.unregister()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.lr_tools
    del bpy.types.Scene.lr_tools_object

    icons.unregister()
    keymaps.unregister_keymaps()
