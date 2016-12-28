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
        
                
    def generate_distance_seed_deposition_maps(self):
        '''
        Generating maps of distance and applying the curves
        '''
        
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

            cont+=1    
    
    def create_summary_maps(self, method = 'maximum'): # adicionei aqui o argumento method; se quisermos podemos fazer de outros jeitos
        '''
        Genereting final map --> maximum of the maps
        '''
        # agora da pra fazer uma outra funcao pra pegar o maximo dos cinco mapas, pra ter uma mapa final de deposicao
        
        try:
            print ("genereting summary raster")
            grass.run_command('r.series', input=self.map_names_seed_rain, out="map_seed_rain_maxVal", overwrite=True, method=method)
        except:
            self.errorLog = "Problems in the function create_summary_maps r.series  "
            self.Logfile # chamand a funcao log
            self.errorLog = ''         

        expression5 = "map_seed_rain_maxVal_by_pasture="+self.pasturemap+"*"+"map_seed_rain_maxVal"
        try:
            grass.mapcalc(expression5, overwrite = True, quiet = True)
        except:
            self.errorLog = "Problems in the function create_summary_maps " +expression5
            self.Logfile # chamand a funcao log
            self.errorLog = ''              
        
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