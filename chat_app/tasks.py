# chat_app/tasks.py

from celery import shared_task

@shared_task
def generate_assessment(conversation_id):
    from .models import Conversation, Message, Assessment
    import openai
    from django.conf import settings

    conversation = Conversation.objects.get(id=conversation_id)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Prepare the conversation transcript
    transcript = ''
    for msg in messages:
        transcript += f"{msg.sender_name}: {msg.message}\n"

    openai.api_key = settings.OPENAI_API_KEY

    # Call the OpenAI API to generate the assessment
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that evaluates customer service conversations and provides feedback to the customer service agent."},
            {"role": "user", "content": f"Please assess the following conversation between a customer and a customer service agent:\n\n{transcript}\n\nProvide feedback on the agent's performance."},
        ],
    )

    assessment_text = response['choices'][0]['message']['content'].strip()

    # Save the assessment
    Assessment.objects.create(
        conversation=conversation,
        assessment_text=assessment_text
    )
