import os
import random
import re
import json
import openai
import tiktoken
from typing import List, Dict
from dotenv import load_dotenv


class PieceWiseGPT:
    """
    PieceWiseGPT slices a given content string into logical pieces to fit within
    a GPT context window.

    Attributes:
    - content (str): The input content string.
    - window_size (int): The desired context window size.
    - llm_model (str): The OpenAI LLM model version.
    - llm_encoding (?): An object for encoding a specific llm_model
    - token_encoding_rate (float): The ratio of tokens to source characters
    - prompt (str): A GPT prompt for finding logical semantic boundaries
    - chunks (List[str]): The resultant chunks after processing.
    """

    CONTEXT_WINDOW_SIZE_DEFAULT = 8192
    CONTEXT_DIVISOR = 8 # any number greater or equal to 2 (splits the input context window size)
    TOKEN_PADDING = 128 # less tokens to "pad" for input; prevents
    LLM_MODEL_VERSION_MIN = "gpt-4"
    TOKEN_ENCODING_RATE_DEFAULT = 4.0 / 3.0  # English w/ Latin characters avg

    def __init__(self, content: str):
        """
        Initializes a new instance of the PieceWiseGPT class.

        Args:
        - content (str): The input content string to process.

        Raises:
        - ValueError: If the content is empty after preprocessing or if there are issues with the API/environment variables.
        """
        self.content: str = content
        self.window_size: int = self.CONTEXT_WINDOW_SIZE_DEFAULT
        self.llm_model: str = self.LLM_MODEL_VERSION_MIN
        self.llm_model_details: Dict[str, Any] = {}
        self.llm_encoding: None
        self.token_encoding_rate: float = self.TOKEN_ENCODING_RATE_DEFAULT
        self.attempts = 0 # total number of attempts required to slice the content
        self.chunks: List[str] = []

        self._preprocess()
        self._validate_api()
        self._token_encoding_rate()
        self._load_prompt()
        self._slice()

    def _preprocess(self):
        """
        Processes the content by removing leading and trailing whitespace.

        Raises:
        - ValueError: If the content is empty after preprocessing.
        """
        self.content = self.content.strip()

        if not self.content:
            raise ValueError(
                "Content is empty after preprocessing. No work to perform."
            )

    def _validate_api(self):
        """
        Validates the availability and correctness of OpenAI API and environment variables.

        Raises:
        - ValueError: If the API key or LLM model version is incorrect or missing, or if there's an issue connecting to OpenAI.
        """
        load_dotenv()

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError(
                "Required environment variable OPENAI_API_KEY is missing or empty."
            )

        if os.getenv("LLM_MODEL") and not os.getenv("LLM_MODEL", "").startswith(
            self.LLM_MODEL_VERSION_MIN
        ):
            raise ValueError(
                "LLM_MODEL requires 'gpt-4 as a minimum. Please check your environment."
            )

        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.llm_model = os.getenv("LLM_MODEL")

        # Fetch models and store information about the one we're using
        try:
            available_models = [model.id for model in openai.Model.list().data]
            if self.llm_model and self.llm_model not in available_models:
                raise ValueError(
                    f"The model {self.llm_model} is not available or you don't have access to it."
                )
        except openai.error.OpenAIError as e:
            raise ValueError(
                f"Failed to fetch the list of models from OpenAI: {str(e)}"
            )

        # Update context window size if 32k is detected
        if "gpt-4" in self.llm_model:
            self.window_size = 8192

        if "32k" in self.llm_model:
            self.window_size = 32768

        # Set the tiktoken encoder for the approved model
        # TODO: Properly handle error cases
        self.llm_encoding = tiktoken.encoding_for_model(self.llm_model)

    def _token_encoding_rate(self):
        # If content is <1000 characters then just sample the entire content
        if len(self.content) < 1000:
            sections = [self.content]
        else:
            # Else, divide the content into up to 4 random sections of up to 250 characters
            sections = []
            content_indices = list(range(len(self.content) - 250))
            random.shuffle(content_indices)
            for i in range(4):
                start_index = content_indices[i]
                sections.append(self.content[start_index : start_index + 250])

        total_chars = sum(len(section) for section in sections)
        total_tokens = sum(
            len(self.llm_encoding.encode(section)) for section in sections
        )

        # Get the ratio of total characters to the total number of tokens
        self.token_embedding_rate = total_chars / total_tokens

    def _load_prompt(self):
        # Best prompt so far
        with open(
            "./prompts/3_get_last_semantic_boundary.txt", "r", encoding="utf-8"
        ) as file:
            self.prompt = file.read()

    def _slice(self):
        available_input_tokens = (
            self.window_size // self.CONTEXT_DIVISOR
        )  # general use-case is much smaller slices for attention
        available_input_tokens -= len(self.llm_encoding.encode(self.prompt))
        available_input_tokens -= self.TOKEN_PADDING  # padding

        char_count = int(available_input_tokens * self.token_embedding_rate)

        content = self.content

        while content:
            self.attempts += 1

            # If the remaining content is less than what we need to slice
            # we can just append it to the end of the chunks list
            if len(content) <= char_count:
                self.chunks.append(content)
                break

            # Process the next chunk
            prechunk = {"prechunk": content[:char_count]}
            prechunk = json.dumps(prechunk)

            chunk = self._get_semantically_bound_chunk(prechunk)

            # Retry if GPT didn't return a predictable JSON chunk
            if not chunk:
                # this increments attempts
                continue

            # Avoid infinite loops due to unpredictably long whitespace
            if all(c.isspace() for c in chunk):
                break

            self.chunks.append(chunk)

            content = content[len(chunk) :]

    def _get_semantically_bound_chunk(self, txt):
        content = self.prompt + "\n\n[INPUT JSON CONTENT]\n\n" + txt
        max_tokens = self.window_size // 2

        completion = openai.ChatCompletion.create(
            model=self.llm_model,
            max_tokens=max_tokens,
            temperature=1,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            messages=[
                {
                    "role": "system",
                    "content": "The following is a conversation with an AI assistant labeled 'AI' with a user labeled 'Human'. The assistant is helpful, creative, clever, and very friendly. The assistant takes a deep breath and answers questions step by step.",
                },
                {"role": "user", "content": "Human: Hello, who are you?"},
                {
                    "role": "assistant",
                    "content": "AI: I am an AI created by OpenAI. How can I help you today?",
                },
                {"role": "user", "content": f"Human: {content}"},
            ],
        )

        response = completion.choices[0].message.content
        response = self.extract_embedded_json(response)

        return response

    def extract_embedded_json(self, text):
        pattern = r"(\{[^}]+\})"  # A simple pattern to match basic JSON objects
        matches = re.findall(pattern, text)

        valid_jsons = []
        for match in matches:
            try:
                # Try to parse the matched string into a JSON object
                parsed_json = json.loads(match)

                # Check if the "chunk" property exists and is non-empty
                if parsed_json.get("chunk"):
                    valid_jsons.append(parsed_json.get("chunk"))

            except json.JSONDecodeError:
                # If decoding fails, move on to the next iteration
                continue

        # Return the last valid JSON found, or an empty string if none found
        return valid_jsons[-1] if valid_jsons else ""

    def get(self) -> List[str]:
        """
        Fetches the chunks processed by the PieceWiseGPT class.

        Returns:
        - List[str]: List of chunks.
        """
        return self.chunks
