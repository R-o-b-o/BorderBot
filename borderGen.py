from PIL import Image, ImageDraw, ImageColor, ImageSequence
from io import BytesIO
import config
import math, random

imageFormat = config.imageFormat

def GetMostFrequentColor(filepath):
    image = Image.open(filepath)
    
    image = image.convert('P', palette=Image.ADAPTIVE, colors=10)
    image = image.convert("RGB")
    pixels = image.getcolors(image.width ** 2)

    most_frequent_pixel = pixels[0]

    for count, color in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, color)
    
    if most_frequent_pixel[1] == (255, 255, 255) or most_frequent_pixel[1] == (0, 0, 0):
        most_frequent_pixel = random.choice(pixels)

    return '#%02x%02x%02x' % most_frequent_pixel[1]

def GetDominantColors(filepath, numColors):
    image = Image.open(filepath)
    image = image.convert('P', palette=Image.ADAPTIVE, colors=numColors)
    image = image.convert("RGB")
    
    colors = image.getcolors(numColors)
    imageColors = Image.new("RGB", (100 * numColors, 100))
    draw = ImageDraw.Draw(imageColors)
    for i in range(0, len(colors)):
        draw.rectangle([i * 100, 0, i * 100 + 100, 100], fill=colors[i][1])

    imageBytes = BytesIO()
    imageColors.save(imageBytes, format="png")
    imageBytes.seek(0)
    return imageBytes

def GenerateBasic(filepath, color, size):
    if filepath.endswith(".gif"):
        return GenerateGif(filepath, color, size)
    
    color = ImageColor.getcolor(color, 'RGBA')

    imageAvatar = Image.open(filepath)
    imageRing = Image.new('RGBA', (2048, 2048), color=color)

    midp = imageRing.width / 2
    r = midp * (1-size)
    
    draw = ImageDraw.Draw(imageRing)
    
    draw.ellipse((midp-r, midp-r, midp+r, midp+r), fill=(0,0,0,0))
    imageRing.thumbnail(imageAvatar.size, Image.LANCZOS)
    imageAvatar.paste(imageRing, (0, 0), imageRing)

    mask = Image.new('L', (2048, 2048), 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + mask.size, fill=255)
    imageAvatar.putalpha(mask.resize(imageAvatar.size, Image.LANCZOS))
    
    imageAvatar.thumbnail(config.maxSize, Image.LANCZOS)

    imageBytes = BytesIO()
    imageAvatar.save(imageBytes, format=imageFormat)
    imageBytes.seek(0)
    return imageBytes

def GenerateSquare(filepath, color, size):
    color = ImageColor.getcolor(color, 'RGBA')

    imageAvatar = Image.open(filepath)

    x = imageAvatar.width * math.sqrt(1-size)

    imageSquare = Image.new('RGBA', imageAvatar.size, color=color)
    draw = ImageDraw.Draw(imageSquare)
    
    draw.rectangle((x, x, imageAvatar.width - x, imageAvatar.height - x), fill=(0,0,0,0))
    imageAvatar.paste(imageSquare, (0, 0), imageSquare)

    imageBytes = BytesIO()
    imageAvatar.save(imageBytes, format=imageFormat)
    imageBytes.seek(0)
    return imageBytes

def GenerateWithTexture(filepath, texturepath, size):
    if filepath.endswith(".gif"):
        return GenerateGifWithTexture(filepath, texturepath, size)
        
    imageAvatar = Image.open(filepath)
    imageRing = Image.open(texturepath)

    imageRing = imageRing.resize((2048, 2048))
    x = imageRing.width / 2
    r = x * (1-size)
    
    imageRing = imageRing.convert("RGBA")
    draw = ImageDraw.Draw(imageRing)
    
    draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))
    imageRing = imageRing.resize(imageAvatar.size, Image.LANCZOS)
    imageAvatar.paste(imageRing, (0, 0), imageRing)

    mask = Image.new('L', (2048, 2048), 0)
    draw = ImageDraw.Draw(mask) 
    draw.ellipse((0, 0) + mask.size, fill=255)
    imageAvatar.putalpha(mask.resize(imageAvatar.size, Image.LANCZOS))

    imageAvatar.thumbnail(config.maxSize, Image.LANCZOS)
    
    imageBytes = BytesIO()
    imageAvatar.save(imageBytes, format=imageFormat)
    imageBytes.seek(0)
    return imageBytes

def GenerateGif(filepath, color, size):
    imageGif = Image.open(filepath)
    
    sideLength = imageGif.width

    r = sideLength / 2 * (1-size)
    x = sideLength / 2
    
    imageRing = Image.new('RGBA', imageGif.size, color=color)
    
    frames = []
    for frame in ImageSequence.Iterator(imageGif):
        
        draw = ImageDraw.Draw(imageRing)
        draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))

        frame = frame.convert('RGBA')
        frame.paste(imageRing, (0, 0), imageRing)
        
        frames.append(frame)
    imageBytes = BytesIO()
    frames[0].save(imageBytes, format="gif", save_all=True, append_images=frames[1:])
    imageBytes.seek(0)
    return imageBytes

def GenerateGifWithTexture(filepath, texturepath, size):
    imageGif = Image.open(filepath)
    imageRing = Image.open(texturepath)

    sideLength = imageGif.width

    r = sideLength / 2 * (1-size)
    x = sideLength / 2
    imageRing = imageRing.resize(imageGif.size)
    imageRing = imageRing.convert("RGBA")
    
    frames = []
    for frame in ImageSequence.Iterator(imageGif):
        draw = ImageDraw.Draw(imageRing)
        draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))

        frame = frame.convert('RGBA')
        frame.paste(imageRing, (0, 0), imageRing)
        
        frames.append(frame)
    frames[0].save(filepath, save_all=True, append_images=frames[1:])