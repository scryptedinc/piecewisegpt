# models_info.py

OPENAI_MODEL_DETAILS = {
    "gpt-4": 8192,
    "gpt-4-0613": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0314": 8192,
    "gpt-4-32k-0314": 32768,
    "gpt-3.5-turbo": 4097,
    "gpt-3.5-turbo-16k": 16385,
    "gpt-3.5-turbo-instruct": 4097,
    "gpt-3.5-turbo-0613": 4097,
    "gpt-3.5-turbo-16k-0613": 16385,
    "gpt-3.5-turbo-0301": 4097,
    "text-davinci-003": 4097,
    "text-davinci-002": 4097,
    "code-davinci-002": 8001,
    "babbage-002": 16384,
    "davinci-002": 16384,
    "text-curie-001": 2049,
    "text-babbage-001": 2049,
    "text-ada-001": 2049,
    "davinci": 2049,
    "curie": 2049,
    "babbage": 2049,
    "ada": 2049,
}


def get_max_tokens(model_name):
    if model_name in OPENAI_MODEL_DETAILS:
        return OPENAI_MODEL_DETAILS[model_name]
    else:
        raise ValueError(
            f"Model '{model_name}' not found in our records. Please check the model name and try again."
        )


if __name__ == "__main__":
    # Simple test
    model_name = "gpt-4"
    try:
        print(f"Max tokens for {model_name}: {get_max_tokens(model_name)}")
    except ValueError as e:
        print(e)
