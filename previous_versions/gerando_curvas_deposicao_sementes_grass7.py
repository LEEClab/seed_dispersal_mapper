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
 Usage: python gerando_curvas_deposicao_sementes_grass7.py
 
 The Seed Deposition map generator uses a map of habitat/forest area to predict the chance
 of seed deposition in the matrix, as a result of the process of animal-mediated 
 seed dispersal of the plants present inside habitat patches.
 The model assumes that, in large patches, fauna is more abundant and there are animal
 taxa that can carry seeds farther in the matrix (long seed dispersers); on the other hand,
 in small patches there are few long seed disepersers and fauna is less abundant.
 
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
import datetime
import os

class Seed_Deposition_Curves(object):
    
    def __init__(self, mapapatch, escalas_limite, parms_weib, dirfolder):
        self.mapapatch = mapapatch
        self.escalas_limite = escalas_limite
        self.parms_weib = parms_weib
        self.raster_max = 100000
        self.map_names_size = []
        self.map_names_seed_rain = []
        self.errorLog = ''
        self.dirfolder = dirfolder
        self.pasturemap = "Clip_mosaico_final_clip_rast_clip_tif_reclass2_inv"
        self.export_maps = True
        self.format_export = "GTiff"
    
    def Logfile(self):
        os.chdir(self.dirfolder)
        #end time
        time = datetime.now() # INSTANCE
        day = time.day
        month = time.month
        year = time.year
        hour = time.hour # GET end hour
        minuts = time.minute #GET end minuts
        second = time.second #GET 
        txt=open("__Log_"+`day`+`minuts`+`second`+".txt",w)
        txt.write("Error-----------"+self.errorLog+'\n')
        txt.close()
        
    def export_map(self, input_map):
        
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
        
        grass.run_command('r.out.gdal', input=input_map, output=input_map+sufix, format = form, overwrite = True, quiet = True))
        
    def get_maxim_value(self):
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
            
            # par rece um lista com dois valores para a equacao 
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
                                
            cont+=1    
    
    def create_summary_maps(self, method = 'maximum'): # adicionei aqui o argumento method; se quisermos podemos fazer de outros jeitos
        '''
        Genereting final map --> maximum of the maps
        '''
        # agora da pra fazer uma outra funcao pra pegar o maximo dos cinco mapas, pra ter uma mapa final de deposicao
        
        # aqui podemos multiplicar pelo negativo do mapa de manchas tambem, para retirar as manchas... 
        try:
            print ("genereting summary raster")
            grass.run_command('r.series', input=self.map_names_seed_rain, output="map_seed_rain_maxVal", overwrite=True, method=method)
        except:
            self.errorLog = "Problems in the function create_summary_maps r.series  "
            self.Logfile # chamand a funcao log
            self.errorLog = ''        

        expression5 = "map_seed_rain_maxVal_by_pasture = "+self.pasturemap+" * "+"map_seed_rain_maxVal"
        try:
            grass.mapcalc(expression5, overwrite = True, quiet = True)
        except:
            self.errorLog = "Problems in the function create_summary_maps " +expression5
            self.Logfile # chamand a funcao log
            self.errorLog = ''
            
        if self.export_maps:
            self.export_map("map_seed_rain_maxVal")
            self.export_map("map_seed_rain_maxVal_by_pasture") 
        
    def remove_aux_maps(self):
        """
        Acho que remover vai ficar facil na mao..
        tenho medo de precisar usar algum mapa ainda
        melhor limpar depois .. o que acha?
        
        ok!!
        """
        pass
    
class Main(Seed_Deposition_Curves):
    def __init__(self, mapapatch, escalas_limite, parms_weib, dirfolder):
        Seed_Deposition_Curves.__init__(self, mapapatch, escalas_limite, parms_weib, dirfolder)
        
    def Run(self):
        Seed_Deposition_Curves.generate_size_class_maps(self)
        Seed_Deposition_Curves.generate_distance_seed_deposition_maps(self)
        Seed_Deposition_Curves.create_summary_maps(self)
 
 
mapapatch = 'Clip_mosaico_final_clip_rast_clip_tif_reclass2_patch_clump_mata_limpa_AreaHA'
escalas_limite = [10,25,50,250]
parms_weib = [[30,130], [70,170], [120,220], [200,290], [350,350]]
dirfolder = "E:\Documentos_ber\Atividades_2016\consultoria_AgroIcone\curvas_deposicao_sementes\teste_curvas"       
InstanceMain = Main(mapapatch, escalas_limite, parms_weib, dirfolder)
InstanceMain.Run()