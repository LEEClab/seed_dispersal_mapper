# Seed Dispersal Mapper

## Description

The Seed Dispersal Mapper uses a raster map of habitat patch area to predict the chance
of seed deposition in the matrix (or, alternatively, in specific land use classes such as pasture), as a result of 
the process of animal-mediated seed dispersal of the plants present inside habitat patches. We consider seed dispersal as a proxy for the potential for natural regeneration, so that the final map produced is a landscape regenerability map.

The model implicitly considers animal movement as a proxy for understanding seed rain patterns and natural regenerability, based on the assumptions:

- larger patches shelter larger populations, a higher richness and compositional diverisity of dispersers than smaller patches
- larger patches generally have animal dispersers that are able to disperse plant seeds farther than those present in smaller fragments
- the closer the patches are, the greater the seed rain chance and the natural regenerability among them

The model uses the map of habitat patch area to divide habitat patches in size classes defined by the user. For each size class, a different dispersal kernel is applied to estimate seed dispersal and regenerability potential in the matrix around habitat patches. After that, seed dispersal maps for each patch size class are integrated using summary statistics. The limits of patch size classes, the parameters of dispersal kernels for each of them and the chosen summary statistics are all defined by the user in the beggining of the script. The input maps are also defined inside the script.

## Usage

This script runs in GRASS GIS 7.0.X environment, in principle in any operational system where GRASS GIS is supported (Linux, MacOS, Windows). The input maps must be loaded inside GRASS GIS location before running the model. 

After setting the parameters and input maps are set inside the script, start simulation by running:
```
python seed_dispersal_mapper_v1_0.py
```

## Citation

Please cite the Seed Dispersal Mapper when using the model in your work:

Niebuhr, B. B. S.; Pinto, F. S.; Ribeiro, J. W.; Costa, K. M.; Silva, R. F. B.; Ribeiro, M. C. Predicting natural regeneration through landscape structure, movement of frugivore fauna, and seed dispersal. In review.

## Authors

The method was developed inside the Spatial Ecology and Conservation Lab (LEEC) at Universidade Estadual Paulista.

If you need more information, send us an e-mail:
- Bernardo Niebuhr <bernardo_brandaum@yahoo.com.br>
- Milton Ribeiro <mcr@rc.unesp.br>
- Flavia Pinto <flaviasantospinto@gmail.com>
- John Ribeiro <jw.ribeiro.rc@gmail.com>


Laboratório de Ecologia Espacial e Conservação - LEEC  
Universidade Estadual Paulista - UNESP  
Rio Claro - SP - Brasil
