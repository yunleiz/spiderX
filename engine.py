import base64
import io
import json
import urllib

from PIL.Image import core as _imaging
import io
from PIL import Image
import numpy as np
import requests


# from google.protobuf.json_format import MessageToJson
# from google.cloud import vision

def lambda_handler(event, context):
    with urllib.request.urlopen(event['image']) as url:
        image = url.read()

    file = io.BytesIO(image)
    img = Image.open(file)

    img_width, img_height = img.size
    target_height = 300
    scale_factor = target_height * 1. / img_height
    target_width = int(scale_factor * img_width)
    img = img.resize((target_width, target_height), Image.ANTIALIAS)
    img_width, img_height = img.size
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    image_content = base64.b64encode(img_byte_arr.getvalue()).decode('UTF-8')

    r = requests.post(
        "https://vision.googleapis.com/v1/images:annotate?key=AIzaSyAllju_HwbFwSVVZ7DNj6JPfxAwNkYthiQ",
        data=json.dumps({'requests': [
            {
                'image': {
                    'content': image_content
                },
                'features': [
                    {
                        'type': 'DOCUMENT_TEXT_DETECTION'
                    }, {
                        'type': 'TEXT_DETECTION'
                    }
                ]
            }
        ]}))

    results = json.loads(r.text)

    text2segs = {}

    for boundingPoly in results['responses'][0]['textAnnotations']:

        text = boundingPoly['description']
        vertices = boundingPoly['boundingPoly']['vertices']
        n_v = len(vertices)

        x_segs = []
        y_segs = []

        for ix in range(n_v - 1):
            x_seg = [vertices[ix]['x'], vertices[ix + 1]['x']]
            y_seg = [vertices[ix]['y'], vertices[ix + 1]['y']]
            x_segs.append(x_seg)
            y_segs.append(y_seg)

        x_seg = [vertices[ix + 1]['x'], vertices[0]['x']]
        y_seg = [vertices[ix + 1]['y'], vertices[0]['y']]
        x_segs.append(x_seg)
        y_segs.append(y_seg)

        text2segs[text] = (x_segs, y_segs)

    text2segs_valid = {}

    for key in text2segs.keys():

        xsegs, ysegs = text2segs[key]

        # get vertices from segs
        xvers = []
        for xseg in xsegs:
            xvers += xseg
        xvers = list(set(xvers))

        yvers = []
        for yseg in ysegs:
            yvers += yseg
        yvers = list(set(yvers))

        xext = (max(xvers) - min(xvers)) * 1. / img_height
        yext = (max(yvers) - min(yvers)) * 1. / img_height

        # filter by height
        if ((0.04 < yext) & (yext < 0.1) & (2 < len(key)) & (len(key) < 8)):
            text2segs_valid[key] = text2segs[key]

    text2segs_valid_pos = {}

    keys = []
    xavgs = []
    yavgs = []

    for key in text2segs_valid.keys():
        xsegs, ysegs = text2segs_valid[key]

        # get vertices from segs
        xvers = []
        for xseg in xsegs:
            xvers += xseg

        yvers = []
        for yseg in ysegs:
            yvers += yseg

        xavg = np.array(xvers).mean()
        yavg = np.array(yvers).mean()

        keys.append(key)
        xavgs.append(xavg)
        yavgs.append(yavg)

    left_ix = np.array(xavgs).argmin()
    right_ix = np.array(xavgs).argmax()

    if left_ix != right_ix:
        left_text = keys[left_ix]
        right_text = keys[right_ix]

        #     text2segs_valid_pos[left_text] = text2segs_valid[left_text]
        #     text2segs_valid_pos[right_text] = text2segs_valid[right_text]

        # combine left and right
        xvers = []
        yvers = []
        xsegs, ysegs = text2segs_valid[left_text]
        # get vertices from segs
        for xseg in xsegs:
            xvers += xseg
        for yseg in ysegs:
            yvers += yseg

        xsegs, ysegs = text2segs_valid[right_text]
        # get vertices from segs
        for xseg in xsegs:
            xvers += xseg
        for yseg in ysegs:
            yvers += yseg

        xmin = np.array(xvers).min()
        xmax = np.array(xvers).max()
        ymin = np.array(yvers).min()
        ymax = np.array(yvers).max()

        xsegs_combined = [[xmin, xmax], [xmax, xmax], [xmax, xmin], [xmin, xmin]]
        ysegs_combined = [[ymin, ymin], [ymin, ymax], [ymax, ymax], [ymax, ymin]]

        result_text = left_text + ' ' + right_text
        text2segs_valid_pos[result_text] = [xsegs_combined, ysegs_combined]

    else:
        result_text = keys[left_ix]
        text2segs_valid_pos[result_text] = text2segs_valid[result_text]

    return result_text


if __name__ == '__main__':
    event = {"image": "https://s3.amazonaws.com/temp-test-datascience/19869_0.jpg"}
    print(lambda_handler(event, None))