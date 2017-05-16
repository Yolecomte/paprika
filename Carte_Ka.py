import processing
from qgis.core import *
from shutil import copyfile
import numpy
from osgeo import gdal, ogr, osr

def genere_carteKa(Mangin, karst_features, field_karst_features, extension, doss):
	
	#Rasterisation et ouverture de la couche karst features
	copyfile(str(doss)+'/Extension.tif',str(doss)+'/rKarst_features.tif')
	processing.runalg("gdalogr:rasterize_over", karst_features, field_karst_features, str(doss)+'/rKarst_features.tif')
	rKarst_features = QgsRasterLayer(str(doss)+'/rKarst_features.tif','rKarst_features')
	
	#Creation du raster global a partir de la classification de Mangin
		#recuperation des bornes XY de la zone
	extension1 = gdal.Open(extension.source())
	ExtentInfo = extension1.GetGeoTransform()
	Xmin = str(ExtentInfo[0])
	Ymin = str(ExtentInfo[3])
	Xmax = str(ExtentInfo[0] + ExtentInfo[1] * extension1.RasterXSize)
	Ymax = str(ExtentInfo[3] + ExtentInfo[5] * extension1.RasterYSize)
	Extent =(Xmin, Xmax, Ymax, Ymin)
	StrExtent = ','.join(Extent)
		
	if Mangin == 1 :
		ValMangin = 2
	elif Mangin == 2 :
		ValMangin = 3
	elif Mangin == 3 :
		ValMangin = 4
	elif Mangin == 4 :
		ValMangin = 4
	elif Mangin == 5 :
		ValMangin = 1
	
	#recuperation du systeme de coordonnees
	source = gdal.Open(extension.source())
	Syst_coord = source.GetProjection()

	#Croisement des valeurs des rasters sur chaque pixel
	valCarteKa = numpy.zeros((extension1.RasterYSize, extension1.RasterXSize), numpy.int16)
	val_i = range(0, extension1.RasterXSize, 1)
	val_j = range(0, extension1.RasterYSize, 1)
	pKarst_features = rKarst_features.dataProvider()
	#pMangin = rMangin.dataProvider()
	for j in val_j:
		for i in val_i:		
			pos = QgsPoint((ExtentInfo[0] + i * ExtentInfo[1]) - ExtentInfo[1]/2, (ExtentInfo[3] - j * ExtentInfo[1]) - ExtentInfo[1]/2)
			valKarst_features = pKarst_features.identify(pos, QgsRaster.IdentifyFormatValue).results()[1]
			#valMangin = pMangin.identify(pos, QgsRaster.IdentifyFormatValue).results()[1]
			if valKarst_features is None:
				valKarst_features = 0
			index = valKarst_features + ValMangin
			if index > 4 :
				valCarteKa[j,i] = 4
			else :
				valCarteKa[j,i] = index
	
	#ecriture du raster a partir de l'array
	Raster = gdal.GetDriverByName('Gtiff').Create(str(doss)+'/Carte_Ka.tif', extension1.RasterXSize, extension1.RasterYSize, 1, gdal.GDT_Byte)
	proj = osr.SpatialReference()
	proj.ImportFromWkt(Syst_coord)
	Raster.SetProjection(proj.ExportToWkt())
	Raster.SetGeoTransform(ExtentInfo)
	Band = Raster.GetRasterBand(1)
	Band.WriteArray(valCarteKa, 0, 0)
	Band.FlushCache()
	Band.SetNoDataValue(0)