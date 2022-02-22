import io
import json
import base64
import numpy as np
from PIL import Image
# from wand.image import Image
from flask import Flask, request, render_template
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app)

# Read image features
# query_emb = np.load('query_emb.npy')
all_emb = np.load('all_emb.npy')
all_images = np.load('all_images.npy')

def encode_img(img):
    # img = Image.fromarray(np.uint8(img * 255) , 'L')
    data = io.BytesIO()
    img.save(data, 'JPEG')
    enc = base64.b64encode(data.getvalue())
    # enc = base64.b64encode(img.tobytes())
    return enc

def get_annotation(annotations):
    annotation = annotations[0]
    for key, annotation_types in annotation['annotations'].items():
        if annotation_types:
            for row in annotation_types:
                # print(row)
                
                left = row['handles']['textBox']['boundingBox']['left'] - row['handles']['textBox']["x"]
                
                json_data = { 
                    "width":row['handles']['textBox']['boundingBox']['width'],
                    "height":row['handles']['textBox']['boundingBox']['height'],
                    "left":left,
                    "right": left+row['handles']['textBox']['boundingBox']['width'],
                    "top":row['handles']['textBox']['boundingBox']['top'],
                    "bottom":row['handles']['textBox']['boundingBox']['top']+row['handles']['textBox']['boundingBox']['height'],
                    "uuid":row["uuid"],
                    "x":row['handles']['textBox']["x"],
                    "y":row['handles']['textBox']["y"],
                    "length":row['length'] if row.get("length") else 0,
                    "unit":row['unit'],
                }

    return json_data

def crop_image(img, json_data):
    # bbox = 
    pass

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        bs64_img = request.get_json()['image_64']
        # with open('./image-00003.dcm.base64', 'r') as f:
        #     bs64_img = f.readlines()[0].strip()
        bs64_img = base64.b64decode(bs64_img)
        # query = base64.b64decode(query)
        query = np.frombuffer(bs64_img, dtype=np.float32)
        print(query.shape)
        # query = Image.open(io.BytesIO(bs64_img))

        # annotations = json.loads(request.form["annotation"])
        # img_encoded = json.loads(request.form["image"])

        # img_file = request.files['image']
        # img = Image(blob = img_file)
        
        # buffer = io.BytesIO()
        # img_file.write(buffer, 'JPEG')
        # print(img_file, type(img_file))
        # print('123')
        # img_bytes = img_file.read()
        # stream = io.BytesIO(img_bytes)
        # stream.seek(0)

        # # print(type(stream))
        # image = Image.open(stream)
        # # print(image)
        # enc = base64.b64encode(img_bytes)
        # # print(enc)
        # # img = Image(blob=img_file)

        # annotations = json.loads(request.form["annotation"])
        # json_data = get_annotation(annotations)
        
        # Query
        # query = crop_image(img, json_data)
        # query = encode_img(query)
        query_emb = np.arange(256)

        # Run search
        distance = np.subtract(query_emb, all_emb)
        distance = np.linalg.norm(distance, axis=1, ord=2)
        indices = np.argsort(distance)
        candidates = [(encode_img(all_images[i]).decode('utf-8'), distance[i]) for i in indices[1:6]]

        return render_template(
            'index.html',
            query_path=query.decode('utf-8'),
            candidates=candidates)
            
    else:
        return render_template('index.html')


if __name__=="__main__":
    # CORS(app)
    app.run("0.0.0.0", debug=True)
