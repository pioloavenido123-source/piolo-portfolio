from PIL import Image
import os, hashlib

src = '/home/cmark/projects/openwebui/data/uploads/ab5bd417-b25b-431b-9072-7dd773144dd2_719159710_921058027655696_4928549003061234339_n.png'
dst = '/home/cmark/piolo-portfolio/profile.jpg'

print(f'Source exists: {os.path.exists(src)}')
print(f'Source size: {os.path.getsize(src)} bytes')

img = Image.open(src)
print(f'Source image: {img.size}, mode={img.mode}')

if img.mode in ('RGBA', 'P'):
    img = img.convert('RGB')

img = img.resize((400, 400), Image.LANCZOS)
img.save(dst, 'JPEG', quality=90)
print(f'Saved to: {dst}')
print(f'Output size: {os.path.getsize(dst)} bytes')

with open(dst, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()
print(f'Output MD5: {md5}')
print(f'Old placeholder MD5: 97b3e1fd2ba479e43b87568b5ab2a26b')
print(f'Different from placeholder: {md5 != "97b3e1fd2ba479e43b87568b5ab2a26b"}')