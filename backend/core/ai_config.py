"""
AI Service Configuration
"""

class AIConfig:
    # 超时设置 (秒)
    OPENAI_TIMEOUT = 120
    GEMINI_TIMEOUT = 120
    
    # 重试设置
    MAX_RETRIES = 3
    RETRY_DELAY = 2  # 秒
    
    # 请求限制
    MAX_TOKENS = 1000
    TEMPERATURE = 0.7
    
    # 错误处理
    QUOTA_KEYWORDS = ['quota', 'billing', 'limit', 'exceeded']
    AUTH_KEYWORDS = ['authentication', 'api_key', 'permission', 'unauthorized']
    NETWORK_KEYWORDS = ['timeout', 'connection', 'network', 'unreachable']
    
    @classmethod
    def is_quota_error(cls, error_message: str) -> bool:
        """检查是否是配额错误"""
        return any(keyword in error_message.lower() for keyword in cls.QUOTA_KEYWORDS)
    
    @classmethod
    def is_auth_error(cls, error_message: str) -> bool:
        """检查是否是认证错误"""
        return any(keyword in error_message.lower() for keyword in cls.AUTH_KEYWORDS)
    
    @classmethod
    def is_network_error(cls, error_message: str) -> bool:
        """检查是否是网络错误"""
        return any(keyword in error_message.lower() for keyword in cls.NETWORK_KEYWORDS)
    
    @classmethod
    def should_retry(cls, error_message: str) -> bool:
        """判断是否应该重试"""
        # 配额和认证错误不重试
        if cls.is_quota_error(error_message) or cls.is_auth_error(error_message):
            return False
        # 网络错误可以重试
        return True
