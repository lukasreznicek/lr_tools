import bpy
from bpy.app.handlers import persistent


@persistent
def lr_palette(scene):
    pal = bpy.data.palettes.get("LR_ID")
    if pal is None:
        pal = bpy.data.palettes.new("LR_ID")
        # add a color to that palette
        red = pal.colors.new()
        red.color = (1, 0, 0)
        red.weight = 1.0

        green = pal.colors.new()
        green.color = (0, 1, 0)
        green.weight = 1.0

        blue = pal.colors.new()
        blue.color = (0, 0, 1)
        blue.weight = 1.0

        cyan = pal.colors.new()
        cyan.color = (0, 1, 1)
        cyan.weight = 1.0

        saddlebrown = pal.colors.new()
        saddlebrown.color = (0.55, 0.27, 0.07)
        saddlebrown.weight = 1.0

        forestgreen = pal.colors.new()
        forestgreen.color = (0.13, 0.55, 0.13)
        forestgreen.weight = 1.0

        steelblue = pal.colors.new()
        steelblue.color = (0.27, 0.51, 0.71)
        steelblue.weight = 1.0

        indigo = pal.colors.new()
        indigo.color = (0.29, 0, 0.51)
        indigo.weight = 1.0

        laserlemon = pal.colors.new()
        laserlemon.color = (1, 1, 0.33)
        laserlemon.weight = 1.0

        deeppink = pal.colors.new()
        deeppink.color = (1, 0.08, 0.58)
        deeppink.weight = 1.0

        bisque = pal.colors.new()
        bisque.color = (1, 0.89, 0.77)
        bisque.weight = 1.0

        white = pal.colors.new()
        white.color = (1, 1, 1)
        white.weight = 1.0

        black = pal.colors.new()
        black.color = (0, 0, 0)
        black.weight = 1.0

        gray = pal.colors.new()
        gray.color = (0.5, 0.5, 0.5)
        gray.weight = 1.0

        #make red active
        pal.colors.active = red

    bpy.context.tool_settings.vertex_paint.palette = pal
    # ts.vertex_paint.palette = pal


