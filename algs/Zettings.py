INTERSECTA = 0
CONTIENE = 1
IGUALA = 2
TOCA = 3
SOLAPA = 4
DENTRO = 5
CRUZA = 6

COUNT = 0
UNIQUE = 1
MIN = 2
MAX = 3
INTERVALO = 4
SUM = 5
MEDIA = 6
MEDIANA = 7


IGUAL = 0
DIFERENTE = 1
MAYOR = 2
MAYORIGUAL = 3
MENOR = 4
MENORIGUAL=5
COMIENZACON = 6
CONTINE = 7
IS_NULL = 8 
NOT_NULL = 9
NOCONTINETE = 10


DISCARD_NONMATCHING = True
UNDISCARD_NONMATCHING = False

P_CELL_SIZE = 300

#{'key':['attr', 'file', 'title']}

NAMES_INDEX = {
	'IA01': ['ia01','ia01','A01 Densidad neta de habitantes'],
	'IA02': ['ia02','ia02','A02 Densidad neta de viviendas'],
	'IA03': ['ia03','ia03','A03 Compacidad absoluta'],
	'IA04': ['ia04','ia04','A04 Eficiencia en el uso del territorio'],
	'IA05': ['ia05','ia05','A05 Área de predios vacíos'],
	# 'IA06': ['ia06','ia06',''],
	'IA07': ['ia07','ia07','A07 Proximidad a servicios urbanos básicos'],
	'IA08': ['ia08','ia08','A08 Proximidad al espacio público abierto'],
	'IA09': ['ia09','ia09','A09 Cobertura de actividades comerciales cotinianas'],
	'IA10': ['ia10','ia10','A10 Relación entre actividad y residencia'],
	'IA11': ['ia11','ia11','A11 Complejidad urbana'],
	# 'IA12': ['ia12','ia12',''],
	# 'IA13': ['ia13','ia13',''],
	# 'IA14': ['ia14','ia14',''],
	# 'IA15': ['ia15','ia15',''],
	'IB01': ['ib01','ib01','B01 Calidad del aire'],
	'IB02': ['ib02','ib02','B02 Luminación nocturna del viario público'],
	'IB03': ['ib03','ib03','B03 Confort acústico'],
	# 'IB04': ['ib04','ib04',''],
	'IB05': ['ib05','ib05','B05 Superficie verde por habitante'],
	'IB06': ['ib06','ib06','B06 Proximidad al espacio verde público más cercano'],
	'IB07': ['ib07','ib07','B07 Permeabilidad del suelo'],
	'IB08': ['ib08','ib08','B08 Superficie de área agrícola/huertos'],
	'IC01': ['ic01','ic01','C01 Reparto del viario público peatonal'],
	# 'IC02': ['ic02','ic02',''],
	'IC03': ['ic03','ic03','C03 Vías públicas por habitante'],
	'IC04': ['ic04','ic04','C04 Proximidad a redes de transporte alternativo'],
	# 'IC05': ['ic05','ic05',''],
	# 'IC06': ['ic06','ic06',''],
	# 'IC07': ['ic07','ic07',''],
	'IC08': ['ic08','ic08','C08 Espacio público ocupado por vehículos parqueados'],
	# 'IC09': ['ic09','ic09',''],
	# 'IC10': ['ic10','ic10',''],
	# 'IC11': ['ic11','ic11',''],
	# 'IC12': ['ic12','ic12',''],
	'IC13': ['ic13','ic13','C13 Cobertura del sistema de servicio de alcantarillado'],
	# 'IC14': ['ic14','ic14',''],
	# 'IC15': ['ic15','ic15',''],
	# 'IC16': ['ic16','ic16',''],
	# 'IC17': ['ic17','ic17',''],
	# 'IC18': ['ic18','ic18',''],
	# 'IC19': ['ic19','ic19',''],
	# 'IC20': ['ic20','ic20',''],
	'ID01': ['id01','id01','D01 Viviendas con cobertura total de servicios básicos'],
	'ID02': ['id02','id02','D02 Viviendas con carencias constructivas'],
	'ID03': ['id03','id03','D03 Viviendas emplazadas en zonas vulnerables y de riesgo'],
	'ID04': ['id04','id04','D04 Espacios públicos abiertos que necesitan mejoras'],
	'ID05': ['id05','id05','D05 Acceso a internet'],
	# 'ID06': ['id06','id06',''],
	'ID07': ['id07','id07','D07 Indice de calidad de vida'],
	# 'ID08': ['id08','id08',''],
	# 'ID09': ['id09','id09',''],
	'ID10': ['id10','id10','D10 Cercanía y asequibilidad a alimentos'],
	'ID11': ['id11','id11','D11 Robos por número de habitantes'],
	'ID12': ['id12','id12','D12 Seguridad de tenencia de la vivienda'],
	'ID13': ['id13','id13','D13 Población activa con estudios universitarios'],
	# 'ID14': ['id14','id14',''],
	'ID15': ['id15','id15','D15 Mujeres en la fuerza de trabajo remunerado'],
	'ID16': ['id16','id16','D16 Índice de envejecimiento'],
	'ID17': ['id17','id17','D17 Segregación Espacial'],
	'ID19': ['id19','id19','D19 Estabilidad de la comunidad']
}

TEXT_GRID_INPUT = 'Malla (Si ya tienes una malla de estudio)'
OPTIONAL_GRID_INPUT = False