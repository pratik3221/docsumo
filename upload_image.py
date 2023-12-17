from flask import Flask, request, jsonify
import pytesseract
import cv2

import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def getSkewAngle(dialted_image) -> float:
    contours, hierarchy = cv2.findContours(dialted_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # Find the largest contour and surround in min area box
    largestContour = contours[0]
    minAreaRect = cv2.minAreaRect(largestContour)
    # Determine the angle. Convert it to the value that was originally used to obtain skewed image
    angle = minAreaRect[-1]
    if angle < -45:
        angle = 90 + angle
    return -1.0 * angle


def rotateImage(image, angle: float):
    newImage = image.copy()
    (h, w) = newImage.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    newImage = cv2.warpAffine(newImage, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return newImage
# Deskew image


def deskew(image):
    angle = getSkewAngle(image)
    return rotateImage(image, -1.0 * angle)


def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (1, 1), 0)

    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    kernal = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 13))

    dilate = cv2.dilate(thresh, kernal, iterations=1)

    straighted = deskew(dilate)

    cnts = cv2.findContours(straighted, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    cnts = sorted(cnts, key=lambda x: cv2.boundingRect(x)[0])
    for c in cnts:
        x, y, w, h = cv2.boundingRect(c)
        if h > 200 and w > 20:
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)
    return


def extract_text_from_image(image):
    try:
        # Use pytesseract with page segmentation mode (psm) to improve OCR accuracy
        # text = pytesseract.image_to_string(preprocessed_image, config='--psm 1').split('\n')
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return {"error": str(e)}


def post_ocr_process(text):
    lines = text.split("\n\n")
    print(lines)


@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file and allowed_file(file.filename):
            # Save the file to the upload folder
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            img = cv2.imread(file_path)

            preprocess(img)
            text = extract_text_from_image(img)
            # print(text)
            post_ocr_process(text)
            # return {"message": "File uploaded successfully", "data": info, "text": text}, 200
            return {"message": "File uploaded successfully", "text": text}, 200
        else:
            return jsonify({"error": "Invalid file type"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
