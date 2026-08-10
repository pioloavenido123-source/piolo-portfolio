import pymupdf
doc = pymupdf.open('resume.pdf')
print(f"Pages: {doc.page_count}")
for page_num, page in enumerate(doc):
    print(f"\n=== PAGE {page_num+1} ===")
    text = page.get_text()
    # Print full text without truncation
    for line in text.split('\n'):
        if line.strip():
            print(line)