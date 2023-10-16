import unittest
import os
from unittest import mock
import openai
from piecewisegpt import PieceWiseGPT


class TestPieceWiseGPT(unittest.TestCase):
    def setUp(self):
        # This method will run before every test
        self.content = "  This is a sample content.  "

    def test_preprocess(self):
        """Test preprocessing of content"""
        pwg = PieceWiseGPT(self.content)
        self.assertEqual(pwg.content, "This is a sample content.")

    def test_empty_content_exception(self):
        """Test ValueError exception on empty content after preprocessing"""
        with self.assertRaises(ValueError):
            PieceWiseGPT("   ")

    @mock.patch("os.getenv")
    def test_missing_api_key(self, mock_getenv):
        """Test ValueError exception for missing OPENAI_API_KEY"""
        mock_getenv.side_effect = lambda x: None if x == "OPENAI_API_KEY" else "gpt-4.0"
        with self.assertRaises(ValueError):
            PieceWiseGPT(self.content)

    @mock.patch("os.getenv")
    def test_invalid_llm_model(self, mock_getenv):
        mock_getenv.side_effect = (
            lambda k, default=None: "gpt-3" if k == "LLM_MODEL" else None
        )
        with self.assertRaises(ValueError):
            PieceWiseGPT(self.content)

    def test_language_samples(self):
        with open(
            os.path.join(os.path.dirname(__file__), "data", "sample_english.txt"),
            "r",
            encoding="utf-8",
        ) as f:
            self.content = f.read()

        # Instantiate PieceWiseGPT class (English)
        pwg = PieceWiseGPT(self.content)  # or whatever parameters you require
        print(pwg.get())

        with open(
            os.path.join(os.path.dirname(__file__), "data", "sample_german.txt"),
            "r",
            encoding="utf-8",
        ) as f:
            self.content = f.read()

        # Instantiate PieceWiseGPT class (German)
        pwg = PieceWiseGPT(self.content)
        print(pwg.get())

        with open(
            os.path.join(os.path.dirname(__file__), "data", "sample_japanese.txt"),
            "r",
            encoding="utf-8",
        ) as f:
            self.content = f.read()

        # Instantiate PieceWiseGPT class (Japanese)
        pwg = PieceWiseGPT(self.content)
        print(pwg.get())

        # ... (additional tests can be added as needed)


if __name__ == "__main__":
    unittest.main()
