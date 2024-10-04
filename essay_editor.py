from lib2to3.pgen2 import grammar
from openai import OpenAI
from pydantic import BaseModel
import re
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


class SentenceLengthError(Exception):
    pass


class GPTRefusalError(Exception):
    pass


class Step(BaseModel):
    revised_sentence: str | None
    explanation: str | None


class GrammarEditor(BaseModel):
    steps: list[Step]


class EssayEditor:
    def __init__(self, user_prompt: str):
        """
        Initializes the EssayEditor with a prompt and a client for processing the paragraphs.

        :param prompt: The system prompt to provide guidance for sentence grammar checks.
        :param client: The client for connecting to a language model API for grammar checking.
        """
        self.model = "gpt-4o-2024-08-06"
        self.base_prompt = """
            You are an assistant that checks and corrects grammar for an essay.
            For each sentence, review for issues such as subject-verb agreement, passive voice, clarity, coherence, and overall readability.
            If a sentence is correct, return None for both revised_sentence and explanation.
            If there are errors, correct the sentence and explain the changes.
            Ensure the entire essay is cohesive and grammatically sound.
            Make your explanations concise and clear.
        """
        self.user_prompt = user_prompt
        self.client = client

    def split_to_paragraphs(self, text: str, char_limit: int = 500) -> List[str]:
        """
        Splits the input text into paragraphs while adhering to a character limit for each paragraph.

        :param text: The full input text to be split into paragraphs.
        :param char_limit: The maximum number of characters per paragraph.
        :return: A list of paragraphs, with each paragraph having a length <= char_limit.
        """
        paragraphs = text.split("\n\n")
        chunks = []

        for paragraph in paragraphs:
            if len(paragraph) <= char_limit:
                chunks.append(paragraph)
            else:
                # Split by sentence-ending punctuation
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                chunk = ""
                for sentence in sentences:
                    if len(chunk) + len(sentence) + 1 > char_limit:
                        chunks.append(chunk.strip())
                        chunk = sentence
                    else:
                        chunk += " " + sentence
                if chunk:
                    chunks.append(chunk.strip())
        return chunks

    def process_paragraph(self, text: str) -> List[Dict[str, Optional[str]]]:
        """
        Processes a paragraph of text by checking and correcting grammar.

        :param text: A single paragraph of text.
        :return: A list of dictionaries containing the original sentence, revised sentence, and explanation.
        """
        final_propmt = f"{self.base_prompt}\n{self.user_prompt}"
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": final_propmt},
                {"role": "user", "content": text},
            ],
            temperature=0.8,
            response_format=GrammarEditor,
        )

        result = completion.choices[0].message

        if result.refusal:
            raise GPTRefusalError(result.refusal)

        grammar_editor = result.parsed

        sentence_pattern = r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s"
        sentences = re.split(sentence_pattern, text)

        if len(grammar_editor.steps) != len(sentences):
            raise SentenceLengthError(
                f"Expected [{len(grammar_editor.steps)}] sentences, but found [{len(sentences)}] in the input."
            )

        result = []
        for step, orig_sent in zip(grammar_editor.steps, sentences):
            result.append(
                {
                    "original_sentence": orig_sent,
                    "revised_sentence": step.revised_sentence,
                    "explanation": step.explanation,
                }
            )
        return result

    def process_with_retries(self, paragraph: str, max_retries: int = 3) -> Optional[List[Dict[str, Optional[str]]]]:
        """
        Processes a paragraph with retries in case of errors.

        :param paragraph: The paragraph to process.
        :param max_retries: The maximum number of retries allowed in case of failures.
        :return: A list of grammar correction results or None if retries fail.
        """
        for attempt in range(max_retries):
            try:
                return self.process_paragraph(paragraph)

            except GPTRefusalError as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed due to GPT refusal error: {e}")
            except SentenceLengthError as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed due to sentence length error: {e}")
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries} failed due to unexpected error: {e}")

        print(f"Max retry count reached for paragraph: {paragraph}")
        return None

    def process_text(self, text: str) -> List[Dict[str, Optional[str]]]:
        """
        Splits text into paragraphs, processes each paragraph for grammar checking, and returns the results.

        :param text: The full input text to be processed.
        :return: A list of grammar correction results.
        """
        paragraphs = self.split_to_paragraphs(text)
        print(f"Number of paragraphs: {len(paragraphs)}")

        output = []
        for idx, paragraph in enumerate(paragraphs):
            print(f"Processing paragraph {idx + 1}/{len(paragraphs)}...")
            paragraph_results = self.process_with_retries(paragraph)

            if paragraph_results is None:
                print(f"Failed to process paragraph {idx + 1} after retries.")
            else:
                output.extend(paragraph_results)
                print(f"[DONE] Paragraph {idx + 1}")

        print("Processing completed.")
        return output
