import fitz  # PyMuPDF
import sympy as sp
import re

# Step 1: Load the PDF and extract text
def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    return text

# Step 2: Extract LaTeX-like equations using regular expressions
def extract_equations(text):
    # This regex looks for basic LaTeX-style equations (e.g., (a + b)^2, x = a + b)
    equation_pattern = r'\$.*?\$|\\[a-zA-Z]+\{.*?\}|[a-zA-Z0-9_]+(?:\s*[\+\-\*/\^=]\s*[a-zA-Z0-9_]+)+'
    equations = re.findall(equation_pattern, text)
    return equations

# Step 3: Convert LaTeX to SymPy expression
def parse_latex_to_sympy(latex_eqn):
    try:
        # Parse the LaTeX equation into a SymPy expression
        return sp.sympify(latex_eqn.replace('$', ''))
    except Exception as e:
        print(f"Error parsing {latex_eqn}: {e}")
        return None

# # Step 4: Get sentence embeddings from plain text using Sentence Transformers
# def get_text_embeddings(text):
#     model = SentenceTransformer('all-MiniLM-L6-v2')
#     sentences = text.split('\n')  # Split by lines, can be modified to split by sentences
#     embeddings = model.encode(sentences)
#     return embeddings

# Main function to process the PDF
def process_pdf(pdf_path):
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)
    
    # Extract equations (in LaTeX-like format)
    equations = extract_equations(text)
    
    # Process equations using SymPy
    parsed_equations = [parse_latex_to_sympy(eq) for eq in equations if parse_latex_to_sympy(eq) is not None]
    
    # Get text embeddings for the rest of the content
    # embeddings = get_text_embeddings(text)

    return text,equations,parsed_equations

# Example usage
pdf_path = ".\Latex_Test_Docs\differential-equations.pdf"  # Replace with the path to your PDF
text,equations,parsed_equations = process_pdf(pdf_path)

# Write the extracted text to a file
with open('extracted_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

# Write the extracted equations to a file
with open('extracted_equations.txt', 'w', encoding='utf-8') as f:
    for eq in equations:
        f.write(eq + '\n')

# Write the parsed equations to a file
with open('parsed_equations.txt', 'w', encoding='utf-8') as f:
    for parsed_eq in parsed_equations:
        f.write(str(parsed_eq) + '\n')