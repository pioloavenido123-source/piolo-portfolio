from PIL import Image
img = Image.open('profile.jpg')
print(f'Original: {img.size}, mode={img.mode}')
img = img.convert('RGB')
w, h = img.size
size = min(w, h)
left = (w - size) // 2
top = (h - size) // 2
img = img.crop((left, top, left + size, top + size))
img = img.resize((400, 400), Image.LANCZOS)
img.save('profile.jpg', 'JPEG', quality=85, optimize=True)
print('Optimized: 400x400 JPEG')