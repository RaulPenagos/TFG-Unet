"""
Given two directories with .root files with particle tracks, and Geant4 configuration.json files
with cilindrical phantoms,
generates POCA histogram and Ground Truth Images

Needed libraries:
    numpy, matplotlib, ROOT, pillow (PIL)

Runs on Linux and Windows.

@author Raul Penagos
@date   Wed May 14th, 2025
"""
from generateGroundTruth import *
from makePOCA import *


if __name__ == '__main__': 
    """
    Main function, user can introduce the input and output directories using the options -i & -o
    """

    parser = optparse.OptionParser(usage='usage: %prog [options] path', version='%prog 1.0')                           
    parser.add_option('-p', '--input_POCA', action='store', type='string', dest='inputDir_POCA', default='./input', help='Input directory, contains TrackReconstructionFiles.root files')
    parser.add_option('-P', '--output_POCA', action='store', type='string', dest='outputDir_POCA', default='./output', help='Output directory for .png Poca graphs')
    parser.add_option('-t', '--input_truth', action='store', type='string', dest='inputDir_truth', default='./input', help='Input directory, contains Configuration.json files')
    parser.add_option('-T', '--output_truth', action='store', type='string', dest='outputDir_truth', default='./output', help='Output directory for .png Phantoms images')
    (opts, args) = parser.parse_args()

    # TO TRAIN A U-net: must use same pixels and cm_size!!

    # Set the parameters for the POCA histograms
    histogram_params = {'px': 512, 'width_cm': 25, 'height_cm': 25, 'bins': 150}

    # Set the parameters for the Ground Truth image
    image_params = {'px': 512, 'size_cm': 25}


    # Run the analysis
    use_generateGroundTruth(opts.inputDir_truth, opts.outputDir_truth, image_params)
    use_makePOCA(opts.inputDir_POCA, opts.outputDir_POCA, histogram_params)

