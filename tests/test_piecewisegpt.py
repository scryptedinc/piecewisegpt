import unittest
import os
import time
from pprint import pprint
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
        # Calculate the anticipated time for the current content
        gpt4_seconds_per_char = 0.06223 # GPT-4 parsing constant

        # Load sample files
        sample_files = ["sample_english.txt", "sample_german.txt", "sample_japanese.txt"]
        total_chunks = 0
        total_attempts = 0
        total_bytes = sum(os.path.getsize(os.path.join(os.path.dirname(__file__), "data", filename)) for filename in sample_files)

        anticipated_time = total_bytes * gpt4_seconds_per_char
        print(f"Anticipated time based on given data: {anticipated_time:.2f} seconds")
        
        total_start_time = time.time()
        for sample in sample_files:
            print(f"Testing {sample.split('_')[1].capitalize()} sample...")

            with open(os.path.join(os.path.dirname(__file__), "data", sample), "r", encoding="utf-8") as f:
                self.content = f.read()

            start_time = time.time()
            pwg = PieceWiseGPT(self.content)
            chunks = pwg.get()
            num_chunks = len(chunks)
            total_chunks += num_chunks
            total_attempts += pwg.attempts
            execution_time = time.time() - start_time

            # Pretty print the chunks
            for chunk_id, chunk in enumerate(chunks):
                print(f"Chunk #{chunk_id}")
                print("----------------------")
                pprint(chunk)

            print(f"Semantic chunks: {num_chunks}")
            print(f"Required attempts: {pwg.attempts}")
            print(f"Execution time for {sample}: {execution_time:.2f} seconds")
            print("----------------------")

        total_execution_time = time.time() - total_start_time
        print(f"Total semantic chunks: {total_chunks}")
        print(f"Total required attempts: {total_attempts}")
        print(f"Total execution time: {total_execution_time:.2f} seconds")

    # ... (additional tests can be added as needed)


if __name__ == "__main__":
    unittest.main()
