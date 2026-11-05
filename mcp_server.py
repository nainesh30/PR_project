from mcp.server.fastmcp import FastMCP
import asyncio
import serial
import time
import os
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from PIL import ImageGrab
from ctypes import POINTER, cast
import pyautogui
SERIAL_PORT = "COM13"     # change to your ESP32 port
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

def send(cmd: str):
    ser.write(f"{cmd}\n".encode())
    print("📤 Sent:", cmd)
def _get_volume_interface():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(
        IAudioEndpointVolume._iid_,
        CLSCTX_ALL,
        None
    )
    return cast(interface, POINTER(IAudioEndpointVolume))


def _set_brightness(level: int):
    level = max(0, min(level, 100))
    os.system(
        'powershell "(Get-WmiObject -Namespace root/WMI '
        '-Class WmiMonitorBrightnessMethods)'
        f'.WmiSetBrightness(1,{level})"'
    )

# -------------------------------------------------
# 🔊 Volume Controls
# -------------------------------------------------


async def main():
    # 🔑 THIS IS THE MAGIC
    mcp = FastMCP(
        "HomeControl",
        stateless_http=True,
        json_response=True
    )

    @mcp.tool()
    def red_light_on() -> str:
        send("LIGHT_ON")
        return "Light nainesh turned ON"

    @mcp.tool()
    def red_light_off() -> str:
        send("LIGHT_OFF")
        return "Light turned OFF"

    @mcp.tool()
    def bulb_on() -> str:
        send("BULB_ON")
        return "Bulb turned ON"

    @mcp.tool()
    def bulb_off() -> str:
        send("BULB_OFF")
        return "Bulb turned OFF"
    @mcp.tool()
    def volume_up():
        vol = _get_volume_interface()
        current = vol.GetMasterVolumeLevelScalar()
        vol.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
        return "Volume increased"


    @mcp.tool()
    def volume_down():
        vol = _get_volume_interface()
        current = vol.GetMasterVolumeLevelScalar()
        vol.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
        return "Volume decreased"


    @mcp.tool()
    def mute():
        vol = _get_volume_interface()
        vol.SetMute(1, None)
        return "Volume muted"


    @mcp.tool()
    def unmute():
        vol = _get_volume_interface()
        vol.SetMute(0, None)
        return "Volume unmuted"

# -------------------------------------------------
# 💡 Screen Brightness
# -------------------------------------------------
    @mcp.tool()
    def screen_brightness_up():
        _set_brightness(80)
        return "Brightness increased"


    @mcp.tool()
    def screen_brightness_down():
        _set_brightness(30)
        return "Brightness decreased"

# -------------------------------------------------
# 🎵 Media Control
# -------------------------------------------------
    @mcp.tool()
    def play_media():
        pyautogui.press("playpause")
        return "Play media command sent"


    @mcp.tool()
    def pause_media():
        pyautogui.press("playpause")
        return "Pause media command sent"

# -------------------------------------------------
# 📸 Screenshot
# -------------------------------------------------
    @mcp.tool()
    def screenshot():
        screenshots_dir = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            "Screenshots"
        )
        os.makedirs(screenshots_dir, exist_ok=True)

        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = os.path.join(
            screenshots_dir,
            f"screenshot_{timestamp}.png"
        )

        image = ImageGrab.grab(all_screens=True)
        image.save(path)

        return f"Screenshot saved to {path}"
    print("MCP Tool Server running on http://localhost:8000")
    await mcp.run_streamable_http_async()

if __name__ == "__main__":
    asyncio.run(main())
