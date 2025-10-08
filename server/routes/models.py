"""Models list endpoint."""

import time

from fastapi import APIRouter, Header

# Import from wrapper
from server.zai_client_wrapper import ZAIClient

from server.models.openai import ModelList, ModelObject
from server.config import config


router = APIRouter()


@router.get("/v1/models", response_model=ModelList)
async def list_models(authorization: str = Header(None)):
    """
    List available models (OpenAI-compatible endpoint).
    
    Args:
        authorization: Authorization header
        
    Returns:
        List of available models
    """
    # Create Z.AI client
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
    
    client = ZAIClient(
        token=token,
        base_url=config.ZAI_BASE_URL,
        timeout=config.ZAI_TIMEOUT,
        auto_auth=token is None
    )
    
    # Get Z.AI models
    zai_models = client.get_models()
    
    # Convert to OpenAI format
    model_objects = []
    for model in zai_models:
        model_objects.append(
            ModelObject(
                id=model.id,
                object="model",
                created=int(time.time()),
                owned_by="zai"
            )
        )
    
    # Add mapped model names
    for openai_name in config.MODEL_MAPPINGS.keys():
        if openai_name not in [m.id for m in model_objects]:
            model_objects.append(
                ModelObject(
                    id=openai_name,
                    object="model",
                    created=int(time.time()),
                    owned_by="zai"
                )
            )
    
    return ModelList(
        object="list",
        data=model_objects
    )
