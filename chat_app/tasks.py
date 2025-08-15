# chat_app/tasks.py

from celery import shared_task
import bleach
import os

GPT_CONVERSATION_MODEL = os.getenv('GPT_CONVERSATION_MODEL', 'gpt-5-nano')
GPT_ASSESSMENT_MODEL = os.getenv('GPT_ASSESSMENT_MODEL', 'gpt-5-mini')
DEBUG = os.getenv('DEBUG', 'True').lower() in ('1', 'true', 'yes', 'on')


@shared_task
def generate_assessment(conversation_id):
    from .models import Conversation, Message, Assessment
    import openai # type: ignore
    from openai import OpenAI # type: ignore

    conversation = Conversation.objects.get(id=conversation_id)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Prepare the conversation transcript
    transcript = ''
    for msg in messages:
        transcript += f"{msg.sender_name}: {msg.message}\n"

    print('transcript: ', transcript)

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if not OPENAI_API_KEY:
        raise ValueError("Missing OPENAI_API_KEY environment variable")

    client = OpenAI(api_key=OPENAI_API_KEY)

    try:
        # Use ChatCompletion API to generate the assessment
        response = client.chat.completions.create(
            model=GPT_ASSESSMENT_MODEL,
            messages=[
                {"role": "developer", "content": "You are an expert educator that evaluates customer service conversations and provides feedback to the customer service agent."},
                {"role": "user", "content": f"""Please assess the following conversation between a customer and a customer service agent:\n\n{transcript}\n\nProvide detailed feedback on the agent's performance, including strengths and areas for improvement. At the end of the assessment include a score between 0 and 100 and add /100 so they can see it is out of 100.
                Provide the assessment strictly in HTML format. Use only the specified tags.
                Your output must:
                - Use the tags: <ul>, <ol>, <li>, <strong>, <p>, <br />
                - Only include the inner part of the <body> tag
                - Not include any CSS attributes or explanations
                - Not include any JavaScript
                - Not include any HTML attributes
                - Not include any inline styles
                - Not include any <head> tag
                - Not include any <html> tag
                - Not include any <title> tag
                - Not include any <meta> tag
                - Not include any <link> tag
                - Not include any <style> tag
                - Not include any <script> tag
                - Not include any <img> tag
                """},
            ]
        )

        print('Response received from OpenAI API: ', response)

        assessment_text = bleach.clean(
            response.choices[0].message.content.strip(),
            tags=['ul','ol','li','strong','p','br'],
            attributes={},
            strip=True
        )

        # Save the assessment
        # Overwrite existing assessment if present; otherwise fall through to create
        if Assessment.objects.filter(conversation=conversation).update(assessment_text=assessment_text):
            return
        Assessment.objects.create(
            conversation=conversation,
            assessment_text=assessment_text
        )

    except openai.OpenAIError as e:
        # Handle API errors
        print(f"OpenAI API error in generate_assessment: {e}")
