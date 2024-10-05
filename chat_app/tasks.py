# chat_app/tasks.py

from celery import shared_task

@shared_task
def generate_assessment(conversation_id):
    from .models import Conversation, Message, Assessment
    from openai import OpenAI
    # read from the .env file and set the variable OPENAI_API_KEY to the read value.
    import environ
    import os

    env = environ.Env(
        # set casting, default value
        DEBUG=(bool, True)
    )

    # Set the project base directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Take environment variables from .env file
    environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

    # True if not in os.environ because of casting above
    DEBUG = env('DEBUG')

    # Raises Django's ImproperlyConfigured
    # exception if KEY not in os.environ
    OPENAI_API_KEY = env('OPENAI_API_KEY')

    # create OpenAI client object
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    from django.conf import settings

    conversation = Conversation.objects.get(id=conversation_id)
    messages = Message.objects.filter(conversation=conversation).order_by('timestamp')

    # Prepare the conversation transcript
    transcript = ''
    for msg in messages:
        transcript += f"{msg.sender_name}: {msg.message}\n"


    # Call the OpenAI API to generate the assessment
    response = client.chat.completions.create(model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are an assistant that evaluates customer service conversations and provides feedback to the customer service agent."},
        {"role": "user", "content": f"Please assess the following conversation between a customer and a customer service agent:\n\n{transcript}\n\nProvide feedback on the agent's performance."},
    ])

    assessment_text = response.choices[0].message.content.strip()

    # Save the assessment
    Assessment.objects.create(
        conversation=conversation,
        assessment_text=assessment_text
    )
