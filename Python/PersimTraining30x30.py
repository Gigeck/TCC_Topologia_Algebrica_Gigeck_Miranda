%load_ext_ext tensoboard
import itertools
import sklearn.metrics
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input,Dense,Conv2D,MaxPooling2D, Dropout, Flatten
from tensorflow.keras.utils import to_categorical
import os
import glob as glob
import matplotlib.pyplot as plt
import random
from dataclasses import dataclass
from PIL import Image
from sklearn.model_selection import train_test_split
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter)

@dataclass(frozen=True)
class DatasetConfig:
    NUM_CLASSES: int = 2
    IMG_HEIGHT: int  = 233
    IMG_WIDTH: int = 233
    NUM_CHANNELS: int = 3

@dataclass(frozen=True)
class TrainingConfig:
    EPOCHS: int = 101
    BATCH_SIZE: int = 25
    LEARNING_RATE: float = 0.001

def cnn_model(input_shape=(32,32,3)):
    model = Sequential()
    model.add(Input(shape=input_shape))

    # First layer 32 Filters MaxPool
    model.add(Conv2D(filters=32, kernel_size=3, padding='same', activation='relu'))
    model.add(Conv2D(filters=32, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.5))

    # Second Layers 64 filters maxpool
    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.5))

    # third layer 64 filters maxpool
    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.5))

    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(Conv2D(filters=64, kernel_size=3, padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(2,2)))
    model.add(Dropout(0.5))

    # flatten and classify
    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.25))
    model.add(Dense(2, activation='softmax'))

    return model

def plot_results(metrics,title=None,ylabel=None,ylim=None,metric_name=None, color=None):
    fig, ax = plt.subplots(figsize=(15,4))

    if not (isinstance(metric_name,list) or isinstance(matric_name,tuple)):
        metrics = [metrics,]
        matric_name = [metric_name,]

    for id, metric in enumerate(metrics):
        ax.plot(metric,color[id])

    plt.xlabel("Epoch")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xlim([0,TrainingConfig.EPOCHS-1])
    plt.ylim(ylim)
    #Tailor x-axis tick marks
    ax.xaxis.set_major_locator(MultipleLocator(5))
    ax.xaxis.set_major_formatter(FormatStrFormatter('%d'))
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    plt.grid(True)
    plt.legend(metric_name)
    #plt.show()
    plt.savefig(ylabel+'30X30.png')
    plt.close()

def main():
    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    #Loading data
    PATHAI="dataset2"+os.sep+"30x30"+os.sep+"AI_euclidMetric"+os.sep
    PATHREAL="dataset2"+os.sep+"30x30"+os.sep+"Real_euclidMetric"+os.sep
    listAI = sorted(glob.glob(PATHAI+"*.jpg"))
    listReal = sorted(glob.glob(PATHREAL+"*.jpg"))

    listAIjpg = [(Image.open(treco)) for treco in listAI]
    listAIcropped = []
    for img in listAIjpg:
        width , height = img.size
        chosen = min(width,height)
        crop = img.crop((0,0,chosen,chosen))
        listAIcropped.append(img)
    listAInpy = [np.array(treco.resize((256,256))) for treco in listAIcropped]
    for a in listAIjpg:
        a.close()

    listRealjpg = [(Image.open(treco)) for treco in listReal]
    listRealcropped = []
    for img in listRealjpg:
        width , height = img.size
        chosen = min(width,height)
        crop = img.crop((0,0,chosen,chosen))
        listRealcropped.append(crop)
    listRealnpy = [np.array(treco.resize((256,256))) for treco in listRealcropped]
    for a in listRealjpg:
        a.close()
    listAllnpy = np.array((listAInpy+listRealnpy))
    #creating classes
    listAIy = [1 for x in range(len(listAI))]
    listRealy = [0 for x in range(len(listReal))]
    listAlly = np.array(listAIy+listRealy)
    listAllyCat = to_categorical(listAlly)
    #random split, cuz stupid tensorflow first takes split then it shuffles
    x_train, x_test, y_train, y_test = train_test_split(listAllnpy, listAllyCat, test_size=0.3, random_state=SEED)

    #creating model
    myshape = listAllnpy[0].shape
    model = cnn_model(input_shape=myshape)

    model.compile(
        optimizer="rmsprop",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    hist = model.fit(
        x_train,
        y_train,
        batch_size=TrainingConfig.BATCH_SIZE,
        epochs=TrainingConfig.EPOCHS,
        verbose=1,
        validation_data= (x_test,y_test),
    )

    train_loss = hist.history["loss"]
    train_acc = hist.history["accuracy"]
    val_loss = hist.history["val_loss"]
    val_acc = hist.history["val_accuracy"]

    plot_results(
        [train_loss,val_loss],
        ylabel="loss",
        ylim = [0.0,5.0],
        metric_name=["train loss","val loss"],
        color=["g","b"],
    )

    plot_results(
        [train_acc,val_acc],
        ylabel="acc",
        ylim = [0.0,1.0],
        metric_name=["train acc","val acc"],
        color=["g","b"],
    )

    model.save("modelResize30x30.keras")


if __name__ == "__main__":
    main()
