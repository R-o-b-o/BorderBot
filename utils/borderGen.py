from PIL import Image, ImageDraw, ImageColor, ImageSequence
from io import BytesIO
import config
import math, random, os
from asgiref.sync import sync_to_async
from skimage.color import rgb2lab, lab2rgb
import numpy as np
import warnings

image_format = config.image_format

def color_swap(source, tar):
    with Image.open(source) as sourceImage:
        with Image.open(tar) as tarImage:
            source_lab = rgb2lab(np.array(sourceImage.convert('RGB')))
            target_lab = rgb2lab(np.array(tarImage.convert('RGB')))
            
            data_source = np.asarray(source_lab, dtype=float).reshape(np.multiply.reduce(sourceImage.size), 3)
            data_tar = np.asarray(target_lab, dtype=float).reshape(np.multiply.reduce(tarImage.size), 3)
            
            #dataS = np.add(np.multiply(np.divide(np.subtract(dataS, dataS.mean(axis=0)), dataS.std(axis=0)), dataT.std(axis=0)), dataT.mean(axis=0)).reshape(sourceImage.size[::-1]+(3,))
            data_source = (((data_source - data_source.mean(axis=0)) / data_source.std(axis=0) * data_tar.std(axis=0)) + data_tar.mean(axis=0)).reshape(sourceImage.size[::-1]+(3,))
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                return get_image_bytes(Image.fromarray(np.uint8(lab2rgb(data_source)*255)), image_format)

def get_most_frequent_color(filepath):
    with Image.open(filepath) as image:
        image = image.convert('P', palette=Image.ADAPTIVE, colors=10)
        image = image.convert("RGB")
        pixels = image.getcolors(image.width ** 2)

        most_frequent_pixel = pixels[0]

        for count, color in pixels:
            if count > most_frequent_pixel[0]:
                most_frequent_pixel = (count, color)
        
        if min(most_frequent_pixel[1]) > 235 or max(most_frequent_pixel[1]) < 20:
            most_frequent_pixel = random.choice(pixels)

        return '#%02x%02x%02x' % most_frequent_pixel[1]

def get_dominant_colors(filepath, num_colors):
    with Image.open(filepath) as image:
        image = image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
        image = image.convert("RGB")

        return ['#%02x%02x%02x' % color[1] for color in image.getcolors(num_colors)]

def get_dominant_colors_image(filepath, num_colors):
    with Image.open(filepath) as image:
        image = image.convert('P', palette=Image.ADAPTIVE, colors=num_colors)
        image = image.convert("RGB")
        
        colors = get_dominant_colors(filepath, num_colors)
        image_colors = Image.new("RGB", (100 * num_colors, 100))
        draw = ImageDraw.Draw(image_colors)
        for i in range(0, len(colors)):
            draw.rectangle([i * 100, 0, i * 100 + 100, 100], fill=colors[i])

        return get_image_bytes(image_colors, "png"), colors

@sync_to_async
def get_avatar_history_image(filepaths):
    av_width = math.ceil(math.sqrt(len(filepaths)))
    av_height = math.ceil(len(filepaths) / av_width)

    image_history = Image.new("RGBA", (3000, math.ceil(3000 * av_height/av_width)))
    width = math.trunc(image_history.width / av_width)
    height = math.trunc(image_history.height / av_height)

    for i in range(0, len(filepaths)):
        with Image.open(filepaths[i]) as image:
            #image = image.convert("RGB")
            image = image.resize((width, height))

            image_history.paste(image, ((i % av_width) * width, height * math.trunc(i / av_width)))

    return get_image_bytes(image_history, "webp")

@sync_to_async
def generate_basic(filepath, color, size, image_format=image_format):
    if filepath.endswith(".gif"):
        return generate_basic_GIF(filepath, color, size)
    
    color = ImageColor.getcolor(color, 'RGBA')

    with Image.open(filepath) as image_avatar:
        image_ring = Image.new('RGBA', (2048, 2048), color=color)

        midp = image_ring.width / 2
        r = midp * (1-size)
        
        draw = ImageDraw.Draw(image_ring)
        
        draw.ellipse((midp-r, midp-r, midp+r, midp+r), fill=(0,0,0,0))
        image_ring.thumbnail(image_avatar.size, Image.LANCZOS)
        image_avatar.paste(image_ring, (0, 0), image_ring)

        mask = Image.new('L', (2048, 2048), 0)
        draw = ImageDraw.Draw(mask) 
        draw.ellipse((0, 0) + mask.size, fill=255)
        image_avatar.putalpha(mask.resize(image_avatar.size, Image.LANCZOS))
        
        image_avatar.thumbnail(config.max_size, Image.LANCZOS)

        return get_image_bytes(image_avatar, image_format)

@sync_to_async
def generate_square(filepath, color, size, image_format=image_format):
    color = ImageColor.getcolor(color, 'RGBA')

    with Image.open(filepath) as image_avatar:
        x = image_avatar.width * math.sqrt(1-size)

        image_square = Image.new('RGBA', image_avatar.size, color=color)
        draw = ImageDraw.Draw(image_square)
        
        draw.rectangle((x, x, image_avatar.width - x, image_avatar.height - x), fill=(0,0,0,0))
        image_avatar.paste(image_square, (0, 0), image_square)

        return get_image_bytes(image_avatar, image_format)

@sync_to_async
def generate_textured(filepath, texturepath, size, image_format=image_format, colorSwap=False):
    if filepath.endswith(".gif"):
        return generate_textured_GIF(filepath, texturepath, size)
        
    with Image.open(filepath) as image_avatar:
        with Image.open(texturepath) as image_ring:
            if colorSwap: 
                image_ring = image_ring.resize(image_avatar.size, Image.LANCZOS)
                image_ring = Image.open(color_swap(get_image_bytes(image_ring, "bmp"), get_image_bytes(image_avatar, "bmp")))

            image_ring = image_ring.resize((2048, 2048))


            x = image_ring.width / 2
            r = x * (1-size)
            
            image_ring = image_ring.convert("RGBA")
            draw = ImageDraw.Draw(image_ring)
            
            draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))
            image_ring = image_ring.resize(image_avatar.size, Image.LANCZOS)
            image_avatar.paste(image_ring, (0, 0), image_ring)

            mask = Image.new('L', (2048, 2048), 0)
            draw = ImageDraw.Draw(mask) 
            draw.ellipse((0, 0) + mask.size, fill=255)
            image_avatar.putalpha(mask.resize(image_avatar.size, Image.LANCZOS))

            image_avatar.thumbnail(config.max_size, Image.LANCZOS)
            
            return get_image_bytes(image_avatar, image_format)

def generate_basic_GIF(filepath, color, size):
    with Image.open(filepath) as image_GIF:
        image_ring = Image.new('RGBA', (2048, 2048), color=color)

        midp = image_ring.width / 2
        r = midp * (1-size)
        
        draw = ImageDraw.Draw(image_ring)
        
        draw.ellipse((midp-r, midp-r, midp+r, midp+r), fill=(0,0,0,0))
        image_ring.thumbnail(image_GIF.size, Image.LANCZOS)

        frames = []
        for frame in ImageSequence.Iterator(image_GIF):
            
            frame = frame.convert('RGBA')
            frame.paste(image_ring, (0, 0), image_ring)

            frames.append(frame)
        image_bytes = BytesIO()
        frames[0].save(image_bytes, format="gif", save_all=True, append_images=frames[1:])
        image_bytes.seek(0)
        return image_bytes

def generate_textured_GIF(filepath, texturepath, size):
    with Image.open(filepath) as image_GIF:
        with Image.open(texturepath) as image_ring:
            x = image_GIF.width / 2
            r = x * (1-size)
            
            image_ring = image_ring.resize(image_GIF.size)
            image_ring = image_ring.convert("RGBA")

            draw = ImageDraw.Draw(image_ring)
            draw.ellipse((x-r, x-r, x+r, x+r), fill=(0,0,0,0))
            
            frames = []
            for frame in ImageSequence.Iterator(image_GIF):

                frame = frame.convert('RGBA')
                frame.paste(image_ring, (0, 0), image_ring)
                
                frames.append(frame)
            image_bytes = BytesIO()
            frames[0].save(image_bytes, format="gif", save_all=True, append_images=frames[1:])
            image_bytes.seek(0)
            return image_bytes

def image_to_static(filepath):
    if filepath.endswith('.gif') and os.path.isfile(filepath):
        with Image.open(filepath) as image:
            image.save(filepath.replace('gif', image_format))
        os.remove(filepath)     

def get_image_bytes(image, format):
    image_bytes = BytesIO()
    image.save(image_bytes, format=format)
    image_bytes.seek(0)
    return image_bytes
