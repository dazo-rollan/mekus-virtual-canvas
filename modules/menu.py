import cv2
import numpy as np
from drawing import (
    COLORS, CLEAR, ERASER, WHITE,
    SHAPES, FREE_DRAW, SHAPE_CIRCLE,
    SHAPE_RECTANGLE, SHAPE_LINE
)

# ----- Button Class -----
class CircleButton:
    def __init__(self, cx, cy, radius, color, text='', isPen=False):
        self.cx = cx
        self.cy = cy
        self.radius = radius
        self.color = color
        self.text = text
        self.isPen = isPen
        self.alpha = 0.5

    def draw(self, img, text_color=(255, 255, 255), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.6, thickness=1):
        overlay = img.copy()
        cv2.circle(overlay, (self.cx, self.cy), self.radius, self.color, -1)
        cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha, 0, img)

        if self.text in SHAPES and self.text == currentShape:
            offset = self.radius // 2
            cv2.line(img, (self.cx - offset, self.cy - offset), (self.cx + offset, self.cy + offset), (0, 0, 0), 2)
            cv2.line(img, (self.cx + offset, self.cy - offset), (self.cx - offset, self.cy + offset), (0, 0, 0), 2)

        if self.text:
            size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)[0]
            pos = (self.cx - size[0] // 2, self.cy + self.radius + size[1] + 10)
            cv2.putText(img, self.text, pos, fontFace, fontScale, text_color, thickness)

    def isOver(self, x, y):
        return (x - self.cx) ** 2 + (y - self.cy) ** 2 < self.radius ** 2

# ----- Toggles -----
def draw_toggle(cx, cy, r, isOn):
    cv2.circle(frame, (cx, cy), r, (255, 255, 255), -1)
    cv2.circle(frame, (cx, cy), r, (200, 200, 200), 2)
    if isOn:
        offset = 8
        cv2.line(frame, (cx - offset, cy - offset), (cx + offset, cy + offset), (0, 0, 255), 2)
        cv2.line(frame, (cx + offset, cy - offset), (cx - offset, cy + offset), (0, 0, 255), 2)

# ----- Setup -----
canvas = np.zeros((720, 1280, 4), np.uint8)
canvas[..., :3] = WHITE
canvas[..., 3] = 0

previewCanvas = np.zeros_like(canvas)

drawing = False
ix, iy = -1, -1
x, y = -1, -1
color = COLORS[0]
brushSize = 5
eraserSize = 30
usingEraser = False
currentShape = FREE_DRAW

# Toggles
hideBoard = True
hideColors = True
hidePenSizes = True

toggleR = 30
toggleX, toggleY = 80, 50

# Shifted X positions slightly to the right
penToggleX, penToggleY, penToggleR = 1170, 50, 30
clearBtnX = penToggleX - 80      # 1090
eraserBtnX = clearBtnX - 80      # 1010
colorToggleX = eraserBtnX - 80   # 930
eraserBtnY = colorToggleY = clearBtnY = penToggleY

eraserBtnR = colorToggleR = 30

# Buttons
colors = []
color_radius = 25
for i, c in enumerate(COLORS[:8]):
    cx = colorToggleX - 50 - i * (color_radius * 2 + 5)
    colors.append(CircleButton(cx, colorToggleY, color_radius, c))

clearBtn = CircleButton(clearBtnX, clearBtnY, 30, (100, 100, 100), CLEAR)

penSizes = []
for i, size in enumerate(range(5, 30, 5)):
    penSizes.append(CircleButton(penToggleX, penToggleY + 60 + i * 50, size, (80, 80, 80), isPen=True))

# Shape buttons beside board toggle
shapeButtons = []
shapeBarX = toggleX + toggleR + 60
shapeBarY = toggleY
for i, shape in enumerate(SHAPES[:4]):
    shapeButtons.append(CircleButton(shapeBarX + i * 80, shapeBarY, 25, (60, 60, 60), shape))

# Whiteboard area
def isInsideWhiteBoard(x, y):
    return 50 < x < 1070 and 120 < y < 700

# ----- Mouse Logic -----
def mouse_callback(event, x_, y_, flags, param):
    global drawing, ix, iy, color, brushSize, usingEraser
    global hideBoard, hideColors, hidePenSizes, currentShape, x, y

    x, y = x_, y_

    if event == cv2.EVENT_LBUTTONDOWN:
        ix, iy = x, y
        drawing = True

        if (x - toggleX)**2 + (y - toggleY)**2 < toggleR**2:
            hideBoard = not hideBoard
        if not hideBoard:
            if (x - penToggleX)**2 + (y - penToggleY)**2 < penToggleR**2:
                hidePenSizes = not hidePenSizes
            if (x - colorToggleX)**2 + (y - colorToggleY)**2 < colorToggleR**2:
                hideColors = not hideColors
            if (x - eraserBtnX)**2 + (y - eraserBtnY)**2 < eraserBtnR**2:
                usingEraser = not usingEraser
            if clearBtn.isOver(x, y):
                canvas[:] = 0
                canvas[..., :3] = WHITE
                canvas[..., 3] = 0

            for c in colors:
                if c.isOver(x, y):
                    color = c.color
                    usingEraser = False

            for p in penSizes:
                if p.isOver(x, y):
                    brushSize = p.radius

            for s in shapeButtons:
                if s.isOver(x, y):
                    currentShape = s.text

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing and not hideBoard and isInsideWhiteBoard(x, y):
            if usingEraser:
                mask = np.zeros_like(canvas[..., 0])
                cv2.circle(mask, (x, y), eraserSize, 255, -1)
                canvas[mask == 255] = [255, 255, 255, 0]
            elif currentShape == FREE_DRAW:
                b, g, r = color
                cv2.line(canvas, (ix, iy), (x, y), (b, g, r, 255), brushSize)
                ix, iy = x, y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if not hideBoard and not usingEraser and currentShape in [SHAPE_LINE, SHAPE_RECTANGLE, SHAPE_CIRCLE]:
            if isInsideWhiteBoard(x, y):
                if currentShape == SHAPE_LINE:
                    cv2.line(canvas, (ix, iy), (x, y), color + (255,), brushSize)
                elif currentShape == SHAPE_RECTANGLE:
                    cv2.rectangle(canvas, (ix, iy), (x, y), color + (255,), brushSize)
                elif currentShape == SHAPE_CIRCLE:
                    center_x = (ix + x) // 2
                    center_y = (iy + y) // 2
                    radius = int(((x - ix) ** 2 + (y - iy) ** 2) ** 0.5 / 2)
                    cv2.circle(canvas, (center_x, center_y), radius, color + (255,), brushSize)

# ----- Draw UI -----
def draw_ui():
    alpha = canvas[..., 3:] / 255.0
    frame[:] = (frame * (1 - alpha) + canvas[..., :3] * alpha).astype(np.uint8)

    previewAlpha = previewCanvas[..., 3:] / 255.0
    frame[:] = (frame * (1 - previewAlpha) + previewCanvas[..., :3] * previewAlpha).astype(np.uint8)

    draw_toggle(toggleX, toggleY, toggleR, not hideBoard)
    
    if not hideBoard:
        draw_toggle(penToggleX, penToggleY, penToggleR, not hidePenSizes)
        draw_toggle(colorToggleX, colorToggleY, colorToggleR, not hideColors)
        draw_toggle(eraserBtnX, eraserBtnY, eraserBtnR, usingEraser)

        cv2.putText(frame, "Colors", (colorToggleX - 30, colorToggleY + colorToggleR + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Thickness", (penToggleX - 40, penToggleY + penToggleR + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, "Eraser", (eraserBtnX - 30, eraserBtnY + eraserBtnR + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        clearBtn.draw(frame)

        if not hideColors:
            for c in colors:
                c.draw(frame)
                if c.color == color:
                    offset = c.radius // 2
                    cv2.line(frame, (c.cx - offset, c.cy - offset), (c.cx + offset, c.cy + offset), (0, 0, 0), 2)
                    cv2.line(frame, (c.cx + offset, c.cy - offset), (c.cx - offset, c.cy + offset), (0, 0, 0), 2)

        if not hidePenSizes:
            for p in penSizes:
                cv2.circle(frame, (p.cx, p.cy), p.radius + 4, (255, 255, 255), -1)
                cv2.circle(frame, (p.cx, p.cy), p.radius, p.color, -1)
                if p.radius == brushSize:
                    offset = int(p.radius * 0.7)
                    cv2.line(frame, (p.cx - offset, p.cy - offset), (p.cx + offset, p.cy + offset), (0, 0, 0), 2)
                    cv2.line(frame, (p.cx + offset, p.cy - offset), (p.cx - offset, p.cy + offset), (0, 0, 0), 2)

        for s in shapeButtons:
            s.alpha = 0.9 if s.text == currentShape else 0.4
            s.draw(frame)

    cv2.putText(frame, "Board", (toggleX - 30, toggleY + toggleR + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

# ----- Main Loop -----
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
cv2.namedWindow("video")
cv2.setMouseCallback("video", mouse_callback)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)

    previewCanvas[:] = 0
    if drawing and not hideBoard and not usingEraser and isInsideWhiteBoard(ix, iy):
        if currentShape in [SHAPE_LINE, SHAPE_RECTANGLE, SHAPE_CIRCLE]:
            if isInsideWhiteBoard(x, y):
                if currentShape == SHAPE_LINE:
                    cv2.line(previewCanvas, (ix, iy), (x, y), color + (255,), brushSize)
                elif currentShape == SHAPE_RECTANGLE:
                    cv2.rectangle(previewCanvas, (ix, iy), (x, y), color + (255,), brushSize)
                elif currentShape == SHAPE_CIRCLE:
                    center_x = (ix + x) // 2
                    center_y = (iy + y) // 2
                    radius = int(((x - ix) ** 2 + (y - iy) ** 2) ** 0.5 / 2)
                    cv2.circle(previewCanvas, (center_x, center_y), radius, color + (255,), brushSize)

    draw_ui()
    cv2.imshow("video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()