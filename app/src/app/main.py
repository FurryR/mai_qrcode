from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import pyautogui
import time
import cv2
from pyzbar import pyzbar
import mss
from Xlib import X, display, xobject
import asyncio
import os
import numpy as np

disp = display.Display()
app = FastAPI()
token = os.environ["TOKEN"]


def parseTimestamp(qr: str) -> int:
    if not qr.startswith("SGWCMAID"):
        return 0
    try:
        timestamp = int(qr[8:20])
        return timestamp
    except ValueError:
        return 0


def parseQR(img: cv2.typing.MatLike) -> list[str]:
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(
        gray_img, 120, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    bboxes: list[tuple[int, int, int, int]] = []
    for contour in contours:
        area = cv2.contourArea(contour)
        xmin, ymin, width, height = cv2.boundingRect(contour)
        extent = width * height
        if extent > np.pi / 4 and area > 100:
            bboxes.append((xmin, ymin, width, height))

    qrs: list[str] = []
    for xmin, ymin, xmax, ymax in bboxes:
        roi = img[ymin : ymin + ymax, xmin : xmin + xmax]
        decoded_objects = pyzbar.decode(roi)
        for obj in decoded_objects:
            qrs.append(obj.data.decode("utf-8"))

    # sort qr by timestamp
    qrs.sort(key=parseTimestamp)

    return qrs


def get_window_title(win: xobject.drawable.Window) -> str | None:
    # Try modern UTF-8 title
    title = win.get_full_property(disp.intern_atom("_NET_WM_NAME"), X.AnyPropertyType)
    if title and title.value:
        try:
            return title.value.decode("utf-8")
        except:
            return title.value
    # Fallback to legacy WM_NAME
    title = win.get_full_property(disp.intern_atom("WM_NAME"), X.AnyPropertyType)
    if title and title.value:
        try:
            return title.value.decode("utf-8")
        except:
            return title.value
    return None


def get_window_with_title(titleName: str) -> xobject.drawable.Window | None:
    root = disp.screen().root
    for window in root.query_tree().children:
        title = get_window_title(window)
        if titleName == title:
            return window
    return None


def process_qr_sync() -> str | JSONResponse:
    window = get_window_with_title("舞萌丨中二")
    if not window:
        return JSONResponse(
            {"code": 500, "message": "Window not found", "data": None},
            status_code=500,
            headers=generate_cors(),
        )
    # base_coords = window.translate_coords(disp.screen().root, 0, 0)
    size = window.get_geometry()
    original_decoded: list[str] = []
    decoded: list[str] = []
    with mss.mss() as sct:
        shot = sct.grab((size.x, size.y, size.x + size.width, size.y + size.height))
        img = np.frombuffer(shot.rgb, dtype=np.uint8).reshape(
            (shot.height, shot.width, 3)
        )

        if img is None:
            return JSONResponse(
                {"code": 500, "message": "Internal Server Error", "data": None},
                status_code=500,
                headers=generate_cors(),
            )
        original_decoded = parseQR(img)

    pyautogui.moveTo(size.x + 500, size.y + 1200)
    pyautogui.click()

    current = time.time()
    while True:
        time.sleep(0.05)
        with mss.mss() as sct:
            shot = sct.grab((size.x, size.y, size.x + size.width, size.y + size.height))
            img = np.frombuffer(shot.rgb, dtype=np.uint8).reshape(
                (shot.height, shot.width, 3)
            )
            if img is None:
                return JSONResponse(
                    {
                        "code": 500,
                        "message": "Internal Server Error",
                        "data": None,
                    },
                    status_code=500,
                    headers=generate_cors(),
                )
        decoded = parseQR(img)
        if len(decoded) >= 1 and decoded[-1] != (
            original_decoded[-1] if len(original_decoded) >= 1 else ""
        ):
            return decoded[-1]
        elif time.time() - current > 10:
            return JSONResponse(
                {"code": 500, "message": "Timeout waiting for QR code", "data": None},
                status_code=500,
                headers=generate_cors(),
            )


global_task: asyncio.Task[str | JSONResponse] | None = None


def generate_cors() -> dict:
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
        "Access-Control-Allow-Credentials": "true",
    }


@app.get("/v1/request")
async def get_qrcode(request: Request):
    global global_task
    req_token = request.query_params.get("token")
    if req_token != token:
        return JSONResponse(
            {"code": 403, "message": "Forbidden", "data": None},
            status_code=403,
            headers=generate_cors(),
        )

    result: str | JSONResponse | None = None

    task = (
        (global_task := asyncio.create_task(asyncio.to_thread(process_qr_sync)))
        if not global_task or global_task.done()
        else global_task
    )
    result = await task

    if isinstance(result, str):
        return JSONResponse(
            {"code": 200, "message": "", "data": result},
            headers=generate_cors(),
        )
    else:
        return result
