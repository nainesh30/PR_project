# server.py
from mcp.server.fastmcp import FastMCP
import asyncio
import serial
import time

SERIAL_PORT = "COM11"     # change to your ESP32 port
BAUD_RATE = 115200

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)

def send(cmd: str):
    ser.write(f"{cmd}\n".encode())
    print("📤 Sent:", cmd)

async def main():
    # Stateless server (no session persistence, no sse stream with supported client)
    mcp = FastMCP("MCPServer", stateless_http=True, json_response=True)

 

 
    @mcp.tool()
    def move_robot(direction: str, duration: float) -> str:
        match direction.strip().lower():
            case "forward":
                direction = MoveDirection.MOVE_FORWARD
            case "backward" | "back":
                direction = MoveDirection.MOVE_BACKWARD
            case "left":
                direction = MoveDirection.MOVE_LEFT
            case "right":
                direction = MoveDirection.MOVE_RIGHT
            case _:
                raise ValueError("Invalid direction")

        print(f"Moving robot {direction} for {duration} seconds")
        request = MoveRequest(direction=direction, duration=duration)
        robot_stub.Move(request)
        return "Success"

    @mcp.tool()
    def get_battery_level() -> str:
        request = AdcDataRequest(channel=0)
        response = sensor_stub.GetAdc(request)
        return f"Battery level is {response.sample} Volts"

    print("Starting MCP server...")
    await mcp.run_streamable_http_async()


if __name__ == "__main__":
    asyncio.run(main())