import requests
from app.logger import logger
from app.config import cfg

class LLMClient:
    """LLM 统一调用客户端"""

    @staticmethod
    def deepseek_query(query_data, temperature=0, max_tokens=None):
        """
        DeepSeek 模型调用

        Args:
            query_data: 查询文本
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: 模型响应内容
        """
        config = cfg.LlmConfig['deepseek']
        url = config['url']

        if not url:
            raise ValueError("DeepSeek URL 未配置")

        input_data = {
            "model": config['model'],
            "max_tokens": max_tokens or config['max_tokens'],
            "temperature": temperature,
            "messages": [
                {"role": "user", "content": query_data}
            ]
        }

        try:
            res = requests.post(
                url,
                json=input_data,
                proxies={"http": "", "https": ""},
                timeout=config['timeout']
            )
            res.raise_for_status()
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error("DeepSeek 调用失败: {}".format(e))
            raise

    @staticmethod
    def qianwen_query(query_data, temperature=0.7, max_tokens=None):
        """
        通义千问模型调用

        Args:
            query_data: 查询文本
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            str: 模型响应内容
        """
        config = cfg.LlmConfig['qianwen']
        url = config['url']

        if not url:
            raise ValueError("Qianwen URL 未配置")

        input_data = {
            "model": config['model'],
            "max_tokens": max_tokens or config['max_tokens'],
            "stream": False,
            "temperature": temperature,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query_data}
            ]
        }

        try:
            res = requests.post(
                url,
                json=input_data,
                proxies={"http": "", "https": ""},
                timeout=config['timeout']
            )
            res.raise_for_status()
            return res.json()['choices'][0]['message']['content']
        except Exception as e:
            logger.error("Qianwen 调用失败: {}".format(e))
            raise

# 便捷函数
def deepseek_query(query_data, temperature=0, max_tokens=None):
    return LLMClient.deepseek_query(query_data, temperature, max_tokens)

def qianwen_query(query_data, temperature=0.7, max_tokens=None):
    return LLMClient.qianwen_query(query_data, temperature, max_tokens)
