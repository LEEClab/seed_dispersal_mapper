#"class tanto a tanto" + "seedrain"
import grass.script as grass
import os
p=grass.list_grouped ('rast', pattern='*map*') ['PERMANENT']

#os.chdir(r"E:\__data_2016\____John\_________Pastacompartilhada\__Agroicone\___RESULTADOS")
#for i in p:
    #if not "hab" in i :
       ## print i
        #grass.run_command('r.out.gdal',input=i, output=i+'.tif',overwrite = True)
        
#bloco de remover perigoso        
for i in p:
    grass.run_command('g.remove', type='rast',name=i, flags = "f")