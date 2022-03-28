#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from lxml import etree
import time
import argparse
import sys
import uuid



if __name__ == "__main__":
    # -------------start of program-------------------#

    print("\n****** EsriShapefile2infraGML Converter *******\n")
    argparser = argparse.ArgumentParser(description='******* EsriShapefile2infraGML Converter *******')
    argparser.add_argument('-i', '--inputFilename', help='EsriShapefile dataset filename', required=False)
    argparser.add_argument('-o', '--outputFilename', help='infraGML dataset filename', required=False)
    args = vars(argparser.parse_args())

    inputFileName = args['inputFilename']
    if inputFileName:
        inputFile = str(inputFileName)
        print("Esri Shapefile input file: ", inputFile)
    else:
        print("Error: Enter the Esri Shapefile dataset!! ")
        sys.exit()

    outputFileName = args['outputFilename']
    if outputFileName:
        outputFile = str(outputFileName)
    #    print ("InfraGML output file: ", outputFile)
    else:
        print("Error: Enter the infraGML filename!! ")
        sys.exit()

    start = time.time()
    citygml2infragml(inputFile, outputFile)
    end = time.time()
    print("Time taken for InfraGML generation: ", end - start, " sec")
