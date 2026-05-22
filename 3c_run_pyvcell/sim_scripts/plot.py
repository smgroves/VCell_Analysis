
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pyvcell.vcml as vc


def _fix_analytic_expr(expr: str) -> str:
    """Replace C-style logical operators with numexpr-compatible ones."""
    return expr.replace("&&", "&").replace("||", "|")


def plot_2d_geo(geo, title="Geometry", resolution=50):
    # Work on a deep copy so the original model is not modified
    geo_copy = geo.model_copy(deep=True)
    for sv in geo_copy.subvolumes:
        if sv.analytic_expr:
            sv.analytic_expr = _fix_analytic_expr(sv.analytic_expr)

    seg = geo_copy.to_segmented_image(resolution=resolution)
    label_slice = seg.labels[:, :, 0]

    unique = sorted(seg.label_names.keys())
    cmap = plt.colormaps["tab10"]
    colors = {label: cmap(i / max(len(unique) - 1, 1)) for i, label in enumerate(unique)}

    rgb = np.zeros((*label_slice.T.shape, 4))
    patches = []
    for label, name in seg.label_names.items():
        mask = label_slice.T == label
        rgb[mask] = colors[label]
        patches.append(mpatches.Patch(color=colors[label], label=name))

    fig, ax = plt.subplots()
    ax.imshow(rgb, origin="lower",
              extent=[geo.origin[0], geo.origin[0] + geo.extent[0],
                      geo.origin[1], geo.origin[1] + geo.extent[1]])
    ax.legend(handles=patches, loc="upper right")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(title)
    plt.show()