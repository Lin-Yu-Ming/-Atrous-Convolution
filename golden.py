# -*- coding: utf-8 -*-
"""數位ic_n.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dCnpFOo6Kur8TRkvRCxilmXuCpNeow7S
"""

# connect to your google drive
from google.colab import drive
drive.mount('/content/drive')

import os
os.chdir('/content/drive/MyDrive/數位ic')

from  matplotlib import pyplot as plt
import cv2
import numpy as np
import math
import tensorflow as tf
from tensorflow.keras import layers,models
import pandas as pd
import os


image = cv2.imread("1.jpg") 
image = image[:,:,::-1]
image_gray = cv2.imread("1.jpg",0)
image_resize = cv2.resize(image_gray, (64, 64), interpolation=cv2.INTER_NEAREST)
cv2.imwrite('image_resize.jpg', image_resize)



plt.figure(figsize=(10,20))
plt.subplot(1,3,1)
plt.imshow(image_gray,cmap='gray')
plt.title('image')

plt.subplot(1,3,2)
plt.imshow(image_gray,cmap='gray')
plt.title('gray')

plt.subplot(1,3,3)
plt.imshow(image_resize,cmap='gray')
plt.title('resize')
plt.show()

print('image shape: ', image.shape)
print('imagee_gray shape: ', image_gray.shape)
print('image_resize shape: ', image_resize.shape)

"""# Layer0

# padding
"""

def padding_img(img, p_size):
    return np.pad(img, pad_width=p_size, mode='edge')


padding_image= padding_img(image_resize, 2)  

plt.figure(figsize=(10,20))
plt.subplot(1,2,1)
plt.imshow(image_resize,cmap='gray')
plt.title('image_resize')
plt.subplot(1,2,2)
plt.imshow(padding_image,cmap='gray')
plt.title('padding_image')
print('image_resize shape: ', image_resize.shape)
print('image_padding shape: ',padding_image.shape)

#cnn.set_weights([custom_kernel, custom_bias])

#convoluted_image1 = cnn.predict(image_input)
#convoluted_image1 = convoluted_image1.squeeze()

#plt.imshow(convoluted_image1, cmap='gray')
#plt.show()
#print('convoluted_image1 shape: ', convoluted_image1.shape)

"""# convolution"""

def Convolution(imag, kernel, bias=0):
    k = kernel
    KernelSize = k.shape[0]
    padimg = padding_img(imag,(KernelSize-1)//2)
    rows, cols = padimg.shape
    output = np.zeros((rows-KernelSize+1, cols-KernelSize+1))


    for i in range(0,rows-KernelSize+1):
        for j in range(0,cols-KernelSize+1):
            output[i,j] = np.sum(np.multiply(padimg[i:i+KernelSize, j:j+KernelSize], k))

    output = output + bias

    return output


def relu(x):
    return np.maximum(0, x)

kernel = np.array([[-0.0625,0,-0.125,0,-0.0625],
          [0 ,0 ,0 ,0, 0] ,        
          [-0.25,0,1,0,-0.25],
          [0 ,0 ,0 ,0, 0],
          [-0.0625,0,-0.125,0,-0.0625]])

bias = -0.75

convolution_image_dilated = Convolution(image_resize,kernel,bias)
relu_image_dilated = relu(convolution_image_dilated)


plt.figure(figsize=(10,20))
plt.subplot(1,3,1)
plt.imshow(image_resize,cmap='gray')
plt.title('image_resize')
plt.subplot(1,3,2)
plt.imshow(convolution_image_dilated ,cmap='gray')
plt.title('convolution_image_dilated ')
plt.subplot(1,3,3)
plt.imshow(relu_image_dilated,cmap='gray')
plt.title('relu_image_dilated')
print('image_resize shape: ', image_resize.shape)
print('convolution_image_dilated: ',convolution_image_dilated.shape)
print('relu_image_dilated: ',relu_image_dilated.shape)

"""# Layer1

# MaxPooling
"""

def max_pooling(image, pool_size=(2, 2), stride=(2, 2)):
    height, width = image.shape
    pool_height, pool_width = pool_size
    stride_height, stride_width = stride
    
    output_height = (height - pool_height) // stride_height + 1
    output_width = (width - pool_width) // stride_width + 1
    
    output = np.zeros((output_height, output_width))
    
    for i in range(0, output_height):
        for j in range(0, output_width):
            y = i * stride_height
            x = j * stride_width
            output[i, j] = np.max(image[y:y+pool_height, x:x+pool_width])
    #output = np.round(output)
    output = np.ceil(output)
    return output

max_pooling_image=max_pooling(relu_image_dilated, pool_size=(2, 2), stride=(2, 2))


plt.subplot(1,2,1)
plt.imshow(relu_image_dilated,cmap='gray')
plt.title('relu_image_dilated')
plt.subplot(1,2,2)
plt.imshow(max_pooling_image,cmap='gray')
plt.title('max_pooling_image')

print('relu_image_dilated: ',relu_image_dilated.shape)
print('max_pooling_image: ',max_pooling_image.shape)

"""# pixel值(IEEE754 floating point into fixed point)"""

def float_to_fixed_point(num, integer_bits, fraction_bits):
    # Calculate the scaling factor
    scaling_factor = 2 ** fraction_bits

    # Multiply the number by the scaling factor to move the decimal point
    num_scaled = num * scaling_factor

    # Round the number to the nearest integer
    num_rounded = round(num_scaled)

    # Check if the number is within the allowed range
    max_integer = 2 ** (integer_bits - 1) - 1  # Subtract 1 bit for the sign
    min_integer = -2 ** (integer_bits - 1)
    if num_rounded > max_integer * scaling_factor or num_rounded < min_integer * scaling_factor:
        raise ValueError(f"The number {num} cannot be represented with {integer_bits} integer bits and {fraction_bits} fraction bits.")

    # Convert the rounded number to a binary string
    binary_str = format(num_rounded & ((1 << (integer_bits + fraction_bits)) - 1), f'0{integer_bits + fraction_bits}b')

    return binary_str
def print_image_pixels_fixed_point(img, integer_bits, fraction_bits):
   with open("output.txt", "w") as file:
    data_count = 0
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            fixed_point_binary = float_to_fixed_point(img[i, j], integer_bits, fraction_bits)
            pixel_str = f'{fixed_point_binary} //data{data_count}: {img[i, j]}' 
            print(pixel_str)
            file.write(pixel_str + "\n")
            data_count += 1

integer_bits = 9
fraction_bits = 4
#print_image_pixels_fixed_point(image_resize, integer_bits, fraction_bits)
#print_image_pixels_fixed_point(relu_image_dilated, integer_bits, fraction_bits)
print_image_pixels_fixed_point(max_pooling_image, integer_bits, fraction_bits)

"""# 驗證"""

def print_image_pixels(img):
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            binary_str = format(int(img[i, j]), 'b')
            print(f'Pixel({i},{j}): {img[i, j]}| Binary: {binary_str}')

print_image_pixels(image_resize)
