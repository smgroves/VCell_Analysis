#Merging plots in different pfds
from pypdf import PdfWriter
import os

os.chdir('/Users/catalinaalvarez/Documents/CPC_plots_2026/CPC_readouts/')

def merge_pdfs(output_filename, input_pdfs):
    # Initialize the writer
    merger = PdfWriter()

    for pdf in input_pdfs:
        # Append the entire PDF file to the writer
        merger.append(pdf)

    # Save the result
    merger.write(output_filename)
    merger.close()

# Example usage
plots = ["Comparison arms _0%_ic_corrected_500s.pdf",
        "Comparison arms _5%_ic_corrected_500s.pdf",
        "Comparison arms _10%_ic_corrected_500s.pdf",
        "Comparison arms _15%_ic_corrected_500s.pdf",
        "Comparison arms _20%_ic_corrected_500s.pdf",
        "Comparison arms _25%_ic_corrected_500s.pdf",
        "Comparison arms _30%_ic_corrected_500s.pdf",
        "Comparison arms _35%_ic_corrected_500s.pdf",
        "Comparison arms _40%_ic_corrected_500s.pdf",
        "Comparison arms _45%_ic_corrected_500s.pdf",
        "Comparison arms _50%_ic_corrected_500s.pdf",
        "Comparison arms _55%_ic_corrected_500s.pdf",
        "Comparison arms _60%_ic_corrected_500s.pdf",
        "Comparison arms _65%_ic_corrected_500s.pdf",
        "Comparison arms _70%_ic_corrected_500s.pdf",
        "Comparison arms _75%_ic_corrected_500s.pdf",
        "Comparison arms _80%_ic_corrected_500s.pdf",
        "Comparison arms _85%_ic_corrected_500s.pdf",
        "Comparison arms _90%_ic_corrected_500s.pdf",
        "Comparison arms _95%_ic_corrected_500s.pdf",
        "Comparison arms _100%_ic_corrected_500s.pdf"
         ]
merge_pdfs("combined_plots_ic_corrected.pdf", plots)
