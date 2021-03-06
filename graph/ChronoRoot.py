import os
import csv
import cv2

from .fileFunc import createResultFolder, loadPath, getROIandSeed
from .imageFunc import getCleanSeg, getCleanSke, savePlotImages, saveEmpty
from .graphFunc import createGraph, saveGraph, saveProps
from .trackFunc import graphInit, matchGraphs
from .rsmlFunc import createTree
from .graphPostProcess import trimGraph
from .dataWork import dataWork

def ChronoRootAnalyzer(conf):
    ext = "*" + conf["FileExt"]
    all_files = loadPath(conf['Path'], ext) 
    images = [file for file in all_files if 'mask' not in file]
       
    ext = "*" + conf["FileExt"]
    all_files = loadPath(conf['SegPath'], ext) 
    segFiles = [file for file in all_files if 'mask' in file]
    
    lim = conf['Limit'] 
    
    if lim!=0:
        images = images[:lim]
        segFiles = segFiles[:lim]
    
    bbox, seed = getROIandSeed(conf, images, segFiles)
    seed = list(seed[0])
    originalSeed = seed.copy()
    
    saveFolder, graphsPath, imagePath, rsmlPath = createResultFolder(conf)
    
    start = 0
    N = len(images)
    pfile = os.path.join(saveFolder, "Results.csv") # For CSV Saver
    
    with open(pfile, 'w+') as csv_file:
        csv_writer = csv.writer(csv_file)
        row0 = ['FileName', 'TimeStep','MainRootLength','LateralRootsLength','NumberOfLateralRoots','TotalLength']
        csv_writer.writerow(row0)
        
        for i in range(0, N):
            print('TimeStep', i+1, 'of', N)
            segFile = segFiles[i]
            seg, flag1 = getCleanSeg(segFile, bbox, originalSeed)
            
            original = cv2.imread(images[i])[bbox[0]:bbox[1],bbox[2]:bbox[3]]
            
            if flag1:
                ske, bnodes, enodes, flag2 = getCleanSke(seg)
                if flag2:
                    start = i
                    break
            
            image_name = images[i].replace(conf['Path'],'').replace('/','')
            saveProps(image_name, i, False, csv_writer, 0)
            saveEmpty(image_name, imagePath, original)
        
        print('Growth Begin')
        grafo, seed, ske2 = createGraph(ske.copy(), seed, enodes, bnodes)
        grafo, ske, ske2 = trimGraph(grafo, ske, ske2)
        
        grafo = graphInit(grafo)
           
        gPath = os.path.join(graphsPath, 'graph_%s.xml.gz' %i)
        saveGraph(grafo, gPath)
        
        rsmlTree, numberLR = createTree(conf, i, images, grafo, ske, ske2)
        
        rsml = os.path.join(rsmlPath, 'TimeStep-%s.rsml' %i)
        rsmlTree.write(open(rsml, 'w'), encoding='unicode')
        
        image_name = images[i].replace(conf['Path'],'').replace('/','')
        saveProps(image_name, i, grafo, csv_writer, numberLR)
        
        original = cv2.imread(images[i])[bbox[0]:bbox[1],bbox[2]:bbox[3]]
        savePlotImages(image_name, imagePath, original, seg, grafo, ske2)
        
        segErrorFlag = False #Previous time-step error
        trackCount = 0
        
        for i in range(start+1, N):
            print('TimeStep', i+1, 'of', N)
            errorFlag_ = False
            
            segFile = segFiles[i]
            seg, flag1 = getCleanSeg(segFile, bbox, originalSeed)
            
            if flag1:
                ske, bnodes, enodes, flag2 = getCleanSke(seg)
                if not flag2:
                    errorFlag_ = True
            else:
                errorFlag_ = True
            
            trackError = False
        
            if not errorFlag_:               
                grafo2, seed, ske2_ = createGraph(ske.copy(), seed, enodes, bnodes)
                grafo2, ske_, ske2_ = trimGraph(grafo2, ske.copy(), ske2_)
                
                if not segErrorFlag:
                    try:
                        grafo = matchGraphs(grafo, grafo2)
                        ske =  ske_.copy()
                        ske2 = ske2_.copy()
                    except:
                        trackError = True
                else:
                    grafo = graphInit(grafo2)
                    ske =  ske_.copy()
                    ske2 = ske2_.copy()
                    
            else:
                image_name = images[i].replace(conf['Path'],'').replace('/','')
                saveProps(image_name, i, False, csv_writer, 0)
                saveEmpty(image_name, imagePath, original)
            
            segErrorFlag = errorFlag_
            
            if not segErrorFlag and not trackError:           
                gPath = os.path.join(graphsPath, 'graph_%s.xml.gz' %i)
                saveGraph(grafo, gPath)
                
                rsmlTree, numberLR = createTree(conf, i, images, grafo, ske, ske2)
                rsml = os.path.join(rsmlPath, 'TimeStep-%s.rsml' %i)
                rsmlTree.write(open(rsml, 'w'), encoding='unicode')
                
                image_name = images[i].replace(conf['Path'],'').replace('/','')
                saveProps(image_name, i, grafo, csv_writer, numberLR)
                
                original = cv2.imread(images[i])[bbox[0]:bbox[1],bbox[2]:bbox[3]]
                savePlotImages(image_name, imagePath, original, seg, grafo, ske2)
        
            if trackError and trackCount > 5:
                print('Analysis ended early at timestep', i, 'of', N)
                break
            elif trackError:
                trackCount += 1
            else:
                trackCount = 0
    
    dataWork(conf, pfile, saveFolder)
