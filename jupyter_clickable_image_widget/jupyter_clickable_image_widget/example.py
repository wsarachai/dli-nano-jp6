import anywidget
import traitlets


class ClickableImageWidget(anywidget.AnyWidget):
    """
    Live image widget that forwards click coordinates to Python.

    JupyterLab 4 compatible — built on anywidget (no npm/webpack required).

    API-compatible with the original jupyter_clickable_image_widget:
      - Set `value` to JPEG bytes (use traitlets.dlink + bgr8_to_jpeg)
      - Register a click handler via on_msg(callback)
      - Callback receives: content = {
            'event': 'click',
            'eventData': {'offsetX': <px>, 'offsetY': <px>}
        }
    """

    _esm = """
function render({ model, el }) {
    const img = document.createElement("img");
    img.style.cssText = "cursor:crosshair;display:block;";

    function update() {
        const buf = model.get("value");
        if (!buf || buf.byteLength === 0) return;
        const blob = new Blob([buf], { type: "image/jpeg" });
        const prev = img.src;
        img.src = URL.createObjectURL(blob);
        img.onload = () => { if (prev) URL.revokeObjectURL(prev); };
    }

    function resize() {
        img.width  = model.get("width");
        img.height = model.get("height");
    }

    model.on("change:value",  update);
    model.on("change:width",  resize);
    model.on("change:height", resize);

    img.addEventListener("click", (e) => {
        const rect = img.getBoundingClientRect();
        const sx = (img.naturalWidth  || model.get("width"))  / rect.width;
        const sy = (img.naturalHeight || model.get("height")) / rect.height;
        model.send({
            event: "click",
            eventData: {
                offsetX: Math.round((e.clientX - rect.left) * sx),
                offsetY: Math.round((e.clientY - rect.top)  * sy),
            },
        });
    });

    resize();
    update();
    el.appendChild(img);

    return () => { if (img.src) URL.revokeObjectURL(img.src); };
}
export default { render };
"""

    value  = traitlets.Bytes(b"").tag(sync=True)
    width  = traitlets.Int(224).tag(sync=True)
    height = traitlets.Int(224).tag(sync=True)
