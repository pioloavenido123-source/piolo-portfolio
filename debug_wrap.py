import pymupdf

FONT_REG_FILE = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
font_obj = pymupdf.Font(fontfile=FONT_REG_FILE)

# Test: measure a line that was getting cut off
test_line = "A detail-oriented Information Technology graduate and AI developer with hands-on experienc"
w = font_obj.text_length(test_line, fontsize=9)
print(f"Width of cut-off line: {w:.1f} (max should be 483-15=468)")
print(f"  Overflows by: {w - 468:.1f} points")

# Now measure the full word
full = "A detail-oriented Information Technology graduate and AI developer with hands-on experience"
w2 = font_obj.text_length(full, fontsize=9)
print(f"Width with full word: {w2:.1f}")

# What about "experience" alone?
ew = font_obj.text_length("experience", fontsize=9)
print(f"Width of 'experience': {ew:.1f}")

# Check the actual page width and text position
print(f"\nPage width: 595, margins L=56 R=56, content=483")
print(f"Text starts at x=56, so max text end = 56+483 = 539")
print(f"But the cut-off text at x=56 with width {w:.1f} ends at {56+w:.1f}")