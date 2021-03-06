def dwtcoefftoarray(myim, wavelet, level, denoise, partial=False):
    ''' 
    This function collects all the coefficients of the DWT and converts them
    in a flat array which can be passed to the Deep Neural Network.
    
    Parameters:
        - myim = image opened with PIL.Image
        - wavelet = which wavelet to use
        - level = level of the wavelet decomposition
        - denoise = wheter to prior denoise the image or not, denoise should be set to "yes" or "no"
        - partial = True or False <-- let's you choose wheter to take only the second and third levels coeffiecients if level is 3, or the second, third and fourth levels coefficients if level is 4
    '''
    if denoise == 'yes':
        myimfl = img_as_float(myim)
        myim = denoise_wavelet(myimfl, method='BayesShrink', mode='soft', rescale_sigma='True')
    elif denoise == 'no':
        pass

    coeffs = pywt.wavedec2(myim, wavelet, level=level)

    infocoeffs = pywt.ravel_coeffs(coeffs)

    if partial == False:
        ''' 
        If partial is False I want to take all the coefficients obtained from the wavedec2 decomposition 
        '''
        coeffsarray = infocoeffs[0]

    if partial == True:
        ''' 
        If partial is True AND level is 3 I want to take the coefficients of 2nd and 3rd levels without the 1st level ones
        and without those related to the approximated image.
        If partial is True AND level is 4 I want to take the coefficients of 2nd, 3rd and 4th levels without the 1st level ones
        and without those related to the approximated image.
        '''
        secondlevelcoeffs = np.concatenate(( infocoeffs[0][infocoeffs[1][-2]['da']], infocoeffs[0][infocoeffs[1][-2]['ad']], 
                                            infocoeffs[0][infocoeffs[1][-2]['dd']] ))
        thirdlevelcoeffs = np.concatenate(( infocoeffs[0][infocoeffs[1][-3]['da']], infocoeffs[0][infocoeffs[1][-3]['ad']], 
                                            infocoeffs[0][infocoeffs[1][-3]['dd']] ))
        if level == 3:    
            coeffsarray = np.concatenate((secondlevelcoeffs, thirdlevelcoeffs))
        elif level == 4:
            fourthlevelcoeffs = np.concatenate(( infocoeffs[0][infocoeffs[1][-4]['da']], infocoeffs[0][infocoeffs[1][-4]['ad']], 
                                                infocoeffs[0][infocoeffs[1][-4]['dd']] ))
            coeffsarray = np.concatenate(( secondlevelcoeffs, thirdlevelcoeffs, fourthlevelcoeffs ))
        else:
            pass
    
    return coeffsarray


def dwtanalysis(myim, wavelet, level, denoise):
    ''' 
    This function decomposes the original image with a Discrete Wavelet Transformation
    using the desired wavelet family up to the fifth level. One can choose to denoise 
    the original image prior to the DWT decomposition. The coefficients matrices obtained from 
    the DWT are then masked keeping only those values which are greater than
    the standard deviation calculated over the matrix values. The image is then
    reconstructed using the new coefficients. 

    Parameters:
        - myim = image opened with PIL.Image
        - wavelet = which wavelet to use
        - level = level of the wavelet decomposition
        - denoise = wheter to prior denoise the image or not, denoise should be set to "yes" or "no" 
    '''
    if denoise == 'yes':
        myimfl = img_as_float(myim)
        myim = denoise_wavelet(myimfl, method='BayesShrink', mode='soft', rescale_sigma='True')
    elif denoise == 'no':
        pass

    if level == 2:
        cA, (cH2, cV2, cD2), (cH1, cV1, cD1) = pywt.wavedec2(myim, wavelet, level=level)
    elif level == 3:
        cA, (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1) = pywt.wavedec2(myim, wavelet, level=level)
    elif level == 4:
        cA, (cH4, cV4, cD4), (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1) = pywt.wavedec2(myim, wavelet, level=level)
    elif level == 5:
        cA, (cH5, cV5, cD5), (cH4, cV4, cD4), (cH3, cV3, cD3), (cH2, cV2, cD2), (cH1, cV1, cD1) = pywt.wavedec2(myim, wavelet, level=level)
    else:
        pass

    ''' 
    Now, I get the standard deviation for each matrix (image and coefficients).
    The std will act as a treshold so that if abs(value) < 0. --> value = 0.
                                            elif abs(value) > 0. --> value = value
    '''
    ncA = np.zeros_like(cA) # I won't need the approximated image anymore, I only need to modify the n'th level coefficient.

    std10 = np.std(cH1)
    std11 = np.std(cV1)
    std12 = np.std(cD1)

    ncH1 = pywt.threshold(cH1, std10, mode = 'hard', substitute = 0.)
    ncV1 = pywt.threshold(cV1, std11, mode = 'hard', substitute = 0.)
    ncD1 = pywt.threshold(cD1, std12, mode = 'hard', substitute = 0.)

    std20 = np.std(cH2)
    std21 = np.std(cV2)
    std22 = np.std(cD2)

    ncH2 = pywt.threshold(cH2, std20, mode = 'hard', substitute = 0.)
    ncV2 = pywt.threshold(cV2, std21, mode = 'hard', substitute = 0.)
    ncD2 = pywt.threshold(cD2, std22, mode = 'hard', substitute = 0.)

    if level == 3 or level == 4:
        std30 = np.std(cH3)
        std31 = np.std(cV3)
        std32 = np.std(cD3)

        ncH3 = pywt.threshold(cH3, std30, mode = 'hard', substitute = 0.)
        ncV3 = pywt.threshold(cV3, std31, mode = 'hard', substitute = 0.)
        ncD3 = pywt.threshold(cD3, std32, mode = 'hard', substitute = 0.)
    else:
        pass

    if level == 4 or level == 5:
        std40 = np.std(cH4)
        std41 = np.std(cV4)
        std42 = np.std(cD4)

        ncH4 = pywt.threshold(cH4, std40, mode = 'hard', substitute = 0.)
        ncV4 = pywt.threshold(cV4, std41, mode = 'hard', substitute = 0.)
        ncD4 = pywt.threshold(cD4, std42, mode = 'hard', substitute = 0.)
    else:
        pass

    if level == 5:
        std50 = np.std(cH5)
        std51 = np.std(cV5)
        std52 = np.std(cD5)

        ncH5 = pywt.threshold(cH5, std50, mode = 'hard', substitute = 0.)
        ncV5 = pywt.threshold(cV5, std51, mode = 'hard', substitute = 0.)
        ncD5 = pywt.threshold(cD5, std52, mode = 'hard', substitute = 0.)
    else:
        pass

    ''' 
    To let things be more readable I define new_coeff,
    this is just so that waverec2 (the function needed to reconstruct
    the image from a set of given coefficient) can do what it does.
    '''
    if level == 2:
        new_coeff = ncA, (ncH2, ncV2, ncD2), (ncH1, ncV1, ncD1) 
    elif level == 3:
        new_coeff = ncA, (ncH3, ncV3, ncD3), (ncH2, ncV2, ncD2), (ncH1, ncV1, ncD1) 
    elif level == 4:
        new_coeff = ncA, (ncH4, ncV4, ncD4), (ncH3, ncV3, ncD3), (ncH2, ncV2, ncD2), (ncH1, ncV1, ncD1)     
    elif level == 5:
        new_coeff = ncA, (ncH5, ncV5, ncD5), (ncH4, ncV4, ncD4), (ncH3, ncV3, ncD3), (ncH2, ncV2, ncD2), (ncH1, ncV1, ncD1) 

    ''' Here the image is reconstructed using the new coefficients.
    '''
    mynewim = pywt.waverec2(new_coeff, wavelet)
    mynewim = pywt.threshold(mynewim, 0., mode = 'greater', substitute = 0.)

    return myim, mynewim


def savecomparison(myim, mynewim, save_path, title_of_image, name_of_image):
    ''' 
    This function saves an image showing the comparison between the original image and the
    reconstructed one in which details are highly enhanced.
    
    Parameters:
        - myim = the original image opened with PIL.Image
        - mynewim = the image obtained with the DWT analysis
        - save_path = path to which the image will be saved
        - title_of_image = title of the comparison image
        - name_of_image = name with which the image will be saved 
    '''
    dpi = 96

    plt.figure(figsize=(1200/dpi, 600/dpi), dpi=dpi)
    plt.subplot(1,2,1)
    plt.title("Normale")
    plt.imshow(myim, cmap='gray')
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,      
        top=False, 
        left=False,
        right=False,        
        labelbottom=False,
        labelleft=False)
    plt.colorbar(orientation='horizontal')

    plt.subplot(1,2,2)
    plt.title(title_of_image)
    plt.imshow(mynewim, cmap='gray')
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,      
        top=False, 
        left=False,
        right=False,        
        labelbottom=False,
        labelleft=False)
    plt.colorbar(orientation='horizontal')

    final_path = os.path.join(save_path, name_of_image)

    plt.savefig(final_path, bbox_inches='tight')



from PIL import Image
from skimage.restoration import denoise_wavelet
from skimage import img_as_float
import matplotlib.pyplot as plt
import numpy as np
import pywt
import os
import glob
import argparse

if __name__ == "__main__":
    # Arguments
    parser = argparse.ArgumentParser(description="Tool to process images with wavelets")
    parser.add_argument('-path', help='You need to give me the path pointing to the folder containing CMEPDA-Project', type=str)
    parser.add_argument('-wavelet', help='Which Wavelet Family do you want to use?', type=str)
    parser.add_argument('-level', help='Which level of decomposition do you desire?', type=int, choices=[2,3,4,5])
    parser.add_argument('-denoise', help='Would you like to denoise your images before processing them?', type=str, choices=['yes','no'])
    parser.add_argument('-savepath', help='Where would you save the processed images?', type=str)
    args = parser.parse_args()

    cmepdapath = args.path
    level = args.level
    denoise = args.denoise
    wavelet = args.wavelet
    save_path = args.savepath
    
    # Getting images folder path to open the image
    general_path = os.path.join(cmepdapath, 'CMEPDA-Project', 'Images')

    # Starting from the general_path folder, which contains Train and Test folders, 
    # these loops cycle every image contained in 0 and 1 subfolders in order to process
    # them with the dwtanalysis() function. Then the images are saved in the desired folder.

    for folder in ['Train', 'Test']: 
        # 0 folder's images are those without microcalcifications.
        # 1 folder's images are those containing microcalcifications.    
        zero_images_path = os.path.join(general_path, folder, '0')
        one_images_path = os.path.join(general_path, folder, '1')

        # Here I retrieve all the images in the .pgm format.
        zero_images_names = glob.glob(os.path.join(zero_images_path, '*.pgm'))
        one_images_names = glob.glob(os.path.join(one_images_path, '*.pgm'))

        
        for i, image_path in enumerate(zero_images_names):
            im = Image.open(image_path)
            myim, mynewim = dwtanalysis(im, wavelet, level=level, denoise=denoise)
                
            final_save_path = os.path.join(save_path, 'Processed Images', f'{wavelet}_{level}levels_{denoise}denoise', f'{folder}_png', '0')
            if not os.path.exists(final_save_path):
                os.makedirs(final_save_path)
            final_path = os.path.join(final_save_path, f'{i}.png')

            mynewim = mynewim.astype(np.uint8)
            mynewim = Image.fromarray(mynewim)
            mynewim.save(final_path)

        for i, image_path in enumerate(one_images_names):
            im = Image.open(image_path)
            myim, mynewim = dwtanalysis(im, wavelet, level=level, denoise=denoise)
                
            final_save_path = os.path.join(save_path, 'Processed Images', f'{wavelet}_{level}levels_{denoise}denoise', f'{folder}_png', '1')
            if not os.path.exists(final_save_path):
                os.makedirs(final_save_path)
            final_path = os.path.join(final_save_path, f'{i}.png')

            mynewim = mynewim.astype(np.uint8)
            mynewim = Image.fromarray(mynewim)
            mynewim.save(final_path)