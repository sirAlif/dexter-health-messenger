from fastapi import APIRouter, HTTPException, Depends
from services.openai import OpenAIService
from db.models import AIRequest
from api.dependencies import get_openai_service, get_current_user_id

router = APIRouter()


@router.post("/chat/{user_id}")
async def chat_with_ai(
        user_id: int,
        request: AIRequest,
        openai_service: OpenAIService = Depends(get_openai_service),
        current_user_id: int = Depends(get_current_user_id)
):
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if len(request.prompt) == 0:
            raise HTTPException(status_code=400, detail="Invalid prompt!")
        ai_response = await openai_service.send_prompt_to_gpt(request.prompt)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
