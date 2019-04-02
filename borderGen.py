from PIL import Image, ImageDraw, ImageColor, ImageSequence
import os, io

def GetMostFrequentColor(filepath):
    image = Image.open(filepath)
    
    image = image.convert("RGB")
    pixels = image.getcolors(image.width ** 2)

    most_frequent_pixel = pixels[0]

    for count, color in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, color)
    
    return '#%02x%02x%02x' % most_frequent_pixel[1]

def GenerateBasic(filepath, color, size):
    color = ImageColor.getcolor(color, 'RGBA')

    imageAvatar = Image.open(filepath)
    sideLength = imageAvatar.width

    r = sideLength / 2 * (1-size)

    imageRing = Image.new('RGBA', imageAvatar.size, color=color)
    draw = ImageDraw.Draw(imageRing)
    x = sideLength / 2
    
    draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))
    
    imageAvatar.paste(imageRing, (0, 0), imageRing)
    imageAvatar.save(filepath)
    os.replace(filepath, filepath.replace(".webp", ".png")) 

    return filepath.replace(".webp", ".png")

def GenerateWithTexture(filepath, texturepath, size):
    imageAvatar = Image.open(filepath)
    imageRing = Image.open(texturepath)

    r = imageAvatar.width / 2 * (1-size)
    
    imageRing = imageRing.resize(imageAvatar.size)
    imageRing = imageRing.convert("RGBA")
    draw = ImageDraw.Draw(imageRing)
    x = imageAvatar.width / 2
    
    draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))
    
    imageAvatar.paste(imageRing, (0, 0), imageRing)
    imageAvatar.save(filepath)
    
    os.replace(filepath, filepath.replace(".webp", ".png")) 

    return filepath.replace(".webp", ".png")

def GenerateGif(filepath, color, size):
    imageGif = Image.open(filepath)
    
    sideLength = 512

    r = sideLength / 2 * (1-size)
    x = sideLength / 2
    
    imageRing = Image.new('RGBA', (512, 512), color=color)
    
    frames = []
    for frame in ImageSequence.Iterator(imageGif):
        frame = frame.resize((512, 512))
        draw = ImageDraw.Draw(imageRing)
        draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))

        frame = frame.convert('RGBA')
        frame.paste(imageRing, (0, 0), imageRing)
        
        frames.append(frame)
    frames[0].save(filepath, save_all=True, append_images=frames[1:])

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