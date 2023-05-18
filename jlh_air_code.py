import geopandas as gpd
import geoparquet as gpq
import pandas as pds
import numpy as np

#INISIASI DATA YANG DIGUNAKAN
table_pl = pds.read_csv('[lokasi file]')
table_kba = pds.read_csv('[lokasi file]')
table_kva = pds.read_csv('[lokasi file]')
ekoregion = gpd.read_file('[lokasi file]')
PL_1996 = gpd.read_file('[lokasi file]')
PL_2021 = gpd.read_file('[lokasi file]')

#MENYAMAKAN SISTEM KOORDINAT
PL_1996 = PL_1996.to_crs(3395)
PL_2021 = PL_2021.to_crs(3395)
ekoregion = ekoregion.to_crs(3395)

#PROSES OVERLAY DATA
overlay_old = ekoregion.overlay(PL_1996, how='intersection',keep_geom_type=False)
overlay_new = overlay_old.overlay(PL_2021, how='intersection',keep_geom_type=False)
jlh = gpd.GeoDataFrame(overlay_new)

#PROSES JOIN TABLE SKOR PL

jlh_pl_96 = pds.merge(jlh, table_pl, left_on='PL96_ID', right_on='pl',suffixes=[None,'_96'])
jlh_pl_21 = pds.merge(jlh_pl_96, table_pl, left_on='PL2021_ID', right_on='pl',suffixes=[None,'_21'])
jlh_kba = pds.merge(jlh_pl_21, table_kba, left_on='KBA_250', right_on='KBA_250')
jlh_kva = pds.merge(jlh_kba, table_kva, left_on='KVA_250', right_on='KVA_250')

jlh=jlh_kva

#MENGHITUNG SKOR JASLING 1996
jlh['SPgAir_96'] = (jlh['KBA_Pg']*0.28) + ((jlh['KVA_Pg']*0.12)) + (jlh['PLPg']*0.6)
jlh['SPyAir_96'] = (jlh['KBA_Py']*0.28) + ((jlh['KVA_Py']*0.12)) + (jlh['PLPy']*0.6)

#MENGHITUNG SKOR JASLING 2021
jlh['SPgAir_21'] = (jlh['KBA_Pg']*0.28) + ((jlh['KVA_Pg']*0.12)) + (jlh['PLPg_21']*0.6)
jlh['SPyAir_21'] = (jlh['KBA_Pg']*0.28) + ((jlh['KVA_Pg']*0.12)) + (jlh['PLPy_21']*0.6)


#MENGHITUNG SKOR KECENDERUNGAN
jlh['SKPgAir'] = jlh['SPgAir_21'] - jlh['SPgAir_96']
jlh['SKPyAir'] = jlh['SPyAir_21'] - jlh['SPyAir_96']

#KLASIFIKASI SKOR JASLING(Sangat Rendah - Sangat Tinggi)
class_pg_96 = [
    (jlh['SPgAir_96'] <= 1.8),
    (jlh['SPgAir_96'] > 1.8) & (jlh['SPgAir_96'] <= 2.6),
    (jlh['SPgAir_96'] > 2.6) & (jlh['SPgAir_96'] <= 3.4),
    (jlh['SPgAir_96'] > 3.4) & (jlh['SPgAir_96'] <= 4.2),
    (jlh['SPgAir_96'] > 4.2)
    ]

class_py_96 = [
    (jlh['SPyAir_96'] <= 1.8),
    (jlh['SPyAir_96'] > 1.8) & (jlh['SPyAir_96'] <= 2.6),
    (jlh['SPyAir_96'] > 2.6) & (jlh['SPyAir_96'] <= 3.4),
    (jlh['SPyAir_96'] > 3.4) & (jlh['SPyAir_96'] <= 4.2),
    (jlh['SPyAir_96'] > 4.2)
    ]

class_pg_21 = [
    (jlh['SPgAir_21'] <= 1.8),
    (jlh['SPgAir_21'] > 1.8) & (jlh['SPgAir_21'] <= 2.6),
    (jlh['SPgAir_21'] > 2.6) & (jlh['SPgAir_21'] <= 3.4),
    (jlh['SPgAir_21'] > 3.4) & (jlh['SPgAir_21'] <= 4.2),
    (jlh['SPgAir_21'] > 4.2)
    ]

class_py_21 = [
    (jlh['SPyAir_21'] <= 1.8),
    (jlh['SPyAir_21'] > 1.8) & (jlh['SPyAir_21'] <= 2.6),
    (jlh['SPyAir_21'] > 2.6) & (jlh['SPyAir_21'] <= 3.4),
    (jlh['SPyAir_21'] > 3.4) & (jlh['SPyAir_21'] <= 4.2),
    (jlh['SPyAir_21'] > 4.2)
    ]

values = ['Sangat Rendah', 'Rendah', 'Sedang', 'Tinggi', 'Sangat Tinggi']


jlh['PgAir_96'] = np.select(class_pg_96, values)
jlh['PyAir_96'] = np.select(class_py_96, values)
jlh['PgAir_21'] = np.select(class_pg_21, values)
jlh['PyAir_21'] = np.select(class_py_21, values)

#KLASIFIKASI KECENDERUNGAN JASA (MENURUN,TETAP,MENINGKAT)
class_KPgAir = [
    (jlh['SKPgAir'] < 0),
    (jlh['SKPgAir'] == 0),
    (jlh['SKPgAir'] > 0)
    ]

class_KPyAir = [
    (jlh['SKPyAir'] < 0),
    (jlh['SKPyAir'] == 0),
    (jlh['SKPyAir'] > 0)
    ]

values = ['Menurun', 'Tetap', 'Meningkat']

jlh['KPgAir9621'] = np.select(class_KPgAir, values)
jlh['KPyAir9621'] = np.select(class_KPyAir, values)

#EKSPOR FILE
jlh.to_file("jlh.gpkg", layer='JLH_Air', driver="GPKG")
