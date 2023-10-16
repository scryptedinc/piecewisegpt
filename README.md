# PieceWiseGPT - The Smarter Splitter Upper

`PieceWiseGPT` is a Python wrapper for OpenAI GPT models that allows users to slice longer content into manageable chunks by recognizing the "semantic boundaries" at the end of content. For instance, if a sentence is prematurely cut by the slicer, GPT will detect it and truncate the content to an earlier, logical starting point. This capability seems consistent across languages.

**Why would you want to do this?**

Looping over content in smaller, logical chunks with GPT is a great way to extract and manipulate data without losing details due to lack of attention/focus in larger context windows.

**Use Case Example:**

You're using GPT to loop over a chapter of a book, and want to classify entities, objects, events, relationships, colors, environments, and so on but you notice when you try to do too much at once that details get lost. By iterating over smaller portions, that have been divided cleanly so semantic meaning is preserved, you can.

> **Note**: Currently, the `gpt-3.5-turbo` model is not supported due to prompt compatibility reasons. It is advised to use `gpt-4` for best results.

## Installation

1. **Dependencies**: Ensure you have the necessary pip packages installed:
```bash
pip install -r requirements.txt
```

2. **Environment Setup**: Copy the `.env.example` file to `.env` and fill in your `OPENAI_API_KEY`:
```bash
cp .env.example .env
```
Then edit `.env` and provide your API key.

> **Note**: Alternatively, PieceWiseGPT will also search the environment for the required values if the .env file is not found, such as when using this as a module in another project.

## Tests

```bash
python -m unittest discover tests
```

## Usage

Using `PieceWiseGPT` is straightforward:

```python
from piecewisegpt import PieceWiseGPT

pwg = PieceWiseGPT("Your long content here...")
# wait... (sorry about the wait)
chunks = pwg.get()
print(chunks)
```

## How It Works

Here's a breakdown of the main functionalities:

- **Initialization**: The constructor (`__init__`) takes in a content string. Upon instantiation, the content undergoes preprocessing, API validation, calculation of the token encoding rate, loading of the necessary GPT prompt, and then slicing.

- **Preprocessing**: Trims leading and trailing whitespace from the content.

- **API Validation**: Checks for the availability and correctness of OpenAI API keys and the LLM model version. Also fetches the list of available models.

- **Token Encoding Rate Calculation**: Determines the token to character conversion rate. This can vary based on the language and content. Fun theory: ChatGPT referenced a theory that agglutinative languages have the worse encoding rates.

- **Prompt Loading**: Loads a GPT prompt that instructs the model on how to find logical semantic boundaries in the content. There are several attempts in the ./prompts/ folder to look over.

- **Slicing**: The main logic that slices the content based on the computed token encoding rate and the GPT prompt. The slicing window is approximately 4x smaller than the actual available window

- **Chunk Retrieval**: Finally, the `get` method allows the user to fetch the processed chunks as a list of strings.

## Project Organization

- `README.md`: This file.
- `__init__.py`: Package initializer.
- `openai_model_details.py`: Contains a method to get the maximum tokens for a given model.
- `piecewisegpt.py`: The main module containing the `PieceWiseGPT` class and its methods.
- `prompts/`: Directory containing various prompt files to instruct the GPT models.
- `tests/`: Contains unit tests for the `PieceWiseGPT` class.

## Test Data

- `sample_english.txt` an excerpt from Critique of Pure Reason by Immanuel Kant (English)
- `sample_german.txt` an excerpt from Critique of Pure Reason by Immanuel Kant (German)
- `sample_japanese.txt` an excerpt from Wikipedia from the article about 2channel (Japanese)

## Future (Hopeful) Improvements

- Making it work with gpt-3.5-turbo is THE DREAM
- Let the user specify a callback to execute whenever a chunk is processed, rather than wait for all chunks to finish
- Better offline semantic boundary detection (give the LLMs the best chance, right?) - easy in English, actually.
- Changes to the constructor: overriding the LLM model, changing window slicing sizes, etc
- Improved few-shot prompt methodology
- Improved ChatCompletion methodology
- Better sampling and chunk size prediction

## Contributions

Contributions to improve the project are always welcome. Please ensure your code adheres to PEP8 standards and is self-documenting. For any bugs or feature requests, feel free to open an issue.

## License

[MIT License](LICENSE)

## Authors

Tim Cotten <tim@scryptedinc.com>, Scrypted Inc., & ChatGPT with GPT-4 by OpenAI

## Contact

@cottenio

## AI Generated

ChatGPT with GPT-4 was used in the creation and documentation of this project. Humans apparently are just the wetware layer for the Singularity.

---

**Important**: Always remember to keep your `OPENAI_API_KEY` confidential and never expose it in public repositories or other insecure locations. The .env file is in .gitignore for a reason. Don't submit your .env file!
