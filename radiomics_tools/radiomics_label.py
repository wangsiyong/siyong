import os
import csv
import SimpleITK as sitk
import traceback
from radiomics import featureextractor, getFeatureClasses, setVerbosity
from collections import OrderedDict

class radiomicsFromLabel(object):
    def resample_sitkImage(self,sitkImage, newSpacing):
        if sitkImage == None: return None
        oldSize = sitkImage.GetSize()
        oldSpacing = sitkImage.GetSpacing()
        newSize = (int(oldSize[0]*oldSpacing[0]/newSpacing[0]), \
                int(oldSize[1]*oldSpacing[1]/newSpacing[1]), \
                int(oldSize[2]*oldSpacing[2]/newSpacing[2]))
        transform = sitk.Transform()
        return sitk.Resample(sitkImage, newSize, transform, sitk.sitkLinear, sitkImage.GetOrigin(), \
                            newSpacing, sitkImage.GetDirection(), 0, sitkImage.GetPixelID())

    def resampleITKLabel(self, image, reference):
        resampler = sitk.ResampleImageFilter()
        resampler.SetInterpolator(sitk.sitkNearestNeighbor)
        resampler.SetReferenceImage(reference)
        return resampler.Execute(image)

    def prepareLabelsFromLabelmap(self, labelmapNode, grayscaleImage, labelsDict):
        # combinedLabelImage = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(labelmapNode.GetName()))
        combinedLabelImage = sitk.ReadImage(labelmapNode)
        # newSpacing = sitk.ReadImage(grayscaleImage).GetSpacing()
        newSpacing = grayscaleImage.GetSpacing()
        resampledLabelImage = self.resampleITKLabel(combinedLabelImage, grayscaleImage)
        # adjustedLabelImage = self.resample_sitkImage(resampledLabelImage,(spacing[0]/2, spacing[1]/2, spacing[2]/2))
        ls = sitk.LabelStatisticsImageFilter()
        ls.Execute(resampledLabelImage,resampledLabelImage)
        th = sitk.BinaryThresholdImageFilter()
        th.SetInsideValue(1)
        th.SetOutsideValue(0)

        for l in ls.GetLabels()[1:]:
            th.SetUpperThreshold(l)
            th.SetLowerThreshold(l)
            labelsDict[labelmapNode] = th.Execute(combinedLabelImage)
        return labelsDict

    def calculateFeatures( self,grayscaleImage, labelImage, featureClasses, settings, enabledImageTypes):
        # type: (Simple ITK image object, Simple ITK image object, list, dict, dict) -> dict
        """
        Calculate a single feature on the input MRML volume nodes
        """
        print('Calculating features for %s', featureClasses)
        print('Instantiating the extractor')
        extractor = featureextractor.RadiomicsFeaturesExtractor(**settings)
        extractor.disableAllFeatures()
        extractor.enableAllInputImages()
        for feature in featureClasses:
            extractor.enableFeatureClassByName(feature)
        # extractor.disableAllImageTypes()
        # for imageType in enabledImageTypes:
            # extractor.enableImageTypeByName(imageType, customArgs=enabledImageTypes[imageType])
        print('Starting feature calculation')
        featureValues = {}
        try:
            featureValues = extractor.execute(grayscaleImage, labelImage)
        except:
            print('pyradiomics feature extractor failed')
        #   traceback.print_exc()
        print('Features calculated')
        return featureValues

    def run(self,image, label, featureClasses, settings, enabledImageTypes,csvFile):
        """
        Run the actual algorithm
        """
        print('Processing started')
        import time
        startTime = time.time()
        # grayscaleImage = sitk.ReadImage(sitkUtils.GetSlicerITKReadWriteAddress(imageNode.GetName()))
        grayscaleImage = sitk.ReadImage(image)
        #sitkUtils.PushToSlicer(label, labelNode.GetName(), overwrite=True, compositeView=2)
        labelsDict = {}
        if label:
            print("label={}".format(label))
            labelsDict = self.prepareLabelsFromLabelmap(label, grayscaleImage, labelsDict)
        # if segmentationNode:
        #   labelsDict = self.prepareLabelsFromSegmentation(segmentationNode, grayscaleImage, labelsDict)

        #self.featureValues = extractor.execute(grayscaleImage, labelImage, images, **kwargs)
        featuresDict = {}
        for l in labelsDict.keys():
            print("Calculating features for "+l)
            try:
                featuresDict[l] = self.calculateFeatures(grayscaleImage,
                                                    labelsDict[l],
                                                    featureClasses,
                                                    settings,
                                                    enabledImageTypes)
            except:
                print('calculateFeatures() failed')
                traceback.print_exc()
        self.saveFeatures2CSVFile(featuresDict,csvFile)
        print("Completed")
        endtime = time.time()
        print("totalTime={}".format(endtime-startTime))
        # return featuresDict

    def saveFeatures2CSVFile(self,featuresDict,csvFile):
        features = featuresDict
        if not features:
            return
        _csv = csvFile
        sortedLabel = sorted(features.keys())
        print("sortedLabel={}".format(sortedLabel))
        sortedFeature = OrderedDict()
        for i in sorted(features[sortedLabel[0]].keys()):
            # print("i={}".format(i))
            sortedFeature[i] = features[sortedLabel[0]][i]

        with open(_csv, 'wb') as csvfile:
            writer = csv.writer(csvfile)
            header = ['', '']
            for i in sortedLabel:
                header.append('Nodule {}'.format(i))
            writer.writerow(header)
            for title, values in sortedFeature.items():
                row = [features[i][title] for i in sortedLabel]
                row.insert(0, title)
                writer.writerow(row)

if __name__ == "__main__":
    # from multiprocessing import Process
    radiomics = radiomicsFromLabel()
    currentFilePath = r"E:\hospitalResults\SHHD\nii\results\liti_niis"
    settings = {}
    settings['binWidth'] = 25
    settings['symmetricalGLCM'] = True   #self.symmetricalGLCMCheckBox.checked
    featureClasses = ['firstorder', "glcm", "shape", "glrlm", "glszm"]
    enabledImageTypes = {"Original": {}, "Wavelet": {}}
    niiFileList = [x for x in os.listdir(currentFilePath) if os.path.isfile(os.path.join(currentFilePath, x)) and os.path.splitext(x)[1]=='.nii' and "label" not in x]
    for niiFile in niiFileList:
        print("niiFile={}".format(niiFile))
        name, _ = os.path.splitext(niiFile)
        labelFile = name + "-label"
        labelImgFile = os.path.join(currentFilePath, labelFile)
        niiImgFile = os.path.join(currentFilePath, niiFile)
        csvFile = os.path.join(currentFilePath, name+"_radiomics.csv")
        if os.path.exists(csvFile):
            continue
        radiomics.run(niiImgFile, labelImgFile, featureClasses, settings, enabledImageTypes, csvFile)
