from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from services.chat import ChatService
from api.dependencies import get_chat_service, validate_websocket_token, get_current_user_id


router = APIRouter()

connected_users = {}


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, chat_service: ChatService = Depends(get_chat_service)):
    # Expect a token in the query string
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    # Validate the token and ensure the user_id matches the token payload
    authenticated_user_id = await validate_websocket_token(token)
    if authenticated_user_id != user_id:
        await websocket.close(code=4003)
        return

    await websocket.accept()
    connected_users[user_id] = websocket
    try:
        while True:
            try:
                data = await websocket.receive_json()
                data["sender_id"] = user_id

                # Validate required fields
                required_fields = ["sender_id", "contact", "content"]
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    await websocket.send_json({"error": f"Missing fields: {', '.join(missing_fields)}"})
                    continue

                # Validate receiver ID
                if not await chat_service.is_valid_user_id(data["contact"]):
                    await websocket.send_json({"error": "Contact does not exist."})
                    continue

                # Send the message
                await chat_service.send_message_to_user(data, connected_users)
            except Exception as e:
                await websocket.send_json({"error": f"Failed to process message: {str(e)}"})
    except WebSocketDisconnect:
        del connected_users[user_id]
    except Exception as e:
        del connected_users[user_id]
        print(f"Unexpected error: {e}")


@router.get("/history/{user_id}")
async def get_messages(
        user_id: int,
        contact: str,
        chat_service: ChatService = Depends(get_chat_service),
        current_user_id: int = Depends(get_current_user_id),
):
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if not await chat_service.is_valid_user_id(contact):
            raise HTTPException(status_code=404, detail="Contact does not exist.")
        messages = await chat_service.get_user_conversation(user_id, contact)
        return messages
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/contacts/{user_id}")
async def get_contacts(
        user_id: int,
        chat_service: ChatService = Depends(get_chat_service),
        current_user_id: int = Depends(get_current_user_id),
):
    try:
        if user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        contacts = await chat_service.get_user_contacts(user_id)
        return contacts
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
