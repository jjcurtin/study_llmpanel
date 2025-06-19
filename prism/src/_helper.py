from twilio.rest import Client

def send_sms(app, receiver_numbers, messages):
    account_sid = app.twilio_account_sid
    auth_token = app.twilio_auth_token
    from_number = app.twilio_from_number
    client = Client(account_sid, auth_token)

    for index, (to_number, message_body) in enumerate(zip(receiver_numbers, messages), start = 1):
        try:
            message = client.messages.create(body = message_body, from_ = from_number, to = to_number)
        except Exception as e:
            app.add_to_transcript(f"ERROR: Failed to send SMS {index} to {to_number}. Error message: {e}")