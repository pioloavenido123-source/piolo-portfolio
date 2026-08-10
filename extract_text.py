import pymupdf
doc = pymupdf.open('resume.pdf')
for page_num, page in enumerate(doc):
    print(f'=== PAGE {page_num+1} ===')
    blocks = page.get_text('dict')['blocks']
    for block in blocks:
        if 'lines' not in block:
            continue
        for line in block['lines']:
            for span in line['spans']:
                y = round(span['bbox'][1], 1)
                x = round(span['bbox'][0], 1)
                h = round(span['bbox'][3] - span['bbox'][1], 1)
                print(f'y={y} x={x} h={h} size={span["size"]:.1f} | {span["text"][:90]}')