import os
import glob
from PIL import Image

def main():
    otherExtensions = {'.jpg', '.jpeg', '.bmp', '.webp'}
    chosenExtension = '.png'
    pathAI = 'dataset'+os.sep+'AiArtData'+os.sep
    pathReal = 'dataset'+os.sep+'RealArt'+os.sep
    paths = [pathAI,pathReal]

    for ext in otherExtensions:
        print("Dealing with "+ext)
        for pat in paths:
            print("Dealing with "+pat)
            for infile in glob.glob(pat+'*'+ext):
                file, exten = os.path.splitext(infile)
                #print(infile)
                #print(file)
                #print(exten)
                #print(file+chosenExtension)
                #print(" ")
                img = Image.open(infile)
                img.save(file+chosenExtension)
                os.remove(infile)
    pass

if __name__=="__main__":
    main()