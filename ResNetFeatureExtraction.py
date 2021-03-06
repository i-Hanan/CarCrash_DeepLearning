from keras.preprocessing import image
from keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import preprocess_input
import numpy as np
import shutil
from sklearn.cluster import KMeans
import csv
import glob
import sys

model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
model.summary()

video_type = sys.argv[1]
base_path = "/home/aman/Desktop/Mini-Project/RefinedKeyFrames/" + video_type
print("Processing in ResNetFeatureExtraction.py- Processing for Folder: ", base_path)
# base_path = '/home/aman/Desktop/Mini-Project/data/test/Accident'


def get_features(img_path):
    # load image setting the image size to 224 x 224
    img = image.load_img(img_path, target_size=(224, 224))
    # convert image to numpy array
    img_data = image.img_to_array(img)
    # the image is now in an array of shape (3, 224, 224)
    # need to expand it to (1, 3, 224, 224) as it's expecting a list
    img_data = np.expand_dims(img_data, axis=0)
    img_data = preprocess_input(img_data)

    resnet50_feature = model.predict(img_data)

    # print(resnet50_feature.shape)
    # print(type(resnet50_feature))
    # print(resnet50_feature.ndim)
    # print(resnet50_feature)

    resnet50_feature = resnet50_feature.tolist()
    resnet50_feature = [j for sub in resnet50_feature for j in sub]
    return resnet50_feature


if __name__ == '__main__':

    allKeyFramesFeat = []
    video_label = []

    counter = 0
    dir_path = base_path + '/*.jpeg'

    for img_path in glob.iglob(dir_path):
        counter += 1

    print("Processing in ResNetFeatureExtraction.py- Total Refined KeyFrames in this Folder is: ", counter)
    if counter <= 5:
        print("This must be greater than 5; So exiting!")
        shutil.rmtree("RefinedKeyFrames")
        sys.exit(0)

    for img_path in glob.iglob(dir_path):

        print("Processing in ResNetFeatureExtraction.py- Processing for RefinedKeyFrame: ", img_path)
        feat = get_features(img_path)
        allKeyFramesFeat.append(feat)

    if video_type == 'Accident':
        video_label.append(1)
    else:
        video_label.append(0)

    print("Processing in ResNetFeatureExtraction.py- Size of allKeyFramesFeat vector: ", len(allKeyFramesFeat))
    shutil.rmtree("RefinedKeyFrames")

    # Clustering
    kmeans = KMeans(n_clusters=5, random_state=0).fit(allKeyFramesFeat)
    print("Processing in ResNetFeatureExtraction.py- Cluster labels: ", kmeans.labels_)

    vectorForVideo = []
    for eachCentroid in kmeans.cluster_centers_:
        vectorForVideo.extend(eachCentroid)

    print("Processing in ResNetFeatureExtraction.py- BOVW size: ", len(vectorForVideo))

    # Making feature_vector.csv
    with open("feature_vector.csv", 'a') as outfile:
        writer = csv.writer(outfile, delimiter=' ')
        writer.writerow(vectorForVideo)

    # Making label_vector.csv
    with open("label_vector.csv", 'a') as outfile:
        writer = csv.writer(outfile, delimiter=' ')
        writer.writerow(video_label)
