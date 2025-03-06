import PySimpleGUI as sg, os, json, cv2, numpy as np, time
from types import SimpleNamespace as namespace

items=namespace(imgs=os.listdir('imgs'),current_image='',crop_img='',
	folder='imgs/',FILE_EXTENSIONS=[('PNG','*.png*'),('JPG','*.jpg*')],
	CLOSE_EVENTS={sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, 'Salir','Tomar foto'})

if items.imgs:
	items.current_image=items.imgs[0]

def layout():
	column_layout=[
		[sg.T('Lista de Imágenes')],
		[sg.Listbox(items.imgs,key='imgs',size=(58,20),enable_events=True,
			tooltip='Selecciona una imagen para establecerla como principal.')
		],
		[sg.In(key='new_img',size=40,enable_events=True,visible=False)],
		[sg.BM('Agregar',['Agregar',['Desde una imagen','Tomar foto']],key='Agregar'),
		*map(sg.B,('Remover','Escoger','Salir'))],
	]
	return [
		[sg.Column(column_layout, element_justification='c')]
	]


def photo_window():
	frame=None
	layout=[
	[sg.Image(key='img',size=(640,480))],
	[sg.B('Tomar foto'),sg.Exit('Salir')]
	]
	cap = cv2.VideoCapture(0)
	window=sg.Window('Tomar foto',layout,finalize=True,element_justification='c',
		resizable=True,enable_close_attempted_event=True)

	while True:
		event, data = window.read(timeout=20)
		if event not in items.CLOSE_EVENTS:
			_,frame=cap.read()
			window['img'].update(data=cv2.imencode('.png', frame)[1].tobytes())
		else:
			window.close()
			break
	return frame


def cvwindow(name,img, WINDOW_NAME="Rectangle Window"):
	drawing = True
	ix,iy = -1,-1

	def draw_rectangle(event, x, y, flags, param):
	   nonlocal ix, iy, drawing, img
	   if event == cv2.EVENT_LBUTTONDOWN:
	      drawing = True
	      ix = x
	      iy = y
	   elif event == cv2.EVENT_LBUTTONUP:
	      drawing = False
	      items.crop_img=img[iy:y,ix:x].copy()
	      cv2.rectangle(img, (ix, iy),(x, y),(255, 0, 0),2)
	      cv2.imshow(WINDOW_NAME, img)
	      time.sleep(0.7)

	# Create a window and bind the function to window
	cv2.namedWindow(WINDOW_NAME)

	# Connect the mouse button to our callback function
	cv2.setMouseCallback(WINDOW_NAME, draw_rectangle)

	# display the window
	cv2.imshow(WINDOW_NAME, img)
	while drawing:
	   if cv2.waitKey(10) == 27:
	   	break
	cv2.destroyWindow(WINDOW_NAME)


def main():
	window=sg.Window('Program_Name',layout(),finalize=True,element_justification='c',
		resizable=True,enable_close_attempted_event=True)

	def refresh_list():
		window['imgs'].update(values=items.imgs)

	while True:
		event, data = window.read()
		if event not in items.CLOSE_EVENTS:
			match event:
				case 'Remover':
					if data['imgs']:
						img=data['imgs'][0]
						items.imgs.remove(img)
						os.remove(items.folder+img)
						refresh_list()
						
					else:
						sg.popup_ok('Debe Seleccionar una imagen primero.')

				case 'imgs':
					if items.imgs:
						items.current_image=data[event][0]

				case 'Agregar':
					new_img=None
					match data[event]:
						case 'Desde una imagen':
							new_img=sg.popup_get_file(
								'A continuación recorte a manera de selección la parte\n'
									'de la imagen que corresponde a un parqueo.'
									'\nUna vez haya terminado, cierre la ventana presionando la X.',
									'Buscar Imagen',
								file_types=items.FILE_EXTENSIONS)
							if new_img:
								new_img=cv2.imread(new_img.replace('/','\\'))

						case 'Tomar foto':
							new_img=photo_window()

					if new_img is not None:
						assert new_img is not None
						cvwindow('Imagen',new_img)
						new_img_name=sg.popup_get_text('Inserte El nombre del archivo')
						if new_img_name:
							cv2.imwrite(items.folder+new_img_name,items.crop_img)
							items.imgs.append(new_img_name)
							items.current_image=new_img_name
							items.crop_img=cv2.cvtColor(items.crop_img,cv2.COLOR_BGR2GRAY)
							refresh_list()

				case 'Escoger':
					if items.current_image:
						items.crop_img=cv2.imread(items.folder+items.current_image,cv2.IMREAD_GRAYSCALE)
					else:
						sg.popup_ok('Debe Escoger una imagen primero.')

				case _:
					print(event)
				
		else:
			window.close()
			break

if __name__ == '__main__':
	main()