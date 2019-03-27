from PIL import Image, ImageDraw, ImageColor
import os


def GenerateBasic(filepath, color, size):
    color = ImageColor.getcolor(color, 'RGBA')

    imageAvatar = Image.open(filepath)
    sideLength = imageAvatar.width

    r = sideLength / 2 * (1-size)

    imageRing = Image.new('RGBA', (sideLength, sideLength), color=color)
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

