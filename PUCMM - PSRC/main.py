"""
------------------Librerías---------------------
-	PySimpleGUI: Librería con todas las herramientas necesarias para trabajar con la creación
de interfaces gráficas de usuario.

-	numpy: Biblioteca que cuenta con soporte para la creación de matrices o vectores,
así como funciones matemáticas de alto nivel con estos mismos.

-	cv2: Librería que permite el trabajo a alto a nivel de contenido multimedia, así como operaciones
complejas como detección de imágenes y objetos, manipulación de vídeo e imágenes, etc..

"""
import PySimpleGUI as sg, cv2, config, numpy as np


'''Esta variable es usada cuando el usuario presiona el botón de detener grabación. Se crea
una matrix de 640x480 con el valor 255, usando el método full de numpy.
la librería cv2 se encarga de encodificar esta matrix en formato de imagen PNG,
con el metodo IMENCODE.'''
EMPTY_IMG=cv2.imencode('.png', np.full((480,640),255))[1].tobytes()


'''La funcion set_optionss de PySimpleGUI nos permite configurar algunas opciones por defecto,
para de esa forma no tener que especificarlas todo el tiempo. Al poner el font en times new
roman 16 y centrar al texto, automaticamente todos los controles y ventanas tendran esta
configuración. Si se borrará esta línea, habría que especificar la fuente, para cada control
y ventana, así como la justificación a las columnas y ventanas.'''
sg.set_options(font=('Times new roman',16),text_justification='c')

'''Esta función sirve para configurar el diseño de la ventana principal.
PySimpleGUI usa una ideología en la que divide una ventana en filas y columnas que contienen
controles de interacción con el usuario.
'''

def layout():
	menu_layout=[
	['Menu', ['Grabar','Detener Grabación','Configuración','Salir','Acerca de']]
	]
	frame_video_layout=[
	[sg.Image(key='image')]
	]
	label_column=[
	[sg.T('Parqueos Ocupados: '),sg.T('N/A',key='free_parkings')],
	[sg.T('Parqueos Libres: '),sg.T('N/A',key='taken_parkings')]
	]
	return [
	[sg.Menu(menu_layout)],
	[sg.Frame('Contador de Parqueos',frame_video_layout,expand_y=True,expand_x=True,
		element_justification='c')],
	[sg.Column(label_column,element_justification='r')]
	]
	return layout

def main_window():
	return sg.Window('Program_Name',layout(),finalize=True,element_justification='c',
		resizable=True,enable_close_attempted_event=True)

def main():
	sg.theme('DarkAmber')#Se configura la paleta de colores a utilizar
	window=main_window()
	window.maximize()#La ventana se abre en pantalla completa
	cap = cv2.VideoCapture(r"C:\Users\elmen\OneDrive\Desktop\Parking_imgs\prueba.mp4")#Se crea un videocapturador que conecte con la camara.
	recording = False

	while True:
		event, data = window.read(timeout=20)
		if event not in config.items.CLOSE_EVENTS:
			match event:
				case 'Grabar':
					if not isinstance(config.items.crop_img,np.ndarray):
						sg.popup_ok('No se ha configurado ninguna imagen.\n'
							'Vaya al apartado de configuración para escoger una imagen.')
					else:
						recording = True
						window['free_parkings'].update('0')
						window['taken_parkings'].update('0')

				case 'Detener Grabación':
					recording = False
					window['image'].update(data=EMPTY_IMG)

				case 'Configuración':
					window.close()
					config.main()
					window=main_window()
					window.maximize()

			if recording:
				_, frame = cap.read()#El Método read permite capturar el frame actual.
				'''Se transforma la imagen a una escala de grises. Esto facilita el
				reconocimiento de objetos y la búsqueda de parques vacíos.
				'''
				gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
				'''Se obtiene la imagen recortada que corresponde a un parqueo vacío.
				Luego, con el método matchTemplate, se obtienen todas las coordenadas donde
				la imagen de un parqueo vacio fue encontrada, y se procede a dibujar rectangulos
				en el frame con el metodo rectangle de cv2. Posteriormente, se obtiene
				la encodificación PNG del frame, ya que por defecto, cada frame es devuelto en forma de
				una matrix numpy, y luego se actualiza el control de interfaz Image de PySimpleGUI,
				pasando los bytes como el argumento "data".'''
				template=config.items.crop_img
				w, h = template.shape[::-1]
				res = cv2.matchTemplate(gray_frame,template,cv2.TM_CCOEFF_NORMED)
				loc = (np.where(res >= 0.8))[::-1]
				for pt in zip(*loc):
					cv2.rectangle(frame, pt, (pt[0] + w, pt[1] + h), (0,0,255), 2)
				imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
				window['image'].update(data=imgbytes)
		else:
			window.close()
			break


if __name__ == '__main__':
	main()