"""
사용자 정의 예외 클래스
"""


class ChatbotException(Exception):
    """챗봇 기본 예외"""
    pass


class RegionNotFoundError(ChatbotException):
    """지역을 찾을 수 없을 때 발생하는 예외"""
    pass


class VectorStoreError(ChatbotException):
    """벡터 스토어 관련 예외"""
    pass


class DocumentNotFoundError(ChatbotException):
    """문서를 찾을 수 없을 때 발생하는 예외"""
    pass


class APIError(ChatbotException):
    """API 호출 관련 예외"""
    pass
