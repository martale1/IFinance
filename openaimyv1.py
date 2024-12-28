import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

class myOpenAIv1:

    def __init__(self,model="gpt-3.5-turbo"):
        _ = load_dotenv(find_dotenv()) # read local .env file
        self.api_key = os.environ['OPENAI_API_KEY']
        self.model=model

    def get_completion(self,prompt, ):
        print(prompt)
        messages = [{"role": "user", "content": prompt}]
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
        model=self.model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
        )
        return response.choices[0].message.content

    def get_completion_from_messages(self,system_content, user_content,temperature=0,max_tokens=5000):
        self.create_message(system_content,user_content)
        client = OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content,response.usage

    def create_message(self, system_content, user_content):
        self.messages = [
            {'role': 'system', 'content': system_content},
            {'role': 'user', 'content': user_content},
        ]

