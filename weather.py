import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather", log_level="ERROR")


# mcp server demo
class Weather:
    def __init__(self, temperature: float, location: str) -> None:
        self.temperature = temperature
        self.location = location

    def to_dict(self) -> dict:
        """将 Weather 对象转换为字典"""
        return {
            "temperature": self.temperature,
            "location": self.location
        }


@mcp.tool()
async def get_weather(location: str) -> str:
    """
    获取指定地点的天气信息

    Args:
        location: 地点名称

    Returns:
        包含天气信息的 JSON 字符串
    """
    # 这里可以替换为真实的天气 API 调用
    # 示例：使用 httpx 调用天气 API
    try:
        # 这里只是一个示例，实际使用时需要替换为真实的天气 API
        # async with httpx.AsyncClient() as client:
        #     response = await client.get(
        #         f"https://api.weather.com/v1/location/{location}",
        #         params={"api_key": "YOUR_API_KEY"}
        #     )
        #     data = response.json()
        #     temperature = data["current"]["temperature"]

        # 暂时使用固定温度
        temperature = 26.5
        w = Weather(temperature, location)
        rst = json.dumps(w.to_dict(), indent=2, ensure_ascii=False)
        return rst

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "location": location
        }, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    mcp.run(transport='stdio')