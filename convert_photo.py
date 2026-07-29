from PIL import Image

src = '/home/cmark/projects/openwebui/data/uploads/5d4040f8-2ae0-4315-92e6-4fe0b6c5fdc1_719159710_921058027655696_4928549003061234339_n.png'
dst = '/home/cmark/piolo-portfolio/profile.jpg'

img = Image.open(src)
print(f'Original size: {img.size}, mode: {img.mode}')
img = img.convert('RGB')
img = img.resize((400, 400), Image.LANCZOS)
img.save(dst, 'JPEG', quality=85)
print(f'Saved profile.jpg at {img.size}')