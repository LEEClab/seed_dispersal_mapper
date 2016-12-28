#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 Seed Dispersal Mapper v. 1.0
 
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Milton C. Ribeiro - mcr@rc.unesp.br
 
 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 This script runs in GRASS GIS 7.0.X environment.
 Usage: python seed_dispersal_mapper_v1_0.py
 
 The Seed Dispersal Mapper uses a raster map of habitat/forest area to predict the chance
 of seed deposition in the matrix  (or, alternatively, in specific land use classes such as pasture), 
 as a result of the process of animal-mediated seed dispersal of the plants present inside habitat patches.
 The model assumes that, in large patches, fauna is more abundant and there are animal
 taxa that can carry seeds farther in the matrix (long seed dispersers); 
 on the other hand, in small patches there are few long seed disepersers and fauna is less abundant.
 
 The model work as following:
 - First, the input habitat area map is divided in size classes; classes are defined by the user;
 - Second, for each patch size class, a map of chance of seed rain is generated, given parameters
   of abundance and mobility of animal in each size class, also defined by the user;
 - Third, a method of summaryzing the chance of seed deposition for each pixel in the map is used;
   it may be the maximum, minimum, mean, median, or another summary statistics 
   of the seed deposition maps for each size class.
 - Finally, a map of matrices (such as pasture) is used as a mask where we are interested in looking
   at the seed rain pattern.
"""
#---------------------------------------------------------------------------------------

# Import modules
import grass.script as grass
from datetime import datetime
import os, sys

#----------------------------------------------------------------------------------
# Parameters

# Users must change these parameters

# Folder for output maps (they are generated inside GRASS GIS Location and also exported in this folder)
dirfolder = r"/home/leecb/Documentos/UNESP/artigos/manuscrito_Niebuhr_etal_2017_seed_rain_chance_N&C/Validation/results_model_landscape"

# Patch size map (name inside GRASS GIS)
patch_map = 'floresta_1985_bin_dila_0m_orig_clump_mata_limpa_AreaHA'

# Pasture matrix map (name inside GRASS GIS), if applicable
# If absent (= ''), seed dispersal is generated for all matrices only
pasture_map = 'pasto_1985_bin' # or ''

# Patch size limits - for defining the patch size classes
# In this case, the classes are: 1. 0-10ha; 2. 10-25ha; 3. 25-50ha; 4. 50-250ha; 5. >250ha
scales_limit = [10,25,50,250]

# Kind of function to generate seed rain curves
# weibull or logistic
function = 'weibull'

# Curve parameters
# For Weibull [A_s, lambda_s]
#parms_weib = [[30,130], [70,170], [120,220], [200,290], [350,350]] # difference abundances at x = 0
parms_weib = [[130,130], [170,170], [220,220], [290,290], [350,350]] # equal abundances (1) at x = 0
parms = parms_weib

# Other functions
# For logistic [K, r_s, a_s]
#parms = [[1, 30, 150], [1, 40, 200], [1, 60, 300], [1, 80, 400], [1, 100, 500]]

# Option: export all maps (including the auxiliary maps generated along the process)? True or False
export_all_maps = False

# Option: export final seed dispersal maps (or keep them only inside GRASS GIS)? True or False
export_final_maps = True

# Command to generate the maps
# DO NOT CHANGE THIS
InstanceMain = Main(patch_map, scales_limit, parms, dirfolder, pasture_map)
InstanceMain.Run()

#----------------------------------------------------------------------------------
# Class Seed Deposition Curves
#
# Here the curve parameters are initialized, the patch area maps are separated into classes,
#   the curves are applied to it and summary seed dispersal maps are generated
class Seed_Deposition_Curves(object):
    
    def __init__(self, patch_map, scales_limit, function, parms, dirfolder, pasture_map, export_all_maps = False, export_final_maps = True):
        '''
        Initializing parameters inside the class
        '''
        
        self.patch_map = patch_map
        self.scales_limit = scales_limit
        self.function = function
        self.parms = parms
        self.raster_max = 100000000 # not working
        self.map_names_size = []
        self.map_names_seed_rain = []
        self.errorLog = ''
        self.dirfolder = dirfolder
        self.pasture_map = pasture_map
        self.export_all_maps = export_all_maps
        self.export_final_maps = export_final_maps
        self.format_export = "GTiff"
        self.txt = ''
        
        # If it is not possible to access the output folder, shows a warning message and exits
        try:
            os.chdir(self.dirfolder)
        except:
            print "Problems in typing output directory: " + self.dirfolder
            sys.exit(101)
        
    def Logfile(self):
        '''
        Writing errors in the log file
        
        This function creates log files with error in the execution, so that it is possible
        to promptly fix it 
        '''
        
        os.chdir(self.dirfolder)
        self.time = datetime.now() # INSTANCE
        self.day = self.time.day
        self.month = self.time.month
        self.year = self.time.year
        self.hour = self.time.hour # GET end hour
        self.minute = self.time.minute #GET end minuts
        self.second = self.time.second #GET
        self.txt=open("__Log_"+`self.day`+`self.minute`+`self.second`+".txt",w)
        self.txt.write("Error-----------"+self.errorLog+'\n')
        self.txt.close()
        
    def export_map(self, input_map):
        '''
        This function export maps in GTiff or PNG formats
        '''
        
        os.chdir(self.dirfolder)
        
        form = self.format_export
        
        if form == 'GTiff':
            sufix = '.tif'
            
            grass.run_command('r.out.gdal', input=input_map, output=input_map+sufix, format = form, overwrite = True, quiet = True, nodata = -99)
        elif form == 'PNG':
            sufix = '.png'
            
            grass.run_command('r.out.png', input=input_map, output=input_map+sufix, compression=9)
        else:
            print 'Export_map form should be GTiff or PNG!'
            self.errorLog = 'Problems in the function export_map; export_map form should be Gtiff or PNG!'
            self.Logfile # chamand a funcao log
            self.errorLog = ''
            return
        
    def get_maxim_value(self):
        '''
        Getting the maximum patch size of the map
        
        This is not working for some reason, but the overall script is working
        '''
        
        stats = grass.parse_command('r.univar', map=self.patch_map, flags='g')
        self.raster_max = int(stats['max'])
    
    def generate_size_class_maps(self, skip_map_creation = False):
        '''
        Generating size class maps
        
        This function uses a patch size map to separate it into different maps, 
        corresponding to the patch size classes defined by the user
        
        Besides generating the maps, the function also produces a list with the maps' names, 
        called "self.map_names_size", which is used in other function to generate 
        seed deposition mapsp
        
        There is the option of skiping map creation and only producing the list of map names
        (in case there was an error and the patch size class maps were already created)
        '''
        
        print 'Generating size class maps'
        n_classes = len(self.scales_limit)+1
        
        # Generating maps of different fragment size classes
        self.map_names_size = []
        for i in range(n_classes):
            
            if i == 0:
                minval = 0
            else:
                minval = self.scales_limit[i-1]
            
            if i == len(self.scales_limit):
                self.get_maxim_value
                maxval = self.raster_max
                maxname = 'Inf'
            else:
                maxval = self.scales_limit[i]
                maxname = `maxval`
                       
            grass.run_command('g.region', rast=self.patch_map)
            map_size = self.patch_map+'_class_'+`minval`+'_'+maxname
            
            print("map ==================> %s" % map_size)
            self.map_names_size.append(map_size)
            
            if skip_map_creation == False:
                expression = map_size+' = if('+self.patch_map+' > '+`minval`+' && '+self.patch_map+' <= '+`maxval`+','+self.patch_map+', null())'
                
                try:
                    grass.mapcalc(expression, overwrite = True, quiet = True)
                except:
                    self.errorLog = "Problems in the function generate_size_class_maps "+ expression
                    self.Logfile # chamand a funcao log
                    self.errorLog = ''
                
            if self.export_all_maps:
                self.export_map(map_size)
    

    def generate_distance_seed_deposition_maps(self, function = 'weibull', skip_dist_map_creation = False, skip_seed_map_creation = False):
        '''
        Generating maps of distance and applying the curves
         
        This function creates maps of distance (in meters) from patch edges, for each patch size class -
        besed on the names of the patch size class maps listed in the function "generate_size_class_maps",
        and applies the correspondent seed dispersal curve. The outputs are seed dispersal maps 
        for all matrices, for each patch size class
        
        There are options for skipping the creation of distance and seed dispersal maps, in case they were
        already generated (at least for some classes)
        '''        
        
        # Checking if the list map_names_size exists; if not, create it
        if len(self.map_names_size) == 0:
            n_classes = len(self.scales_limit)+1
            
            self.map_names_size = []
            for i in range(n_classes):
                        
                if i == 0:
                    minval = 0
                else:
                    minval = self.scales_limit[i-1]
                
                if i == len(self.scales_limit):
                    self.get_maxim_value
                    maxval = self.raster_max
                    maxname = 'Inf'
                else:   
                    maxval = self.scales_limit[i]
                    maxname = `maxval`
                               
                map_size = self.patch_map+'_class_'+`minval`+'_'+maxname
                self.map_names_size.append(map_size)
        
        # Beginning to generate seed rain maps
        cont = 0
        self.map_names_seed_rain = []
        for i in self.map_names_size:
            
            # test if the paramater array size is correct; otherwise, warn it!
        
            if skip_dist_map_creation == False:
                
                print "runing distance map: %s " %i
                
                expression2 = i+'_hab = if('+i+' > 0, 1, null())'
                try:
                    grass.mapcalc(expression2, overwrite = True, quiet = True)
                except:   
                    self.errorLog = "Problems in the function generate_distance_seed_deposition_maps "+ expression2
                    self.Logfile # chamand a funcao log
                    self.errorLog = ''
                     
                try:
                    grass.run_command('r.grow.distance', input=i+'_hab', distance=i+'_hab_dist', overwrite = True)
                except:
                    self.errorLog = "Problems in the function generate_distance_seed_deposition_maps r.grow "+ i+'_hab_dist'
                    self.Logfile # chamand a funcao log
                    self.errorLog = '' 
                    
                expression3 = i+'_hab_dist_pos = if('+i+'_hab_dist > 0, '+i+'_hab_dist, null())'    
                try:
                    grass.mapcalc(expression3, overwrite = True, quiet = True)
                except:   
                    self.errorLog = "Problems in the function generate_distance_seed_deposition_maps "+ expression3
                    self.Logfile # chamand a funcao log
                    self.errorLog = ''             
                 
            if skip_seed_map_creation == False:
            
                print 'running seed dispersal curves: %s' %i  
                    
                par = parms[cont]
                
                if function == 'weibull' or function == 'Weibull':
                    
                    # par recebe um lista com dois valores para a equacao 
                    # vale a pena testar no inicio - se nao for uma lista com dois argumentos, reclamar
                    A_t = float(par[0])
                    lambda_t = float(par[1])
                    print str(par[0])+' '+str(par[1])
                    
                    d=i+'_hab_dist_pos'
                    map_seed = i+'_seed_rain_weibull'
                    self.map_names_seed_rain.append(map_seed)
                    expression4 = map_seed+' = '+`A_t`+' * (1/'+`lambda_t`+') * exp(-('+d+'/'+`lambda_t`+'))'
                    print expression4
                
                elif function == 'logistic' or function == 'Logistic':
                    
                    # par recebe um lista com tres valores para a equacao 
                    # vale a pena testar no inicio - se nao for uma lista com tres argumentos, reclamar
                    K = float(par[0])
                    r_t = float(par[1])
                    a_t = float(par[2])
                    print str(par[0])+' '+str(par[1])+' '+str(par[2])
                    
                    d=i+'_hab_dist_pos'
                    map_seed = i+'_seed_rain_logistic'
                    self.map_names_seed_rain.append(map_seed)
                    expression4 = map_seed+' = '+`K`+'/ (1 + exp(1.0/'+`r_t`+' * ('+d+' - '+`a_t`+')))'
                    print expression4                    
                
                try:
                    grass.mapcalc(expression4, overwrite = True, quiet = True)
                except:
                    self.errorLog = "Problems in the function generate_distance_seed_deposition_maps mapcalc dispersal curves "+ i+'_hab_dist'
                    self.Logfile # chamand a funcao log
                    self.errorLog = ''
                
            if self.export_all_maps:
                self.export_map(map_seed)
                                
            cont += 1
            
    
    def create_summary_maps(self, method = 'maximum', function = 'weibull', skip_matrix_map_creation = False): # adicionei aqui o argumento method; se quisermos podemos fazer de outros jeitos
        '''
        Genereting summary map
        
        Besed on the seed dispersal maps for each patch size class, this function calculates 
        summary statistics and produces seed deposition maps for either one or both of the matrices:
        (i) all matrices (unless the option skip_matrix_map_creation is True) and (ii) only pasture
        (or another land use used as mask)
        '''
        
        # Method options: average, count, median, mode, minimum, min_raster, maximum, max_raster, stddev, range, sum, variance, diversity
        if skip_matrix_map_creation == False:
            name_rseries = 'map_seed_rain_' + method + '_' + function
            
            try:
                print ("genereting summary raster, method: "+method)
                grass.run_command('r.series', input=self.map_names_seed_rain, output=name_rseries, overwrite=True, method=method, flags='n')
            except:
                self.errorLog = "Problems in the function create_summary_maps r.series  "
                self.Logfile # chamand a funcao log
                self.errorLog = ''        

        if self.pasture_map != '':
            name_mapcalc = name_rseries + '_by_pasture'
            expression5 = name_mapcalc+" = if("+self.pasture_map+" > 0, "+name_rseries+", null())"
            
            try:
                print ("genereting summary raster in pasture, method: "+method)
                grass.mapcalc(expression5, overwrite = True, quiet = True)
            except:
                self.errorLog = "Problems in the function create_summary_maps " +expression5
                self.Logfile # chamand a funcao log
                self.errorLog = ''
            
        if self.export_final_maps:
            if skip_matrix_map_creation == False:
                self.export_map(name_rseries)
            if self.pasture_map != '':
                self.export_map(name_mapcalc) 
        
    def remove_aux_maps(self):
        """
        Removing auxiliary maps generated along the simulation
        
        This part was not implemented yet, since we prefered to maintain all maps
        while developing the tool
        """
        pass

#----------------------------------------------------------------------------------
# Class Main
#
# Here we set the simulation parameters and organize the simulation steps to be run
# Change here if you want to simulate only part of the process
class Main(Seed_Deposition_Curves):
    
    def __init__(self, patch_map, scales_limit, parms, dirfolder, pasture_map, export_all_maps, export_final_maps):
        '''
        Initializes simulation parameters
        '''
        Seed_Deposition_Curves.__init__(self, patch_map, scales_limit, function, parms, dirfolder, pasture_map, export_all_maps, export_final_maps)
        
    def Run(self):
        '''
        Run simulation steps
        '''
        
        # Generating maps of patch size classes
        Seed_Deposition_Curves.generate_size_class_maps(self, skip_map_creation=True)
        
        # Generating distance and seed deposition maps for each size class
        Seed_Deposition_Curves.generate_distance_seed_deposition_maps(self, function = function, skip_dist_map_creation=True, skip_seed_map_creation=False)
        
        # Creating summary seed dispersal map
        Seed_Deposition_Curves.create_summary_maps(self, method="maximum", function = function)
        # Other examples
        #Seed_Deposition_Curves.create_summary_maps(self, method="sum")
        #Seed_Deposition_Curves.create_summary_maps(self, method="average")
