"""
LLM函数调用工具定义。
"""
from .types import ToolDefinition


def get_tool_definitions() -> list[ToolDefinition]:
    """获取LLM函数调用的工具定义列表。"""
    return [
        {
            "type": "function",
            "function": {
                "name": "play_video",
                "description": "播放指定的视频文件",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "要播放的视频文件名filename"},
                        "device": {"type": "string", "description": "要在其上播放视频的屏幕名称"}
                    },
                    "required": ["target", "device"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "control_door",
                "description": "控制门的开关",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {"type": "string", "description": "门的全称"},
                        "action": {"type": "string", "enum": ["open", "close"], "description": "要执行的操作：open（打开）或close（关闭）"}
                    },
                    "required": ["target", "action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "seek_video",
                "description": "跳转到视频的指定时间点",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string", "description": "要跳转进度的屏幕名称"},
                        "value": {"type": "integer", "description": "跳转到的秒数"}
                    },
                    "required": ["device", "value"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "set_volume",
                "description": "设置音量到指定的绝对值",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string", "description": "要设置音量的屏幕名称"},
                        "value": {"type": "integer", "minimum": 0, "maximum": 100, "description": "音量值（0-100）"}
                    },
                    "required": ["device", "value"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "adjust_volume",
                "description": "相对提高或降低音量",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "device": {"type": "string", "description": "要调整音量的屏幕名称"},
                        "value": {"type": "string", "enum": ["up", "down"], "description": "音量调整方向：up（提高）或down（降低）"}
                    },
                    "required": ["device", "value"]
                }
            }
        }
    ]