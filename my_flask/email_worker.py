

import pika
import json
import os
from mailjet_rest import Client
from dotenv import load_dotenv
load_dotenv('/app/.env_secrets') 


# Initialize Mailjet client
mailjet = Client(auth=(os.getenv('MAILJET_API_KEY'), os.getenv('MAILJET_API_SECRET')), version='v3.1')

def send_email(email, template_id, variables,subject=None):
    """Send an email using the specified Mailjet template."""
    data = {
        'Messages': [
            {
                'From': {
                    'Email': os.getenv('MAILJET_SENDER_EMAIL'),
                    'Name': os.getenv('COMPANY_NAME'),
                },
                'To': [{'Email': email}],
                'Subject': subject,
                'TemplateID': template_id,
                'TemplateLanguage': True,
                'Variables': variables
            }
        ]
    }

    result = mailjet.send.create(data=data)
    print(result.json())
    if result.status_code != 200:
        print(f"Failed to send email: {result.json()}")
    else:
        print("Email sent successfully!")

def callback(ch, method, properties, body):
    """Process messages from RabbitMQ."""
    print("Received message:", body)
    data = json.loads(body)
    send_email(data['email'], data['template_id'], data['variables'])
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message

def start_worker():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()

        # Declare the queue
        channel.queue_declare(queue='email_queue', durable=True)

        # Subscribe to the queue
        channel.basic_consume(queue='email_queue', on_message_callback=callback, auto_ack=False)

        print("Waiting for messages in 'email_queue'. To exit, press CTRL+C")
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print("Error: Could not connect to RabbitMQ. Make sure the server is running.")
        print("Exception:", e)

if __name__ == "__main__":
    start_worker()

