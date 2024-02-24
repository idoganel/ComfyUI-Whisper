from PIL import ImageDraw, ImageFont, Image
from .utils import tensor2pil, pil2tensor, tensor2Mask
import math
import os
import random    

FONT_DIR = os.path.join(os.path.dirname(__file__),"fonts")

class AddSubtitlesToFramesNode:
    @classmethod
    def INPUT_TYPES(s):

        return {
            "required": { 
                "images": ("IMAGE",),
                "alignment" : ("whisper_alignment",),
                "font_color": ("STRING",{
                    "default": "white"
                }),
                "font_family": (os.listdir(FONT_DIR),),
                "font_size": ("INT",{
                    "default": 100,
                    "step":2,
                    "display": "number"
                }),
                "x_position": ("INT",{
                    "default": 100,
                    "step":50,
                    "display": "number"
                }),
                "y_position": ("INT",{
                    "default": 100,
                    "step":50,
                    "display": "number"
                }),
                "center_x": ("BOOLEAN", {"default": True}),
                "center_y": ("BOOLEAN", {"default": True}),
                "video_fps": ("INT",{
                    "default": 24,
                    "step":1,
                    "display": "number"
                }),
                                "rtl": ("BOOLEAN", {"default": True}),
                                "effects": ("BOOLEAN", {"default": True}),


            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "IMAGE", "subtitle_coord", )
    RETURN_NAMES = ("IMAGE","MASK", "cropped_subtitles","subtitle_coord",)
    FUNCTION = "add_subtitles_to_frames"
    CATEGORY = "whisper"


    def add_subtitles_to_frames(self, images, alignment, font_family, font_size, font_color, x_position, y_position, center_x, center_y, video_fps,rtl,effects):
        pil_images = tensor2pil(images)

        pil_images_with_text = []
        cropped_pil_images_with_text = []
        pil_images_masks = []
        subtitle_coord = []
        x_position_o = x_position
        y_position_o = y_position
        font_size_o = font_size

        #font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)

        if len(alignment) == 0:
            pil_images_with_text = pil_images
            cropped_pil_images_with_text = pil_images
            subtitle_coord.extend([(0,0,0,0)]*len(pil_images))

            # create mask
            width, height = pil_images[0].size
            black_img = Image.new('RGB', (width, height), 'black')
            pil_images_masks.extend([black_img]*len(pil_images))
        

        last_frame_no = 0
        for i in range(len(alignment)):
            alignment_obj = alignment[i]
            start_frame_no = math.floor(alignment_obj["start"] * video_fps)
            end_frame_no = math.floor(alignment_obj["end"] * video_fps)

            if effects: # add some randomness to the text
                x_position = x_position_o + random.randint(-25,25)
                y_position = y_position_o + random.randint(-45,45)
                font_size = font_size_o + random.randint(-30,30)
                font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)
            else:
                font = ImageFont.truetype(os.path.join(FONT_DIR,font_family), font_size)

            # create images without text
            for i in range(last_frame_no, start_frame_no):
                img = pil_images[i].convert("RGB")
                width, height = img.size
                pil_images_with_text.append(img)

                # create mask + cropped image
                black_img = Image.new('RGB', (width, height), 'black')
                pil_images_masks.append(black_img)
                black_img = Image.new('RGB', (1, 1), 'black') # to prevent max() from considering these images, use very small size
                cropped_pil_images_with_text.append(black_img)  
                subtitle_coord.append((0,0,0,0))


            for i in range(start_frame_no,end_frame_no):
                img = pil_images[i].convert("RGB")
                width, height = img.size

                d = ImageDraw.Draw(img)

                
                if rtl:   # a shity way to flip the text
                    text= alignment_obj["value"][::-1]
                # center text
                text_bbox = d.textbbox((x_position, y_position),text, font=font)
           
            #    text_bbox = d.textbbox((x_position, y_position), alignment_obj["value"], font=font)
                if center_x:
                    text_width = text_bbox[2] - text_bbox[0]
                    x_position = (width - text_width)/2
                if center_y:
                    text_height = text_bbox[3] - text_bbox[1]
                    y_position = (height - text_height)/2


                # add text to video frames
                #d.text((x_position, y_position), alignment_obj["value"], fill=font_color,font=font)
                d.text((x_position, y_position), text, fill=font_color,font=font)
              
                pil_images_with_text.append(img)

                # create mask
                black_img = Image.new('RGB', (width, height), 'black')
                d = ImageDraw.Draw(black_img)
                d.text((x_position, y_position),text, fill="white",font=font)    
                pil_images_masks.append(black_img)    

                # crop subtitles to black frame
                text_bbox = d.textbbox((x_position,y_position), text, font=font)
                cropped_text_frame = black_img.crop(text_bbox)
                cropped_pil_images_with_text.append(cropped_text_frame)
                subtitle_coord.append(text_bbox)

            
            last_frame_no = end_frame_no

        # add missing frames with no text at end
        for i in range(len(pil_images_with_text),len(pil_images)):
            pil_images_with_text.append(pil_images[i])
            width,height = pil_images[i].size

            # create mask + cropped image
            black_img = Image.new('RGB', (width, height), 'black')
            pil_images_masks.append(black_img)
            black_img = Image.new('RGB', (1, 1), 'black') # to prevent max() from considering these images, use very small size
            cropped_pil_images_with_text.append(black_img)  
            subtitle_coord.append((0,0,0,0))

        # make cropped images same size
        cropped_pil_images_with_text_normalised = []
        max_width = max(img.width for img in cropped_pil_images_with_text)
        max_height = max(img.height for img in cropped_pil_images_with_text)

        max_width += max_width%2 #      make even so it wont fail 
        max_height += max_height%2 #    make even
        for img in cropped_pil_images_with_text:
            blank_frame = Image.new("RGB", (max_width, max_height), "black")
            blank_frame.paste(img, (0,0))
            cropped_pil_images_with_text_normalised.append(blank_frame)


        tensor_images = pil2tensor(pil_images_with_text)
        cropped_pil_images_with_text_normalised = pil2tensor(cropped_pil_images_with_text_normalised)
        tensor_masks = tensor2Mask(pil2tensor(pil_images_masks))

        return (tensor_images,tensor_masks,cropped_pil_images_with_text_normalised,subtitle_coord,)
