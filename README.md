# PDF Namer

PDF Namer is a Python CLI application that processes PDF documents and renames them based on AI-generated descriptions. This tool is designed to help organize and manage collections of PDF documents by extracting meaningful information and creating standardized filenames.

## Features

- Process single PDF files or entire directories recursively
- Generate meaningful filenames using OpenAI's GPT models
- Multiprocessing support for faster batch processing
- Customizable number of worker processes
- Language selection for filename generation
- Skip files that are already correctly named
- Force processing of files even if they are already correctly named

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/llabusch93/pdf-namer.git
   cd pdf-namer
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key. You have two options:

   a. Set it as an environment variable:
      ```
      export OPENAI_API_KEY=your_api_key_here
      ```

   b. Store it in a file:
      - Create a file named `.openai` in your home directory (`~/.openai`)
      - Add your API key to this file (just the key, without any quotes or additional text)

   The application will first check for the environment variable, and if not found, it will look for the `.openai` file in your home directory.

## Usage

To process a single PDF file:

```
pdf-namer /path/to/your/file.pdf
```

To process all PDF files in a directory recursively:

```
pdf-namer /path/to/your/directory
```

To specify the number of worker processes:

```
pdf-namer /path/to/your/directory --workers 5
```

To specify the language for filename generation:

```
pdf-namer /path/to/your/file.pdf --language english
```

To force processing of files even if they are already correctly named:

```
pdf-namer /path/to/your/file.pdf --force
```

## How it works

1. The program checks if the input is a single file or a directory.
2. For each PDF file:
   a. The program checks if the filename is already in the correct format (YYYY-MM-DD -- DOCUMENT_KIND - DOCUMENT_DESCRIPTION.pdf).
   b. If the filename is correct and the `--force` flag is not used, the file is skipped.
   c. If the filename is incorrect or the `--force` flag is used:
      - The text is extracted from the PDF.
      - The extracted text is sent to OpenAI's GPT model to generate a meaningful filename.
      - The file is renamed using the generated filename.
3. If processing a directory, multiple files are processed concurrently using Python's `multiprocessing` module.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

Laurence Labusch (laurence.labusch@gmail.com)
