# -*- coding: utf-8 -*-
"""
    Program: discoveryRadiomics

    A python scripts for the interface between sigmaLU and Pyradiomics
    1) to convert the sigmaLU nodule json files into mask file in nii format
    2) to convert forming Pyradiomics output into json file

    www.12sigma.cn

    file name: jsonradiomics.py
    date of creation: 2017-06-28
    date of modification: 2018-03-12
    Author: Chunbo Liu (cbliu@12sigma.com)
    purpose:
        to generate radiomics features from input json and nii file using pyradiomics
        package
"""
import os
import sys
import csv
import re
import json
import argparse
from collections import OrderedDict
import numpy, ijson, six
import SimpleITK as sitk
from radiomics import firstorder, glcm, glrlm, glszm, shape, imageoperations, _version
# from sigma.base import get_current_config

print(_version.get_versions()['version'])
# ------------------------------------------------------------------------------
# resampling the sitkImages with origin aligned
def resample_sitkImage(sitkImage, newSpacing):
    """
    :param sitkImage:
    :param newSpacing:
    :return:
    """
    if sitkImage == None: return None

    oldSize = sitkImage.GetSize()
    oldSpacing = sitkImage.GetSpacing()
    newSize = (int(oldSize[0]*oldSpacing[0]/newSpacing[0]), \
               int(oldSize[1]*oldSpacing[1]/newSpacing[1]), \
              int(oldSize[2]*oldSpacing[2]/newSpacing[2]))
    transform = sitk.Transform()
    return sitk.Resample(sitkImage, newSize, transform, sitk.sitkLinear, sitkImage.GetOrigin(), \
                         newSpacing, sitkImage.GetDirection(), 0, sitkImage.GetPixelID())

def calculateRadiomicsFromJson(niiFile, jsonFile):
    # moduleConfig = get_current_config()
    # processing nii
    sitkImageParent = sitk.ReadImage(niiFile)
    direction = sitkImageParent.GetDirection()
    origin = sitkImageParent.GetOrigin()
    spacing = sitkImageParent.GetSpacing()
    # processing json
    f = open(jsonFile)
    p = ijson.parse(f)
    nodules = {}
    label = ''
    for prefix, _, value in p:
        if re.match('Nodules.item\d+.Label', prefix) or prefix == 'Nodules.item.Label':
            label = value
            nodules[label] = {}
            nodules[label]['label'] = value
            nodules[label]['sliceMask'] = ''
        if re.match('Nodules.item\d+.mask.xBegin', prefix) or prefix == 'Nodules.item.mask.xBegin':
            nodules[label]['xBegin'] = float(value)
        if re.match('Nodules.item\d+.mask.yBegin', prefix) or prefix == 'Nodules.item.mask.yBegin':
            nodules[label]['yBegin'] = float(value)
        if re.match('Nodules.item\d+.mask.zBegin', prefix) or prefix == 'Nodules.item.mask.zBegin':
            nodules[label]['zBegin'] = float(value)
        if re.match('Nodules.item\d+.DimInPixelX', prefix) or prefix == 'Nodules.item.DimInPixelX':
            nodules[label]['DimInPixelX'] =int(float(value))
        if re.match('Nodules.item\d+.DimInPixelY', prefix) or prefix == 'Nodules.item.DimInPixelY':
            nodules[label]['DimInPixelY'] = int(float(value))
        if re.match('Nodules.item\d+.DimInPixelZ', prefix) or prefix == 'Nodules.item.DimInPixelZ':
            nodules[label]['DimInPixelZ'] = int(float(value))
        if re.match('Nodules.item\d+.mask.sliceMask.item\d+', prefix) or prefix == 'Nodules.item.mask.sliceMask.item':
            nodules[label]['sliceMask'] += value
    # working on radiomics calculation
    features = {}
    kwargs = {'binWidth': 64,
              'interpolator': sitk.sitkBSpline,
              'resampledPixelSpacing': None}
    for noduleLabel in nodules:
        if 'DimInPixelX' not in nodules[noduleLabel]:
            continue
        bbox_dim = (nodules[noduleLabel]['DimInPixelX'], nodules[noduleLabel]['DimInPixelY'], \
                   nodules[noduleLabel]['DimInPixelZ'])
        bbox_ori = (nodules[noduleLabel]['xBegin'], nodules[noduleLabel]['yBegin'], \
                   nodules[noduleLabel]['zBegin'])

        sitkMask = sitk.Image(bbox_dim[0], bbox_dim[1], bbox_dim[2], sitk.sitkUInt8)
        sitkMask.SetSpacing(spacing)
        sitkMask.SetOrigin(bbox_ori)
        sitkMask.SetDirection(direction)

        for z in range(bbox_dim[2]):
            for y in range(bbox_dim[1]):
                for x in range(bbox_dim[0]):
                    idx = z * bbox_dim[1] * bbox_dim[0]  + y * bbox_dim[0] + x
                    v = int(nodules[noduleLabel]['sliceMask'][idx])
                    sitkMask.SetPixel(x, y, z, v)
        ori_matrix = (int(direction[0] * (bbox_ori[0] - origin[0]) / spacing[0]), \
                      int(direction[4] * (bbox_ori[1] - origin[1]) / spacing[1]), \
                      int(direction[8] * (bbox_ori[2] - origin[2]) / spacing[2]))

        sitkMask = resample_sitkImage(sitkMask, (spacing[0]/2, spacing[1]/2, spacing[2]/2))

        sitkImage = sitk.RegionOfInterest(sitkImageParent, sitkMask.GetSize(), ori_matrix)
        sitkImage.SetSpacing(spacing)
        sitkImage.SetOrigin(bbox_ori)
        sitkImage.SetDirection(direction)

        features[noduleLabel] = {}

        firstOrderFeatures = firstorder.RadiomicsFirstOrder(sitkImage, sitkMask, **kwargs)
        firstOrderFeatures.enableAllFeatures()
        firstOrderFeatures.calculateFeatures()
        firstOrderResult = features[noduleLabel].setdefault('firstorder', {})
        for (key, val) in six.iteritems(firstOrderFeatures.featureValues):
            firstOrderResult[key] = val

        shapeFeatures = shape.RadiomicsShape(sitkImage, sitkMask, **kwargs)
        shapeFeatures.enableAllFeatures()
        shapeFeatures.calculateFeatures()
        shapeResult = features[noduleLabel].setdefault('shape', {})
        for (key, val) in six.iteritems(shapeFeatures.featureValues):
            shapeResult[key] = val

        glcmFeatures = glcm.RadiomicsGLCM(sitkImage, sitkMask, **kwargs)
        glcmFeatures.enableAllFeatures()
        glcmFeatures.calculateFeatures()
        glcmResult = features[noduleLabel].setdefault('glcm', {})
        for (key, val) in six.iteritems(glcmFeatures.featureValues):
            glcmResult[key] = val

        glrlmFeatures = glrlm.RadiomicsGLRLM(sitkImage, sitkMask, **kwargs)
        glrlmFeatures.enableAllFeatures()
        glrlmFeatures.calculateFeatures()
        glrlmResult = features[noduleLabel].setdefault('glrlm', {})
        for (key, val) in six.iteritems(glrlmFeatures.featureValues):
            glrlmResult[key] = val

        glszmFeatures = glszm.RadiomicsGLSZM(sitkImage, sitkMask, **kwargs)
        glszmFeatures.enableAllFeatures()
        glszmFeatures.calculateFeatures()
        glszmResult = features[noduleLabel].setdefault('glszm', {})
        for (key, val) in six.iteritems(glszmFeatures.featureValues):
            glszmResult[key] = val

        if False:
            sigmaValues = numpy.arange(5., 0., -.5)[::1]
            for logImage, imageTypeName, inputKwargs in imageoperations.getLoGImage(sitkImage, sitkMask, sigma=sigmaValues):
                logFirstorderFeatures = firstorder.RadiomicsFirstOrder(logImage, sitkMask, **inputKwargs)
                logShapeFeatures=shape.RadiomicsShape(logImage, sitkMask, **inputKwargs)
                logGlcmFeatures=glcm.RadiomicsGLCM(logImage, sitkMask, **inputKwargs)
                logGlrlmFeatures=glrlm.RadiomicsGLRLM(logImage, sitkMask, **inputKwargs)
                logGlszmFeatures=glszm.RadiomicsGLSZM(logImage, sitkMask, **inputKwargs)
                logFirstorderFeatures.enableAllFeatures()
                logFirstorderFeatures.calculateFeatures()
                logShapeFeatures.enableAllFeatures()
                logShapeFeatures.calculateFeatures()
                logGlcmFeatures.enableAllFeatures()
                logGlcmFeatures.calculateFeatures()
                logGlrlmFeatures.enableAllFeatures()
                logGlrlmFeatures.calculateFeatures()
                logGlszmFeatures.enableAllFeatures()
                logGlszmFeatures.calculateFeatures()
                logFirstOrderResult = features[noduleLabel].setdefault('logFirstOrder', {})
                for (key, val) in six.iteritems(logFirstorderFeatures.featureValues):
                    logFirstOrderResult[key] = val
                logShapeResult = features[noduleLabel].setdefault('logShape', {})
                for (key, val) in six.iteritems(logShapeFeatures.featureValues):
                    logShapeResult[key] = val
                logGlcmResult = features[noduleLabel].setdefault('logGlcm', {})
                for (key, val) in six.iteritems(logGlcmFeatures.featureValues):
                    logGlcmResult[key] = val
                logGlrlmResult = features[noduleLabel].setdefault('logGlrlm', {})
                for (key, val) in six.iteritems(logGlrlmFeatures.featureValues):
                    logGlrlmResult[key] = val
                logGlszmResult = features[noduleLabel].setdefault('logGlszm', {})
                for (key, val) in six.iteritems(logGlszmFeatures.featureValues):
                    logGlszmResult[key] = val

        if False:
            for decompositionImage, decompositionName, inputKwargs in imageoperations.getWaveletImage(sitkImage, sitkMask):
                waveletFirstOrderFeatures = firstorder.RadiomicsFirstOrder(decompositionImage, sitkMask, **inputKwargs)
                waveShapeFeatures=shape.RadiomicsShape(decompositionImage, sitkMask, **inputKwargs)
                waveGlcmFeatures=glcm.RadiomicsGLCM(decompositionImage, sitkMask, **inputKwargs)
                waveGlrlmFeatures=glrlm.RadiomicsGLRLM(decompositionImage, sitkMask, **inputKwargs)
                waveGlszmFeatures=glszm.RadiomicsGLSZM(decompositionImage, sitkMask, **inputKwargs)

                waveletFirstOrderFeatures.enableAllFeatures()
                waveletFirstOrderFeatures.calculateFeatures()
                waveShapeFeatures.enableAllFeatures()
                waveShapeFeatures.calculateFeatures()
                waveGlcmFeatures.enableAllFeatures()
                waveGlcmFeatures.calculateFeatures()
                waveGlrlmFeatures.enableAllFeatures()
                waveGlrlmFeatures.calculateFeatures()
                waveGlszmFeatures.enableAllFeatures()
                waveGlszmFeatures.calculateFeatures()

                waveFirstOrderResult = features[noduleLabel].setdefault('waveFirstOrder', {})
                for (key, val) in six.iteritems(waveletFirstOrderFeatures.featureValues):
                    waveFirstOrderResult[key] = val
                waveShapeResult = features[noduleLabel].setdefault('waveShape', {})
                for (key, val) in six.iteritems(waveShapeFeatures.featureValues):
                    waveShapeResult[key] = val
                waveGlcmResult = features[noduleLabel].setdefault('waveGlcm', {})
                for (key, val) in six.iteritems(waveGlcmFeatures.featureValues):
                    waveGlcmResult[key]=val
                waveGlrlmResult = features[noduleLabel].setdefault('waveGlrlm', {})
                for (key, val) in six.iteritems(waveGlrlmFeatures.featureValues):
                    waveGlrlmResult[key]=val
                waveGlszmResult = features[noduleLabel].setdefault('waveGlszm', {})
                for (key, val) in six.iteritems(waveGlszmFeatures.featureValues):
                    waveGlszmResult[key] = val
    return features

def run(nii, jsf, src=None, dst=None):
    features = calculateRadiomicsFromJson(nii, jsf)
    if not features:
        return
    sortedFeature_Json = OrderedDict()
    for key,val in features.items():
        sortedFeature_Json[key]={}
        for subKey,subVal in val.items():
            for k,v in subVal.items():
                newKey = subKey+"_"+k
                sortedFeature_Json[key][newKey] = v

    _json = jsf
    if src and dst:
        _json = _json.replace(src.strip('/\\'), dst)
    _json = _json.replace('.json', '_radiomics.json')
    with open(_json,"w") as f:
        json.dump(sortedFeature_Json,f,indent=4,sort_keys=True)
    

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(
        description='to calculate the radiomics features from input json and nii files.')
    parser.add_argument('--nii', help='input nii file')
    parser.add_argument('--json', help='input json file')
    args = parser.parse_args()

    if os.path.exists(args.nii) and os.path.exists(args.json):
        # features = calculateRadiomicsFromJson(args.nii, args.json)
        run(args.nii,args.json)
        # fjson = open(args.json.replace('.json', '_radiomics.json'), 'w')
        # featuresFinal = {k:(features[k]) for k in sorted(features.keys())}
        # json.dump(features, fjson, indent=4, sort_keys=True)
        print('radiomics calculation done!')
    # else:
    #     print('please input the correct nii and its json file for radiomics calculation.')
    # currentFilePath = r"D:\tasks\issued"
    # niiFilePath = sys.argv[1]#r"F:\20180312\previous"
    # jsonFilePath = sys.argv[2]

    # run(niiFilePath,jsonFilePath)
    
    # niiFileList=[x for x in os.listdir(currentFilePath) if os.path.isfile(os.path.join(currentFilePath,x)) and os.path.splitext(x)[1]=='.nii']
    # for niiFile in niiFileList:
    #     niiFileName=os.path.splitext(niiFile)[0]
    #     jsonFile=niiFileName+".json"
    #     csvFile=niiFileName+"_CAD_DVD_radiomics.csv"
    #     print(niiFile,"---Start---")
    #     if not os.path.exists(os.path.join(currentFilePath,jsonFile)):
    #         try:
    #             run(os.path.join(currentFilePath,niiFile),os.path.join(currentFilePath,jsonFile))
    #         except RuntimeError as e:
    #             pass
        #         print(niiFile,"---Failed---",e)
        #         niiFile.replace('.nii', '.nii.issued')
        #         # os.rename(os.path.join(currentFilePath,niiFile),os.path.join(currentFilePath,niiFile+".issued"))
        #     else:
        #         print(niiFile,"---Done---")
        # else:
        #     print(niiFile,"Already existed!")