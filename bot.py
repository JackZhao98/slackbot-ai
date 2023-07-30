SLACK_BOT_TOKEN = "xoxb-"
SLACK_APP_TOKEN = "xapp-"
OPENAI_API_KEY = "YOUR_TOKEN"
OPENAI_API_ORG = "YOUR_ORG"

import os
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.webhook import WebhookClient
from slack_bolt import App
from airmart_data_collector import AirmartDataCollector
import json
from openai_chat import OpenAIChat
import asyncio

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(SLACK_BOT_TOKEN)
chatGpt = OpenAIChat(
    api_key=OPENAI_API_KEY,
    org=OPENAI_API_ORG,
    model="gpt-4",
)


# @app.command("/ai")
# def handle_some_command(ack, body, logger):
#     ack()
#     print(body)
#     # Get the text from the message the user sent to the bot
#     store_id = body["text"]
#     collector = AirmartDataCollector()
#     store_data = collector.get_store_data(store_id)
#     # send the response back to the user
#     client.chat_postMessage(
#         channel=body["channel_id"],
#         text=json.dumps(store_data, indent=4),
#     )


def update_message(channel, timestamp, text):
    client.chat_update(
        channel=channel,
        ts=timestamp,
        text=text,
    )


def send_message(channel, text):
    return client.chat_postMessage(
        channel=channel,
        text=text,
    )


def clear_user_chatgpt(uid):
    chatGpt.clear_message(uid)


def add_emoji(channel, timestamp, emoji):
    client.reactions_add(
        channel=channel,
        timestamp=timestamp,
        name=emoji,
    )


# Handle command events
@app.command("/clear")
def handle_clear_command(ack, body, logger, respond):
    ack()
    # print(body)
    uid = body["user_id"]
    clear_user_chatgpt(uid)
    # Respond to the user only visible to them
    respond(text=f"Cleared chatGPT history for <@{uid}>")


@app.command("/ai")
def handle_some_command(ack, body, respond):
    ack()
    uid = body["user_id"]  # String member ID of the user who sent the message
    user_message = body["text"]  # String message the user sent
    print(f"User {uid} said {user_message}")
    message = send_message(uid, "Thinking...")
    channel = message["channel"]
    message_ts = message["ts"]

    def edit_message(text):
        client.chat_update(channel=channel, ts=message_ts, text=text)

    reply = chatGpt.chat_v2(
        user_prompt=user_message, uid=uid, update_message=edit_message
    )
    emoji = chatGpt.chat(
        f"Reply a emoji name (must be default in Slack) in snake case no colons that could best represent your feeling on your previous message:{reply}"
    )
    print(emoji)
    try:
        add_emoji(channel, message_ts, emoji)
    except:
        print("Emoji not found: " + emoji)
        add_emoji(channel, message_ts, "white_check_mark")


@app.event("message")
def handle_message(event, client, say):  # async function
    uid = event["user"]  # String member ID of the user who sent the message
    user_message = event["text"]  # String message the user sent
    print(f"User {uid} said {user_message}")
    channel = event["channel"]
    message = say("Thinking...")
    message_ts = message["ts"]

    def edit_message(text):
        client.chat_update(channel=channel, ts=message_ts, text=text)

    reply = chatGpt.chat_v2(
        user_prompt=user_message, uid=uid, update_message=edit_message
    )

    print("done")
    emoji = chatGpt.chat(
        f"Reply a emoji name (must be default in Slack) in snake case no colons that could best represent your feeling on your previous message:{reply}"
    )
    print(emoji)
    try:
        add_emoji(channel, message_ts, emoji)
    except:
        print("Emoji not found: " + emoji)
        add_emoji(channel, message_ts, "white_check_mark")


# This gets activated when the bot is tagged in a channel
@app.event("app_mention")
def handle_mentions(event, client, say):  # async function
    uid = event["user"]  # String member ID of the user who sent the message
    user_message = event["text"]  # String message the user sent
    print(f"User {uid} said {user_message}")
    channel = event["channel"]
    message = say("Thinking...")
    message_ts = message["ts"]

    def edit_message(text):
        client.chat_update(channel=channel, ts=message_ts, text=text)

    reply = chatGpt.chat_v2(
        user_prompt=user_message, uid=uid, update_message=edit_message
    )

    print("done")
    # ask chatgpt to respond to the user
    emoji = chatGpt.chat(
        f"Reply a emoji name (must be default in Slack) in snake case no colons that could best represent your feeling on your previous message:{reply}"
    )
    print(emoji)
    try:
        add_emoji(channel, message_ts, emoji)
    except:
        print("Emoji not found: " + emoji)
        add_emoji(channel, message_ts, "white_check_mark")


@app.command("/echo")
def repeat_text(ack, respond, command):
    # Acknowledge command request
    ack()
    respond(f"{command['text']}")


if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
