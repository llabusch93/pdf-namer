import os
import subprocess
import PyPDF2
import re
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI


class PDFInfo(BaseModel):
    """
    Pydantic model for storing PDF document information.
    """

    date: str = Field(..., description="The date of the document in YYYY-MM-DD format")
    document_kind: str = Field(
        ..., description="The kind of document (e.g., invoice, letter, brochure)"
    )
    document_name: str = Field(
        ..., max_length=100, description="A brief description of the document content"
    )


def process_pdf(file_path: str, language: str, force: bool = False) -> str:
    """
    Process a PDF file: apply OCR if needed, extract text, generate a new
    filename using AI, and rename the file.

    Args:
        file_path (str): Path to the PDF file to process.
        language (str): The language to use for document kind and name.
        force (bool): Force processing even if the filename is already correct.

    Returns:
        str: The new filename of the processed PDF.
    """
    current_filename = os.path.basename(file_path)
    if not force and is_filename_correct(current_filename):
        print(f"Filename '{current_filename}' is already in the correct format. Skipping processing.")
        return current_filename

    if not has_text(file_path):
        apply_ocr(file_path)

    text = extract_text(file_path)
    new_name = generate_filename(text, file_path, language)
    
    if new_name:
        rename_file(file_path, new_name)
        return new_name
    else:
        return current_filename


def is_filename_correct(filename: str) -> bool:
    """
    Check if the filename is already in the correct format.

    Args:
        filename (str): The filename to check.

    Returns:
        bool: True if the filename is in the correct format, False otherwise.
    """
    pattern = r'^\d{4}-\d{2}-\d{2} -- .+ - .+\.pdf$'
    return bool(re.match(pattern, filename))


def has_text(file_path: str) -> bool:
    """
    Check if a PDF file contains extractable text.

    Args:
        file_path (str): Path to the PDF file to check.

    Returns:
        bool: True if the PDF contains extractable text, False otherwise.
    """
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        return any(page.extract_text().strip() for page in reader.pages)


def apply_ocr(file_path: str) -> None:
    """
    Apply OCR to a PDF file using ocrmypdf.

    Args:
        file_path (str): Path to the PDF file to process with OCR.
    """
    output_file = f"{os.path.splitext(file_path)[0]}_ocr.pdf"
    subprocess.run(
        [
            "ocrmypdf",
            "--language",
            "deu+eng",
            "--deskew",
            "--clean",
            "--force-ocr",
            file_path,
            output_file,
        ],
        check=True,
    )
    os.replace(output_file, file_path)


def extract_text(file_path: str) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path (str): Path to the PDF file to extract text from.

    Returns:
        str: Extracted text from the PDF.
    """
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages)


def truncate_text(text: str, max_words: int = 1000) -> str:
    """
    Truncate the given text to a maximum number of words.

    Args:
        text (str): The text to truncate.
        max_words (int): The maximum number of words to keep. Defaults to 1000.

    Returns:
        str: The truncated text.
    """
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words])


def get_openai_api_key() -> str:
    """
    Get the OpenAI API key from the environment variable or ~/.openai file.

    Returns:
        str: The OpenAI API key.

    Raises:
        ValueError: If the API key is not found in either location.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return api_key

    openai_file_path = os.path.expanduser("~/.openai")
    if os.path.exists(openai_file_path):
        with open(openai_file_path, "r") as f:
            return f.read().strip()

    raise ValueError(
        "OpenAI API key not found in environment variable or ~/.openai file"
    )


def generate_filename(text: str, original_path: str, language: str) -> str:
    """
    Generate a new filename for the PDF using the OpenAI API.

    Args:
        text (str): Extracted text from the PDF.
        original_path (str): Original path of the PDF file.
        language (str): The language to use for document kind and name.

    Returns:
        str: Generated filename in the format
             "YYYY-MM-DD -- DOCUMENT_KIND - DOCUMENT_DESCRIPTION".
    """

    try:
        api_key = get_openai_api_key()
        client = OpenAI(api_key=api_key)

        truncated_text = truncate_text(text)
        messages = [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are a system designed to generate a filename
for a given PDF document content that the user provides.
The language of the document kind and name must be in
{language}. You will get the first
1000 words of the document, and you must extract the following
information that will be given as JSON object back:\n
{{"date": "<The date of the document in the format of YYYY-MM-DD. \
If no document date can be found, use 'NO_DATE'>",
\n"document_kind": "<The kind of the Document, e.g., Invoice, \
Letter, Contract etc.>",
\n"document_name": "<The naming for that document, e.g., 'Blood 
Test results from Dr. Schwarz' or 'Leasing of Škoda Superb' 
etc. Be VERY VERY specific for the description, e.g. name for
what products an invoice is, or what exactly a letter or
confirmation is about. The description must not exceed 80
characters.>"}}
""",
                    }
                ],
            },
            {"role": "user", "content": truncated_text},
        ]
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=1,
            max_tokens=4096,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            response_format={"type": "json_object"},
        )
        pdf_info = PDFInfo.model_validate_json(response.choices[0].message.content)
        
        # If no date is found, use the current date
        if pdf_info.date == "NO_DATE":
            pdf_info.date = datetime.now().strftime("%Y-%m-%d")
        
        return (
            f"{pdf_info.date} -- {pdf_info.document_kind} - "
            f"{pdf_info.document_name}.pdf"
        )
    except Exception as e:
        print(f"Error generating filename: {str(e)}")
        return os.path.basename(original_path)  # Return original filename if there's an error


def rename_file(old_path: str, new_name: str) -> None:
    """
    Rename a file with a new name.

    Args:
        old_path (str): Current path of the file.
        new_name (str): New name for the file.
    """
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    os.rename(old_path, new_path)
