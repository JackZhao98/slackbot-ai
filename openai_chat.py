from time import sleep
import openai
import json

# import openai helper
# from utils.openai.openai_helper import create_chat_completion
from threading import Thread, Lock
import asyncio


class OpenAIChat:
    def __init__(self, api_key, org, model):
        self.api_key = api_key
        self.org = org
        self.model = model
        openai.api_key = api_key
        openai.organization = org
        self.messages = {}
        self.dispatch_message = False

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def process_message(self, message, uid):
        if uid not in self.messages.keys():
            self.messages[uid] = []
        # if length of existing messages is greater than 10, remove first 2
        if len(self.messages[uid]) >= 10:
            self.messages[uid] = self.messages[uid][2:]
        self.messages[uid].append(message)

    def clear_message(self, uid):
        if uid in self.messages.keys():
            self.messages[uid].clear()

    def clear_all(self):
        self.messages.clear()

    def chat_stream(self, prompts):
        for chunk in openai.ChatCompletion.create(
            model=self.model,
            messages=prompts,
            stream=True,
        ):
            content = chunk.choices[0].get("delta", {}).get("content")
            # self.process_message(response_msg.toDict(), uid)
            if content is not None and content != "":
                yield content

    def update_message(self, lock, r, reply):
        with lock:
            r["message"] += reply

    def update_message_worker(self, lock, r, prompts):
        self.dispatch_message = True
        for reply in self.chat_stream(prompts):
            self.update_message(lock, r, reply)
        self.dispatch_message = False
        print("done")

    def chat(self, user_prompt):
        request = {"role": "user", "content": user_prompt}

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an automated machine, responding only in minimal words.",
                },
                request,
            ],
        )
        response_msg = response.choices[0].get("message", {})
        return response_msg.get("content")

    def chat_v2(self, user_prompt, uid, update_message, is_stream=True):
        request = {"role": "user", "content": user_prompt}
        self.process_message(request, uid)
        r = {"message": ""}
        lock = Lock()
        try:
            t2 = Thread(
                target=self.update_message_worker, args=(lock, r, self.messages[uid])
            )
            t2.start()
            print()
            while self.dispatch_message == True and is_stream == True:
                if r["message"] != "":
                    update_message(r["message"])
                    print(".", end="")
                sleep(0.6)
            # Finally, update the message
            update_message(r["message"])
            t2.join()
            self.process_message({"role": "assistant", "content": r["message"]}, uid)
            return r["message"]
        except Exception as e:
            print(e)
            update_message(
                f"{r['message']}\nSomething went wrong. Please try again later."
            )
            return "Something went wrong. Please try again later."
