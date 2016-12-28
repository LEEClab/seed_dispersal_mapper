import grass.script as grass

mapa = 'nome_do_mapa_de_area_LS_patch'
escalas_lim = [10,25,50,250]
parametros_weibull = [[30,130], [70,170], [120,220], [200,290], [350,350]]

def generate_seed_deposition_curves(mapapatch, escalas_limite, parms_weib):
    
    n_classes = len(escalas_limite)+1
    
    # Generating maps of different fragment size classes
    map_names_size = []
    for i in range(n_classes):

        # colocar aqui algo pro usuario sabem em que peh esta, se esta andando, demorando, em qual mapa etc
        #print ...        
        if i == 0:
            minval = 0
        else:
            minval = escalas_limite[i-1]
        
        if i == len(escalas_limite):
            maxval = 1000000000000 # numero muito grande maior que qualquer fragmento (tem que ser maior?)
        else:
            maxval = escalas_limite[i]
                   
        grass.run_command('g.region', rast=mapapatch)
        map_size = mapapatch+'_class_'+`minval`+'_'+`maxval`
        map_names_size.append(map_size)
        expression = map_size+' = if('+mapapatch+' > '+`minval`+' && '+mapapatch+' <= '+`maxval`+','+mapapatch+', null())'
        #print expression
        grass.mapcalc(expression, overwrite = True, quiet = True)
        
    # Generating maps of distance and applying the curves
    cont = 0
    map_names_seed_rain = []
    for i in map_names_size:
        
        # colocar aqui algo pro usuario sabem em que peh esta, se esta andando, demorando, em qual mapa etc
        #print ...
        # Distance maps
        expression2 = i+'_bin = if('+i+' > 0, 1, null())'
        #print expression2
        grass.mapcalc(expression2, overwrite = True, quiet = True)
        grass.run_command('r.grow.distance', input=i+'_bin', distance=i+'_bin_dist')
        
        par = parms_weib[cont]
        print par
        A_t = par[0]
        lambda_t = par[1]
        
        # applting curves
        expression3 = 'd = '+i+'_bin'
        #print expression3
        grass.mapcalc(expression3, overwrite = True, quiet = True)
        map_seed = i+'_seed_rain'
        map_names_seed_rain.append(map_seed)
        expression4 = map_seed+' = '+`A_t`+' * (1/'+`lambda_t`+') * exp(-(d/'+`lambda_t`+'))'
        #print expression4
        grass.mapcalc(expression4, overwrite = True, quiet = True)
        
        cont+=1
        
        # colocar no final um if para g.remove os mapas que nao interessarem, usados so para os calculos
  
generate_seed_deposition_curves(mapa, escalas_lim, parametros_weibull)        

# agora da pra fazer uma outra funcao pra pegar o maximo dos cinco mapas, pra ter uma mapa final de deposicao

# e outra ainda pra multiplicar somente pelos mapas que queremos e em que pode haver deposicao (tipo pastagem, no nosso caso)
        
