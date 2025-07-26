import json
import os
import boto3
from src.services.vision_service import OpenAIVisionService

def get_ssm_parameter(parameter_name: str, region: str = 'us-east-1') -> str:
    """Get parameter from AWS SSM Parameter Store."""
    ssm = boto3.client('ssm', region_name=region)
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except Exception as e:
        raise Exception(f"Failed to get SSM parameter {parameter_name}: {str(e)}")

async def process_update(update_data: dict, telegram_token: str, openai_api_key: str) -> dict:
    """Process a Telegram update."""
    try:
        # Initialize services
        vision_service = OpenAIVisionService(openai_api_key)
        
        # Extract message data
        message = update_data.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        
        if not chat_id:
            return {"statusCode": 200, "body": "No chat ID found"}
        
        # Handle /start command
        if message.get('text') == '/start':
            # Send welcome message via Telegram API
            import requests
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": "Hello! I'm an Image Description Bot. Send me an image and I'll describe it for you!"
            }
            requests.post(url, json=payload)
            return {"statusCode": 200, "body": "Start message sent"}
        
        # Handle photo messages
        if 'photo' in message:
            # Get the highest resolution photo
            photo = message['photo'][-1]
            file_id = photo['file_id']
            
            # Get file from Telegram
            import requests
            file_url_response = requests.get(f"https://api.telegram.org/bot{telegram_token}/getFile?file_id={file_id}")
            file_data = file_url_response.json()
            
            if file_data.get('ok'):
                file_path = file_data['result']['file_path']
                image_url = f"https://api.telegram.org/file/bot{telegram_token}/{file_path}"
                
                # Get description from vision service
                description = await vision_service.describe_image(image_url)
                
                # Send description back
                url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": description
                }
                requests.post(url, json=payload)
                
                return {"statusCode": 200, "body": "Description sent"}
            else:
                return {"statusCode": 400, "body": "Failed to get file from Telegram"}
        
        return {"statusCode": 200, "body": "Update processed"}
        
    except Exception as e:
        return {"statusCode": 500, "body": f"Error processing update: {str(e)}"}

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        # Get API keys from SSM
        telegram_token = get_ssm_parameter("/telegram-bot/prod/telegram-token")
        openai_api_key = get_ssm_parameter("/telegram-bot/prod/openai-api-key")
        
        # Parse the webhook data
        if 'body' in event:
            update_data = json.loads(event['body'])
        else:
            update_data = event
        
        # Process the update
        import asyncio
        result = asyncio.run(process_update(update_data, telegram_token, openai_api_key))
        
        return result
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Lambda error: {str(e)}")
        } 