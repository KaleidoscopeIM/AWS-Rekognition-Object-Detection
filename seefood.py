from PIL import Image, ImageDraw, ImageFont
import boto3
from pprint import pprint, pformat
from io import BytesIO
from image_helpers import *

# --------------------------------------------------------------------
# DO NOT CHANGE THESE FUNCTIONS


def format_text(text, columns):
    '''
    Returns a copy of text that will not span more than the specified number of columns
    :param text: the text
    :param columns: the maximum number of columns
    :return: the formatted text
    '''
    # format the text to fit the specified columns
    import re
    text = re.sub('[()\']', '', pformat(text, width=columns))
    text = re.sub('\n ', '\n', text)
    return text


# HINT: This will be helpful for centering the label
def text_rect_size(text, font, draw=None):
    """
    Returns the size of the rectangle to be used to
    draw as the background for the text.
    :param text: the text to be displayed
    :param font: the font to be used
    :param draw: an ImageDraw.Draw object
    :return: the size of the rectangle to be used to draw as the background for the text
    """
    if draw is None:
        dummy_img = Image.new('RGB', (0, 0), (255, 255, 255, 0))
        draw = ImageDraw.Draw(dummy_img)
        (width, height) = draw.multiline_textsize(text, font=font)
        del draw
    else:
        (width, height) = draw.multiline_textsize(text, font=font)
    return (width * 1.1, height * 1.3)


def add_text_to_img(img, text, bbox, pos=(0, 0), color=(0, 0, 0), bgcolor=(255, 255, 255, 128),
                    columns=60,
                    font=ImageFont.truetype('ariblk.ttf', 22)):
    '''
    Creates and returns a copy of the image with the specified text displayed on it
    :param img: the (Pillow) image
    :param text: the text to display
    :param pos: a 2 tuple containing the xpos, and ypos of the text
    :param color: the fill color of the text
    :param bgcolor: the background color of the box behind the text
    :param columns: the max number of columns for the text
    :param font: the font to use
    :return: a copy of the image with the specified text displayed on it
    '''

    # make a blank image for the text, initialized to transparent text color
    txt_img = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_img)

    # format the text
    text = format_text(text, columns)
    # get the size of the text drawn in the specified font
    (text_width, text_height) = ImageDraw.Draw(img).multiline_textsize(text, font=font)

    # compute positions and box size
    (xpos, ypos) = pos
    rwidth = text_width * 1.1
    rheight = text_height * 1.4
    text_xpos = xpos + (rwidth - text_width) / 2
    text_ypos = ypos + (rheight - text_height) / 2

    # draw the rectangle (slightly larger) than the text
    draw.rectangle([xpos, ypos, xpos + rwidth, ypos + rheight], fill=bgcolor)

    # draw the text on top of the rectangle
    draw.multiline_text((text_xpos, text_ypos), text, font=font, fill=color)
    draw.rectangle((bbox["Width"],bbox["Height"],bbox['Left'],bbox['Height']),fill=bgcolor, outline="blue")
    del draw # clean up the ImageDraw object
    return Image.alpha_composite(img.convert('RGBA'), txt_img)


def get_pillow_img(imgbytes):
    """
    Creates and returns a Pillow image from the given image bytes
    :param imgbytes: the bytes of the image
    """
    return Image.open(BytesIO(imgbytes))

# END DO NOT CHANGE SECTION
# --------------------------------------------------------------------

def label_image(img, search_for, confidence=50):
    '''
    Creates and returns a copy of the image, with labels from Rekognition displayed on it
    :param img: a string that is either the URL or filename for the image
    :param confidence: the confidence level (defaults to 50)

    :return: a copy of the image, with labels from Rekognition displayed on it
    '''
    # replace pass below with your implementation
    text_found = format_text(search_for, 60)
    text_not_found = format_text("not found", 60)

    text_rect_found = text_rect_size(text_found, ImageFont.truetype('ariblk.ttf', 22))
    text_rect_not_found = text_rect_size(text_not_found, ImageFont.truetype('ariblk.ttf', 22))

    img_bytes = get_image(img)

    client = boto3.client('rekognition')
    rekresp = client.detect_labels(Image={'Bytes': img_bytes})
    label_lst = rekresp["Labels"]
    #pprint(label_lst)

    is_found = False
    boundingBox = {}
    for a in label_lst:
        search = a["Name"].lower()
        if len(a["Instances"]) == 0:
            continue
        if search == search_for:
            is_found = True
            boundingBox = a["Instances"][0]["BoundingBox"]
            break

    pillow_img_bytes = get_pillow_img(img_bytes)
    if is_found:
        final_img = add_text_to_img(pillow_img_bytes, text_found, boundingBox, text_rect_found, (255,255,255), (0,255,0))
    else:
        final_img = add_text_to_img(pillow_img_bytes, text_not_found, boundingBox, text_not_found,(255,255,255), (255,0,0))
    return final_img


if __name__ == "__main__":
    # can't use input since PyCharm's console causes problems entering URLs
    # img = input('Enter either a URL or filename for an image: ')

    # pizza
    # img = 'https://render.fineartamerica.com/images/rendered/default/poster/8/10/break/images/artworkimages/medium/1/pizza-slice-diane-diederich.jpg'

    # hot dog
    # img = 'https://i.kinja-img.com/gawker-media/image/upload/s--6RyJpgBM--/c_scale,f_auto,fl_progressive,q_80,w_800/tmlwln8revg44xz4f0tj.jpg'

    # usf
    #img = 'https://media.wtsp.com/assets/WTSP/images/5adf8c34-ca2a-4462-b79e-4a25d8c97500/5adf8c34-ca2a-4462-b79e-4a25d8c97500_360x203.jpg'

    # burgers
    # img = 'https://i.ytimg.com/vi/0SPwwpruGIA/maxresdefault.jpg'

    # another hot dog
    img = 'https://wdwnt.com/wp-content/uploads/2018/07/Two-Foot-Long-Hot-Dog-900x556.jpg'

    # clearwater beach
    #img = 'https://wusfnews.wusf.usf.edu/sites/wusf/files/styles/medium/public/202003/clearwater_beach.jpg'
    srch = 'hot dog'
    labelled_image = label_image(img, srch)

    labelled_image.show()