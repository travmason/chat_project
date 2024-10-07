# chat_app/tasks.py

from celery import shared_task

@shared_task
def generate_assessment(conversation_id):
    from .models import Conversation, Message, Assessment
    import openai
    # read from the .env file and set the variable OPENAI_API_KEY to the read value.
    import environ
    import os

    conversation = Conversation.objects.get(id=conversation_id)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Prepare the conversation transcript
    transcript = ''
    for msg in messages:
        transcript += f"{msg.sender_name}: {msg.message}\n"

    # Read environment variables
    env = environ.Env(
        DEBUG=(bool, True)
    )
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))
    DEBUG = env('DEBUG')
    OPENAI_API_KEY = env('OPENAI_API_KEY')

    openai.api_key = OPENAI_API_KEY

    try:
        # Use ChatCompletion API to generate the assessment
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that evaluates customer service conversations and provides feedback to the customer service agent."},
                {"role": "user", "content": f"Please assess the following conversation between a customer and a customer service agent:\n\n{transcript}\n\nProvide detailed feedback on the agent's performance, including strengths and areas for improvement."},
            ],
            temperature=0.7,
            max_tokens=500,
        )

        assessment_text = response.choices[0].message.content.strip()

        # Save the assessment
        Assessment.objects.create(
            conversation=conversation,
            assessment_text=assessment_text
        )

    except openai.error.OpenAIError as e:
        # Handle API errors
        print(f"OpenAI API error in generate_assessment: {e}")
        # Optionally, you could retry the task or log the error for later review
