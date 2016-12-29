# Seed Dispersal Mapper

The Seed Dispersal Mapper uses a raster map of habitat/forest patch area to predict the chance
of seed deposition in the matrix (or, alternatively, in specific land use classes such as pasture), as a result of 
the process of animal-mediated seed dispersal of the plants present inside habitat patches.

It implicitly considers animal movement as a proxy for understanding seed rain patterns, based on the assumptions:

- larger patches shelter larger frugivore population than smaller patches
- larger patches generally have frugivores that are able to disperse plant seeds farther than those present in smaller fragments
- the closer the patches are, the greater the seed rain chance among them

This script runs in GRASS GIS 7.0.X environment.

Usage: 
```
python seed_dispersal_mapper_v1_0.py
```

The method was developed inside the Spatial Ecology and Conservation Lab (LEEC) at Universidade Estadual Paulista.
If you need more information, send us an e-mail:
- Bernardo Niebuhr <bernardo_brandaum@yahoo.com.br>
- Milton Ribeiro <mcr@rc.unesp.br>
- Flavia Pinto <flaviasantospinto@gmail.com>
- John Ribeiro <jw.ribeiro.rc@gmail.com>


Laboratorio de Ecologia Espacial e Conservacao

Universidade Estadual Paulista - UNESP

Rio Claro - SP - Brasil
