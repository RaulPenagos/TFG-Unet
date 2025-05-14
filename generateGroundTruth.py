"""
Software to simualte the Ground Truth image for several cilindrical
phantoms facing the beam, given a certain PROTECT Configuration.json file.

Runs on Linux and Windows.

@author Raul Penagos
@date   Tue Abr 15th, 2025
"""

import json, os, sys, optparse 
import json
from PIL import Image, ImageDraw
import re # regex for extracting index from the name of ConfigFiles.json


class Phantom():
    """
    Phantom Class, englobes all data for a given cilindrical phantom.
    Also, assigns its density and opacity acording to the biological
    material normalized to 1.
    """
    def __init__(self, name: str, material: str, xPos, yPos, zPos, xDir, yDir, zDir, radius, zsize):
        """
        Generator of the class
        Args:
            Takes all data from the phantom Configuration
        """
        self.name = name 
        self.material = material 
        self.xPos = xPos 
        self.yPos = yPos 
        self.zPos = zPos 
        self.xDir = xDir 
        self.yDir = yDir 
        self.zDir = zDir 
        self.radius = radius 
        self.zsize = zsize
        self.density = None
        self.opacity = None
        self.set_density()

    def set_density(self):
        """
        Sets density and opacity values based off the material, based of NIST database:
        
        Opacity = density * z

            NIST in Geant4:
        "G4_LUNG_ICRP"           ≈ 0.296 g/cm³
        "G4_BRAIN_ICRP"          ≈ 1.04 g/cm³
        "G4_ADIPOSE_TISSUE_ICRP" ≈ 0.92 g/cm³
        "G4_COMPACT_BONE_ICRU"   ≈ 1.85 – 2.00 g/cm³
        """
        materials = ['lung', 'brain', 'fat', 'bone']
        density = [0.296, 1.04, 0.92, 1.90]  # g/cm^3
        opacity = [d * self.zsize for d in density]  # g/cm^2

        # Normalize to 1
        index = [i for i, mat in enumerate(materials) if self.material == mat][0]
        self.density = [density[index]/max(density)][0]
        self.opacity = [opacity[index]/max(opacity)][0]



class PhantomScenario():
    """
    PhantomScenario class stores the 'Phantoms' for a given Configuration.json file
    and is capable of creating a Ground Truth image.
    """
    def __init__(self, configuration_file: str, output_dir: str, params: dict):
        """
        Generator of the class.
        Args:
            configuration_file: Name of the input Configuration.json file 
            output_dir: Name of the output directory to save generated images
            params: contains the parameters for the images
                size = width and height size in cm
                px = number of pixels
        """
        
        self.configuration_file = configuration_file
        self.output_dir = output_dir

        # Stores the Phantom objects
        self.phantoms = []

        # Gets the number label for the image
        self.label = self.extract_index(configuration_file)

        # Store the image parameters
        self.params = params
    
    def extract_index(self, name: str):
        """
        Returns the integer number contained in name if any. Else, 0.
        Input:
            name: string where a number wants to be finded
        """
        match = re.search(r'\d+', name)
        if match:
            return(match.group())
        else:
            return(0) 
        
    def ReadPhantomsFromConfiguration(self):
        """
        Reads the Configuration.json file, it saves up the Phantoms
        that are defined inside with all their characteristics.
        Creating Phantom objects and populating self.phantoms
        """

        if not os.path.exists(self.configuration_file):
            print(f"Error: file '{self.configuration_file}' does not exist.")
            return []

        try:
            with open(self.configuration_file, "r") as f:
                data = json.load(f)
            
        except json.JSONDecodeError as e:
            print(f"Error while decoding JSON file: {e}")
            return []

        if "Phantoms" not in data:
            print(f"Phantoms is not defined in the file  '{self.configuration_file}'")
            return []

        # Extract Phantom data from the file
        phantoms_data = data["Phantoms"]

        for i, p in enumerate(phantoms_data):
            try:
                phantom = Phantom(
                    name = p["name"],
                    material = p["material"],
                    xPos = p["xPos"],
                    yPos = p["yPos"],
                    zPos = p["zPos"],
                    xDir = p["xDir"],
                    yDir = p["yDir"],
                    zDir = p["zDir"],
                    radius = p["radius"],
                    zsize = p["zsize"]
                )
                self.phantoms.append(phantom)
            except KeyError as e:
                print(f"Missing key in phantom #{i+1}: {e}")
                sys.exit()
            except Exception as e:
                print(f"Error while creating phantom #{i+1}: {e}")
                sys.exit()

    def GenerateImage(self):
        """
        Generates and saves a GroundTruth image with the phantoms.
        The image is scaled to reality, and the center of the image is the (0,0)
        Change of reference system is made.
        Uses PIL library to create a circle for each cilindrical phantom.
        """
        # Extracts parameters from the dictionary
        size = self.params['size_cm']
        n = self.params['px']

        center_x, center_y = n / 2, n / 2

        # Create image mode: L (8-bit pixels, grayscale) (0=black, 255=white)
        img = Image.new('L', (n, n), (255) )

        # Create a draw object
        draw = ImageDraw.Draw(img)

        # Loops phantoms and draws them
        for p in self.phantoms:
            circle = [p.xPos, p.yPos, p.radius]  # (x, y, radius)
            circle = [i * n / size for i in circle]  # make picture up to pixel real scale

            opacity = int(255 - p.opacity * 255)  # Compute density on 0-255 scale, denser --> darker

            x_0, y_0, r = circle

            # Compute coordinates of the center of circles
            x = center_x + x_0
            y = center_y + y_0

            bbox = [x - r, y - r, x + r, y + r]  # Bounding box of the circle
            draw.ellipse(bbox, fill = opacity)   # 0 = black 
                                                 # 255 = white
        # Show or save the result
        try:
            img.save(self.output_dir + '/Phantoms_' + str(self.label) + '.png')
            # img.show()
        except:
            print('Output directory does not exist')
            sys.exit()


class FolderAnalyzer():
    """
    Takes all the files from a given directory, several ConfigurationFiles_i.json,
    And generates an image acording to the Phantom geometry.

    """
    def __init__(self, input_dir, output_dir, params):
        """
        Generator of the class.
        Args:
            input_dir   Directory containing ConfigFiles.json
            output_dir  Goal directory for .png images
            params: contains the parameters for the images
                size = width and height size in cm
                px = number of pixels
        """
        self.input_dir = input_dir 
        self.output_dir = output_dir
        self.params = params

    def makeAnalysis(self):
        """
        Runs over all .json files in input_dir and generates Ground Truth images
        in the output_dir.
        """
        # Get all files in the input directory
        conf_files = os.listdir(self.input_dir)

        # Loop over all json files
        for file in conf_files:
            if '.json' in file:
                scene = PhantomScenario(self.input_dir + '/' + file, self.output_dir, self.params)
                scene.ReadPhantomsFromConfiguration()
                scene.GenerateImage()


if __name__ == '__main__': 
    """
    Main function. User can introduce the input and output directories using the options -i & -o
    Will make Gorund Truth images in the output dir for all the Configuration.json files found.
    """
    parser = optparse.OptionParser(usage='usage: %prog [options] path', version='%prog 1.0')                           
    parser.add_option('-i', '--input', action='store', type='string', dest='inputDir', default='.', help='Input directory, contains config.json files')
    parser.add_option('-o', '--output', action='store', type='string', dest='outputDir', default='./output', help='Output directory for .png')
    (opts, args) = parser.parse_args()


    image_params = {'size_cm': 25,'px': 512}
    loader = FolderAnalyzer(opts.inputDir, opts.outputDir, image_params)
    # test = FolderAnalyzer('./ConfigurationFiles', './GroundTruth' )
    loader.makeAnalysis()


    
