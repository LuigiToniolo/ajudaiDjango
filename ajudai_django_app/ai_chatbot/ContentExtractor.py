import openai

from abc import ABC
from constants import GPT3_MODEL_NAME
from get_secret_variables import get_secret_var

class ContentExtractor():
    """
        An abstract class for content extraction using OpenAI API.

        Attributes
        ----------
            openai_api_key : str
                The API key for OpenAI API.

        Methods
        -------
            get_extraction(instructions, user_message)
                A method to get the extraction result using OpenAI API.
    """
    def __init__(self):
        self.openai_api_key = get_secret_var("OPENAI_API_KEY")
        openai.api_key = self.openai_api_key

    def extract(self, instructions, user_message):
        """
            An abstract method to get the extraction result using OpenAI API.

        Parameters
        ----------
            instructions : str
                The instructions for the OpenAI model.
            user_message : str
                The user message to be sent to the OpenAI model.

        Returns
        -------
            str
                The extracted content from the user message.
        """
        completions = openai.ChatCompletion.create(
            model=GPT3_MODEL_NAME,
            messages=[
                {"role": "system", "content": instructions},
                {
                    "role": "user", 
                    "content": user_message
                },
            ]
        )
        return completions['choices'][0]['message']['content']