"""OpenAI-compatible API request/response models."""

from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message in OpenAI format."""
    
    role: Literal["system", "user", "assistant"]
    content: str
    name: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    """OpenAI Chat Completion Request."""
    
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: Optional[int] = Field(default=None, ge=1)
    stream: Optional[bool] = False
    n: Optional[int] = Field(default=1, ge=1, le=1)  # Only support n=1 for now
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    user: Optional[str] = None


class Usage(BaseModel):
    """Token usage information."""
    
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatMessage(BaseModel):
    """Chat message response."""
    
    role: str
    content: str


class ChatChoice(BaseModel):
    """Chat completion choice."""
    
    index: int
    message: ChatMessage
    finish_reason: Optional[str] = None


class ChatCompletionResponse(BaseModel):
    """OpenAI Chat Completion Response."""
    
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatChoice]
    usage: Usage


class ChatChoiceDelta(BaseModel):
    """Streaming delta choice."""
    
    index: int
    delta: Dict[str, str]
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    """Streaming chat completion chunk."""
    
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: List[ChatChoiceDelta]


class ModelObject(BaseModel):
    """Model information."""
    
    id: str
    object: str = "model"
    created: int
    owned_by: str


class ModelList(BaseModel):
    """List of models."""
    
    object: str = "list"
    data: List[ModelObject]

