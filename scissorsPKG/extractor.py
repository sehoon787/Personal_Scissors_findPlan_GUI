from cv2 import cvtColor, COLOR_RGB2BGR, INTER_LINEAR, INTER_AREA, resize
from cv2 import threshold, COLOR_RGB2GRAY, THRESH_BINARY
from cv2 import morphologyEx, getStructuringElement, MORPH_RECT, MORPH_ERODE
from cv2 import findContours, RETR_LIST, CHAIN_APPROX_SIMPLE, boundingRect, contourArea
from cv2 import imshow, waitKey, destroyAllWindows

from numpy import array as np_array
from pandas import DataFrame
from pdf2image import convert_from_path
from PIL import Image

def convert_jpg(format, path, poppler_path):
    if format=="pdf":
        images = convert_from_path(path, fmt='jpg',
                                   dpi=600, first_page=0, last_page=1,
                                   poppler_path=poppler_path)
        numpy_image = np_array(images[0])
    elif format=="png":
        images = Image.open(path).convert('RGB')
        numpy_image = np_array(images)

    img = cvtColor(numpy_image, COLOR_RGB2BGR)

    return img

def preprocessing(img_ori, target_w=1280, target_h=690, show=False):
    h, w, _ = img_ori.shape
    if h*w<target_h*target_w:       # up sampling
        img_ori = resize(img_ori, dsize=(target_w, target_h), interpolation=INTER_LINEAR)
    elif h*w>=target_h*target_w:     # down sampling
        img_ori = resize(img_ori, dsize=(target_w, target_h), interpolation=INTER_AREA)

    gray = cvtColor(img_ori, COLOR_RGB2GRAY)
    # Get rid of JPG artifacts
    gray = threshold(gray, 128, 255, THRESH_BINARY)[1]

    # Create structuring elements
    horizontal_size = 11
    vertical_size = 11
    horizontalStructure = getStructuringElement(MORPH_RECT, (horizontal_size, 1))
    verticalStructure = getStructuringElement(MORPH_RECT, (1, vertical_size))

    # Morphological opening
    mask1 = morphologyEx(gray, MORPH_ERODE, horizontalStructure)
    mask2 = morphologyEx(mask1, MORPH_ERODE, verticalStructure)

    if show:
        # Outputs
        imshow('mask1', mask1)
        imshow('mask2', mask2)
        waitKey(0)
        destroyAllWindows()

    return img_ori, mask2

def find_plan(img, mask, show=False):
    candidates_df = DataFrame(columns=['x', 'y', 'w', 'h', 'cx', 'cy', 'area'])

    min_h = 200
    max_h = 1100
    min_w = 200
    max_w = 1100

    contours, hierarchy = findContours(mask, RETR_LIST, CHAIN_APPROX_SIMPLE)

    try:
        for i, contour in enumerate(contours):
            [x, y, w, h] = boundingRect(contour)
            area = contourArea(contour)
            # measure Square size
            if (min_h < h < max_h) and (min_w < w < max_w) and ((min_h*min_w*1.8)<area):
                # 여백을 줄이기 위해 각 좌표에 추가 연산을 수행
                candidates_df = candidates_df.append({
                    'x': x+3,
                    'y': y+3,
                    'w': w-3,
                    'h': h-3,
                    'cx': x + (w / 2),
                    'cy': y + (h / 2),
                    'area': area}
                    , ignore_index=True)
                # img = cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 128), cv2.LINE_4)
        mins = candidates_df['area'].idxmin()
        coord = candidates_df.iloc[mins, :]

        result = img[int(coord['y']):int(coord['y']+coord['h']),
                 int(coord['x']):int(coord['x']+coord['w'])]

    except Exception as e:
        raise Exception("Can not find plan figure!")

    # cv2.imwrite("result/fig_"+name, result)

    if show:
        imshow('result', result)   # test
        waitKey(0)

    return result

# if __name__ == '__main__':
#     path = "data/"
#     name = "plan3.jpg"
#     img, mask = preprocessing(path=path+name, show=0)
#     find_plan(name, img, mask, show=1)
