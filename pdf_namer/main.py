import argparse
import os
from typing import List
from concurrent.futures import ProcessPoolExecutor

from pdf_namer import process_pdf


def main() -> None:
    """
    Main entry point for the PDF naming CLI application.
    """
    parser = argparse.ArgumentParser(
        description="Process and rename PDF documents using AI."
    )
    parser.add_argument(
        "path",
        help="Path to a PDF file or directory containing PDFs"
    )
    parser.add_argument(
        "-w", "--workers",
        type=int,
        default=3,
        help="Number of worker processes (default: 3)",
    )
    parser.add_argument(
        "-l", "--language",
        type=str,
        required=True,
        help="Language for filename generation (default: german)",
    )
    args = parser.parse_args()

    if os.path.isfile(args.path):
        process_single_file(args.path, args.language)
    elif os.path.isdir(args.path):
        process_directory(args.path, args.workers, args.language)
    else:
        print(f"Error: {args.path} is not a valid file or directory")


def process_single_file(file_path: str, language: str) -> None:
    """
    Process a single PDF file.

    Args:
        file_path (str): Path to the PDF file to process.
        language (str): Language for filename generation (-l/--language).
    """
    try:
        new_name = process_pdf(file_path, language)
        print(f"Processed: {file_path} -> {new_name}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")


def process_directory(directory: str, num_workers: int, language: str) -> None:
    """
    Process all PDF files in a directory recursively using multiple processes.

    Args:
        directory (str): Path to the directory containing PDF files.
        num_workers (int): Number of worker processes to use (-w/--workers).
        language (str): Language for filename generation (-l/--language).
    """
    pdf_files = get_pdf_files(directory)
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        for file_path in pdf_files:
            executor.submit(process_single_file, file_path, language)


def get_pdf_files(directory: str) -> List[str]:
    """
    Recursively find all PDF files in a directory.

    Args:
        directory (str): Path to the directory to search.

    Returns:
        List[str]: A list of paths to PDF files found in the directory.
    """
    pdf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files


if __name__ == "__main__":
    main()
