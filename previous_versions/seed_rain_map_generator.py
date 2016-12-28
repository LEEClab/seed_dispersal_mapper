#!/c/Python25 python
#---------------------------------------------------------------------------------------
"""
 Seed Deposition map generator
 
 John W. Ribeiro - jw.ribeiro.rc@gmail.com
 Bernardo B. S. Niebuhr - bernardo_brandaum@yahoo.com.br
 Milton C. Ribeiro - mcr@rc.unesp.br
 
 Laboratorio de Ecologia Espacial e Conservacao
 Universidade Estadual Paulista - UNESP
 Rio Claro - SP - Brasil
 
 This script runs in GRASS GIS 7 environment.
 Usage: python seed_rain_map_generator.py
 
 The Seed Deposition map generator uses a raster map of habitat/forest area to predict the chance
 of seed deposition in the matrix  (or, alternatively, in specific land use classes), 
 as a result of the process of animal-mediated seed dispersal of the plants present inside habitat patches.
 The model assumes that, in large patches, fauna is more abundant and there are animal
 taxa that can carry seeds farther in the matrix (long seed dispersers); 
 on the other hand, in small patches there are few long seed disepersers and fauna is less abundant.
 
 The model work as following:
 - First, the input habitat area map is divided in size classes; classes are defined by the user;
 - Second, for each patch size class, a map of chance of seed rain is generated, given parameters
   of abundance and mobility of animal in each size class, also defined by the user;
 - Third, a method of summaryzing the chance of seed deposition for each pixel in the map is used;
   it may be the maximum, minimum, mean, or median of the seed deposition maps for each size class.
 - Finally, a map of matrices (such as pasture) is used as amask where we are interested in looking
   at the seed rain pattern.
"""
#---------------------------------------------------------------------------------------

import grass.script as grass
from datetime import datetime
import os, sys

class Seed_Deposition_Curves(object):
    
    def __init__(self, mapapatch, escalas_limite, parms_weib, dirfolder, pasturemap):
        '''
        Initializing parameters
        '''
        
        self.mapapatch = mapapatch
        self.escalas_limite = escalas_limite
        self.parms_weib = parms_weib
        self.raster_max = 10000000
        self.map_names_size = []
        self.map_names_seed_rain = []
        self.errorLog = ''
        self.dirfolder = dirfolder
        self.pasturemap = pasturemap 
        self.export_maps = True
        self.format_export = "GTiff"
        self.txt=''
        
        # exept pra ja tentar entrar na pasta aqui - esta dando alguns problemas, precisa ter o r"..." no nome do dir
        try:
            os.chdir(self.dirfolder)
        except:
            print "Problems in typing output directory: " + self.dirfolder
            sys.exit(101)
        
    def Logfile(self):
        '''
        This function creates log files with error in the execution, so that it is possible
        to promptly fix it 
        '''
        
        os.chdir(self.dirfolder)
        self.time = datetime.now() # INSTANCE
        self.day = self.time.day
        self.month = self.time.month
        self.year = self.time.year
        self.hour = self.time.hour # GET end hour
        self.minuts = self.time.minute #GET end minuts
        self.second = self.time.second #GET
        #self.txt=open("__Log_"+`day`+`minuts`+`second`+".txt",w) #### John, eh isso mesmo? essa linha tinha sumido
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
        elif form == 'PNG':
            sufix = '.png'
        else:
            print 'Export_map form should be Gtiff or PNG !'
            self.errorLog = 'Problems in the function export_map; export_map form should be Gtiff or PNG !'
            self.Logfile # chamand a funcao log
            self.errorLog = ''
            return
        
        grass.run_command('r.out.gdal', input=input_map, output=input_map+sufix, format = form, overwrite = True, quiet = True)#, nodata = -99)
        
    def get_maxim_value(self):
        '''
        Getting the maximum patch size of the map 
        '''
        
        stats = grass.parse_command('r.univar', map=self.mapapatch, flags='g')
        self.raster_max = int(stats['max'])
    
    def generate_size_class_maps(self):
        '''
        Generating size class maps
        '''
        
        print 'Generating size class maps'
        n_classes = len(self.escalas_limite)+1
        
        # Generating maps of different fragment size classes
        self.map_names_size = []
        for i in range(n_classes):
            
            if i == 0:
                minval = 0
            else:
                minval = self.escalas_limite[i-1]
            
            if i == len(self.escalas_limite):
                self.get_maxim_value
                maxval = self.raster_max
                maxname = 'Inf'
            else:
                maxval = self.escalas_limite[i]
                maxname = `maxval`
                       
            grass.run_command('g.region', rast=self.mapapatch)
            map_size = self.mapapatch+'_class_'+`minval`+'_'+maxname
            
            print("map ==================> %s" % map_size)
            self.map_names_size.append(map_size)
            expression = map_size+' = if('+self.mapapatch+' > '+`minval`+' && '+self.mapapatch+' <= '+`maxval`+','+self.mapapatch+', null())'
            
            try:
                grass.mapcalc(expression, overwrite = True, quiet = True)
            except:
                self.errorLog = "Problems in the function generate_size_class_maps "+ expression
                self.Logfile # chamand a funcao log
                self.errorLog = ''
                
            if self.export_maps:
                self.export_map(map_size)
                #pass
    

    def generate_distance_seed_deposition_maps(self):
        '''
        Generating maps of distance and applying the curves
        '''        
        
        # Checking if the list map_names_size exists; if not, create it
        if len(self.map_names_size) == 0:
            n_classes = len(self.escalas_limite)+1
            
            self.map_names_size = []
            for i in range(n_classes):
                        
                if i == 0:
                    minval = 0
                else:
                    minval = self.escalas_limite[i-1]
                
                if i == len(self.escalas_limite):
                    self.get_maxim_value
                    maxval = self.raster_max
                    maxname = 'Inf'
                else:   
                    maxval = self.escalas_limite[i]
                    maxname = `maxval`
                               
                map_size = self.mapapatch+'_class_'+`minval`+'_'+maxname
                self.map_names_size.append(map_size)
        
        # Beginning to generate seed rain maps
        cont = 0    
        self.map_names_seed_rain = []
        for i in self.map_names_size:
            # reclamando caso o par nao tenha dois argumentos
                
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
                 
            print 'running seed dispersal curves: %s' %i  
                
            par = parms_weib[cont]
            
            # par recebe um lista com dois valores para a equacao 
            # vale a pena testar no inicio - se nao for uma lista com dois argumentos, reclamar
            A_t = float(par[0])
            lambda_t = float(par[1])
            print str(par[0])+' '+str(par[1])
            
            d=i+'_hab_dist_pos'
            map_seed = i+'_seed_rain'
            self.map_names_seed_rain.append(map_seed)
            expression4 = map_seed+' = '+`A_t`+' * (1/'+`lambda_t`+') * exp(-('+d+'/'+`lambda_t`+'))'
            print expression4
            
            try:
                grass.mapcalc(expression4, overwrite = True, quiet = True)
            except:
                self.errorLog = "Problems in the function generate_distance_seed_deposition_maps mapcalc dispersal curves "+ i+'_hab_dist'
                self.Logfile # chamand a funcao log
                self.errorLog = ''
                
            if self.export_maps:
                self.export_map(map_seed)
                #pass
                                
            cont += 1
            
    
    def create_summary_maps(self, method = 'maximum'): # adicionei aqui o argumento method; se quisermos podemos fazer de outros jeitos
        '''
        Genereting final map --> maximum of the maps
        '''
        
        # Method options: average, count, median, mode, minimum, min_raster, maximum, max_raster, stddev, range, sum, variance, diversity
        name_rseries = 'map_seed_rain_' + method
        
        try:
            print ("genereting summary raster, method: "+method)
            grass.run_command('r.series', input=self.map_names_seed_rain, output=name_rseries, overwrite=True, method=method, flags='n')
        except:
            self.errorLog = "Problems in the function create_summary_maps r.series  "
            self.Logfile # chamand a funcao log
            self.errorLog = ''        

        #name_mapcalc = name_rseries + '_by_pasture'
        ## conferir aqui!
        ###expression5 = name_mapcalc+" = "+self.pasturemap+" * "+name_rseries
        ##expression5 = name_mapcalc+" = if("+self.pasturemap+" > 0, "+name_rseries+", null())"
        #expression5 = name_mapcalc+" = if("+self.pasturemap+" > 0, "+name_rseries+", null())"
        #try:
            #print ("genereting summary raster in pasture, method: "+method)
            #grass.mapcalc(expression5, overwrite = True, quiet = True)
        #except:
            #self.errorLog = "Problems in the function create_summary_maps " +expression5
            #self.Logfile # chamand a funcao log
            #self.errorLog = ''
            
        if self.export_maps:
            self.export_map(name_rseries)
            #self.export_map(name_mapcalc) 
        
    def remove_aux_maps(self):
        """
        Acho que remover vai ficar facil na mao..
        tenho medo de precisar usar algum mapa ainda
        melhor limpar depois .. o que acha?
        
        ok!!
        """
        pass
    
class Main(Seed_Deposition_Curves):
    def __init__(self, mapapatch, escalas_limite, parms_weib, dirfolder, pasturemap):
        Seed_Deposition_Curves.__init__(self, mapapatch, escalas_limite, parms_weib, dirfolder, pasturemap)
        
    def Run(self):
        Seed_Deposition_Curves.generate_size_class_maps(self)
        Seed_Deposition_Curves.generate_distance_seed_deposition_maps(self)
        Seed_Deposition_Curves.create_summary_maps(self, method="maximum")
        #Seed_Deposition_Curves.create_summary_maps(self, method="sum")
        #Seed_Deposition_Curves.create_summary_maps(self, method="average")
        

# Parameters

# Fragment size map
mapapatch = 'raster_teste_sad_patch_clump_mata_limpa_AreaHA'

# Pasture matrix map
pasturemap = "raster_teste_sad_patch_clump_mata_limpa_AreaHA"

# Patch size limits
escalas_limite = [10,25,50,250]

# Curve parameters
# [As, lambda]
parms_weib = [[30,130], [70,170], [120,220], [200,290], [350,350]]

# como podemos colocar, abaixo, o r sem coloca-lo junto com a pasta?
dirfolder = r"/home/leecb/Documentos/UNESP/analises/Vinicius_Tonetti_MA_mapa_regen/teste_com_Vini_output"


InstanceMain = Main(mapapatch, escalas_limite, parms_weib, dirfolder, pasturemap)
InstanceMain.Run()
