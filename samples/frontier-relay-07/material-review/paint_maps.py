"""Author opaque sRGB graphics for the existing surface UVs."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SIZE = 1024
SCALE = 2
BOUNDS = {
    "side": (-2.36, 1.51, .40, 3.08),
    "roof": (-3.00, 3.70, -.22, 1.00),
    "column": (-1.77, -.71, 1.50, 3.02),
    "stairs": (-1.24, 2.03, -3.62, -2.32),
}
SWATCHES = {
    "marks": {"enamel": "#d1cfc4", "lime": "#cfe80b", "deck": "#82807a",
              "ink": "#2c2e30", "signal": "#dd4a23", "stripe": "#c5db13"},
    "finish": {"enamel": "#c9c8be", "lime": "#aebc25", "deck": "#7c7b77",
               "ink": "#2e3031", "signal": "#d6441b", "stripe": "#c8d537"},
}


def draw_map(stage, surface, colors):
    from PIL import Image, ImageDraw

    x0,x1,y0,y1 = BOUNDS[surface]
    n = SIZE * SCALE
    base = {"side":"enamel", "roof":"enamel", "column":"lime", "stairs":"deck"}[surface]
    image = Image.new("RGB", (n,n), colors[base])
    draw = ImageDraw.Draw(image)

    def poly(points, swatch):
        pixels = [(round((x-x0)/(x1-x0)*(n-1)),round((y1-y)/(y1-y0)*(n-1)))
                  for x,y in points]
        draw.polygon(pixels, fill=colors[swatch])

    if surface == "side":
        # Hand-drawn stencil-style outlines, laid out in side-wall metres.
        left, bottom = -1.57, 1.055
        def digit(outline, swatch):
            poly([(left+x,bottom+z*.91) for x,z in outline], swatch)
        digit([(0,.13),(.11,0),(.67,0),(.81,.14),(.81,.82),
               (.69,.96),(.13,.96),(0,.83)], "ink")
        digit([(.21,.23),(.24,.20),(.60,.20),(.63,.24),(.63,.73),
               (.60,.77),(.24,.77),(.21,.74)], "enamel")
        digit([(.94,.96),(1.68,.96),(1.68,.77),(1.32,0),
               (1.06,0),(1.43,.75),(.94,.75)], "ink")
        for z in (1.16,1.36,1.56):
            poly([(.51,z),(1.28,z),(1.28,z+.143),(.51,z+.143)], "signal")
        if stage == "finish":
            colors = {**colors, "joint": "#9a9992"}
            poly([(-1.96,.89),(-1.947,.89),(-1.947,3.07),(-1.96,3.07)], "joint")
    elif surface == "roof":
        for x, width in ((.01,.42),(.65,.45),(1.31,.62)):
            poly([(x,-.11),(x+width,-.11),(x+width+.63,.505),(x+.63,.505)], "stripe")
        if stage == "finish":
            colors = {**colors, "joint": "#a7a69d"}
            poly([(-.57,.52),(-.56,.52),(-.56,.99),(-.57,.99)], "joint")
    elif surface == "column":
        poly([(-1.665,2.32),(-1.665,2.52),(-1.51,2.72),(-1.36,2.72)], "ink")
        poly([(-1.665,2.04),(-1.665,2.23),(-1.29,2.72),(-1.14,2.72)], "ink")
    else:
        for x in (-1.08,1.64):
            poly([(x,y0),(x+.145,y0),(x+.145,y1),(x,y1)], "stripe")
    out = ROOT / "textures" / stage
    out.mkdir(parents=True,exist_ok=True)
    image.resize((SIZE,SIZE),Image.Resampling.LANCZOS).save(out/f"{surface}-basecolor.png")


if __name__ == "__main__":
    for stage, colors in SWATCHES.items():
        for surface in BOUNDS:
            draw_map(stage,surface,colors)
