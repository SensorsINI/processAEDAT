import cv2
import numpy as np
from matplotlib import pyplot as plt

#open image
img = cv2.imread('messi.jpg',0)
#get image properties
height, width = img.shape
num_pixels_noise = 1000
#apply canny edge detector and blur the image
edges = cv2.Canny(img,80,180)
edges = cv2.GaussianBlur(edges,(5,5),0)
#apply a 2d kernel
kernel = np.ones((5,5),np.float32)/25
dst = cv2.filter2D(edges,-1,kernel)
#normalize
edges = edges / np.std(edges)
edges = (edges-np.min(edges))/(np.max(edges)-np.min(edges))
edges = (np.round(edges*254.0))
edges[np.where(edges >= 200)] = np.random.randint(100,150)
edges[np.where(edges <= 30)] = np.random.randint(100,150)
#add noise
for i in range(num_pixels_noise):
    edges[np.random.randint(0,height)][np.random.randint(0,width)] = np.random.randint(100,150)
#plot
plt.subplot(121),plt.imshow(img,cmap = 'gray')
plt.title('Original Image'), plt.xticks([]), plt.yticks([])
plt.subplot(122),plt.imshow(edges,cmap = 'gray')
plt.title('Processed Image'), plt.xticks([]), plt.yticks([])
plt.show()

