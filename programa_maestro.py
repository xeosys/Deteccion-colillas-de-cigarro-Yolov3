# -*- coding: utf-8 -*-
"""
Universidad Tecnica Federico Santa María
Carrera: Tecnico universitario En Robótica y Mecatrónica 

Trabajo de Titulo

Sección: Procesamiento de Imagen
Autores: Matias Oliver Flores Paz, Omar Eliceo Garrido Huaiquifil
Profesor: Rodrigo Alejandro Méndez 


  En el presente script de Python, se realiza el procesado de imagen para la detección de colillas
  de cigarro. Para lograrlo, esta detección se realiza con una red neuronal Yolov3, las coordenadas
  en la salida, nos permitiran determinar la posición del objeto detectado, y mandas dichas coordenadas 
  por puerto serial, hacia el controlador. Esto con el fin, de lograr unir los dos sistemas.

"""

# Se importan librerias necesarias
from skimage import io                    #Necesaria para conseguir la resolución de la foto
from darknet import performDetect as scan #Darknetlib para el uso de la red neuronal
import serial, time                       #Serial para trabajar con puerto serial, y time para otorgar tiempos de espera
import cv2                                #cv2 para la manipulación de imagen 
import sys


#Se define variabes gobales con el angulo de apertura de la camara
res_x = 30
res_y = 22

#se definen variables solicitud, para solicitar instruccion "buscar o recolectar"
solicitud1 = "-1,0,0,0"
solicitud1 = solicitud1.encode("ASCII")

#instrucción para accionar el brazo
solicitud2 = "1,0,0,0"
solicitud2 = solicitud2.encode("ASCII")



tiempo_bucle = 0

#se define el puerto serial dando acceso a UART, guardandolo en "controlador"
controlador= serial.Serial ("/dev/ttyTHS1", 115200) 


#se construye un ciclo infinito, para posteriormente rectificar la posicion de la camara
while True:
    
 if (time.time() >= (tiempo_bucle + 0.1)):   
         tiempo_bucle = time.time()
         
         
         
         
         #se define la camara (0) y se captura un frame
         #si este es capturado se guarda un booleano true en "leido", si es así, el frame se guarda como foto.jpg
         cap = cv2.VideoCapture(0)

         leido, frame = cap.read()
            
         
         if leido == True:
           img= cv2.imwrite("foto.jpg", frame)
           print("foto lista para procesar")
           
          

         else:
             
             print("error al tomar foto")


         
            
         cap.release()   #se "suelta" la camara
         
         #se define una funcion "defect" para el posterior procesadode imagen
         #se configuran los path del codigo base de la red neuronal yolov3.cfg
         #el path de los archivos data, y los pesos
          
         def detect(img_path):    
                picpath = img_path
                # definir 
                cfg = 'cfg/yolov3.cfg'
                coco = 'cfg/obj.data'  
                data = 'backup/yolov3_last.weights'
                test = scan(imagePath=picpath, thresh=0.25, configPath=cfg, weightPath=data, metaPath=coco, showImage=False, makeImageOnly=False,
                            initOnly=False)  
                # Test por defecto para solo entregar output con coordenadas sin la foto procesada, ShowImage=True para mostrar imagen.
                
              
                

                newdata = []

                
                #se usa la función round en las coordenadas para evitar perder información
                #con la funcion len, se busca determinar la cantidad de objetos detectados, para definir ambos casos (un objeto o multiples) y obtener las 4 coordenas
                
                # para multiples detecciones
                if len(test) >= 2:
                    for x in test:
                        item, confidence_rate, imagedata = x
                        x1, y1, w_size, h_size = imagedata
                        x_start = round(x1 - (w_size/2))
                        y_start = round(y1 - (h_size/2))
                        x_end = round(x_start + w_size)
                        y_end = round(y_start + h_size)
                        data = (item, confidence_rate,
                                (x_start, y_start, x_end, y_end), (w_size, h_size))
                        newdata.append(data)

                # para una detección
                elif len(test) == 1:
                    item, confidence_rate, imagedata = test[0]
                    x1, y1, w_size, h_size = imagedata
                    x_start = round(x1 - (w_size/2))
                    y_start = round(y1 - (h_size/2))
                    x_end = round(x_start + w_size)
                    y_end = round(y_start + h_size)
                    data = (item, confidence_rate,
                            (x_start, y_start, x_end, y_end), (w_size, h_size))
                    newdata.append(data)

                else:
                    newdata = False

                return newdata


         if __name__ == "__main__":
             
               
              # Lo primero es enviar sulicitud de instrucción al controlador
             
               
                    controlador.flushInput()
                    controlador.write(solicitud1)
                    estado = controlador.read()
                    
                    estado = estado.decode('utf-8').strip()
                    estado = int(estado) 
                       
                    print(estado)
                    
                    #si la respuesta es 0, se acciona el brazo
                    if estado == 0:
                          #controlador.flush()
                          controlador.write(solicitud2)
                          estado_fin = controlador.read()
                    
                    
                    else:          
                        run = 'foto.jpg'              #se incluye el path relativo de la foto tomada 
                        detections = detect(run)      # funcion detect sobre imagen tomada, se guarda en detectios
                        
                        
                        image = io.imread("foto.jpg")  #con la librería SKimage, se obtiene la resolución de la imagen en una tupla
                        resols = image.shape
                        
                        
                        #se guardan la resolucion x,y en dos variables
                        resol_x = resols[1]
                        resol_y = resols[0]

                        print(resol_x)
                        print(resol_y)

                        mid_r_x = int(resol_x/2)
                        mid_r_y = int(resol_y/2)
                        
                      
                        print(detections)
                        
                        
                        
                        # se verifica si hay objetos detectados en "detections"
                        if detections ==False:
                            
                            print("no se ha encontrado objeto")
                            pass
                        
                        #función len sobre detections para obtener el numero de objetos
                        #si es mayor a 1, se ejecuta ciclo for para cada una de las imagenes
                        elif len(detections) > 1:
                            for detection in detections:
                                
                              print('Porcentaje: ', detection[1])    #se obtiene el porcentaje de confianza 

                              x1, y1, x2, y2 = detection[2]          #se obtiene 4 coordenadas de los labels
                              
                                
                            print('x1: ', x1)
                            print('y1: ', y1)
                            print('x2: ', x2)
                            print('y2: ', y2)
                            
                            #se busca enviar a controlador datos para la camara (a=0)
                            #se busca punto medio del objeto usando estas 4 coordenadas para determinar posicion del objeto en plano x,y
                            a = "0"  
                            b = "0"
                            mid_x = x2-x1
                            mid_y = y2-y1       
                            print('Delta y:', mid_x)
                            mid_x = (mid_x/2) + x1
                            mid_y = (mid_y/2) + y1
                            print('CENTRO X:', mid_x)
                            print('CENTRO Y:', mid_y)
                            mid_x = mid_r_x - mid_x
                            mid_y = mid_r_y - mid_y
                            print('Distancia al centro y:', mid_x)
                            
                            x_serial = (mid_x * res_x)/mid_r_x
                            y_serial = (mid_y * res_y)/mid_r_y
                            
                            print('Pos_Proceso:', x_serial)                   
                            y_serial = int(y_serial)
                            x_serial = int(x_serial)
                            print('int y:', y_serial)
                            print('Coordenadas serial a enviar')
                            print ('x:',x_serial)
                            print ('y:', y_serial)
                            dato_txt = str(a) + ',' + str(b) + ',' + str(-x_serial) + ',' + str(-y_serial)
                            dato_txt = dato_txt.encode("ASCII")
                            controlador.write(dato_txt)
                            
                            
                        # una detección
                        else:
                            
                            print('porcentaje: ', detections[0][1])
                            
                            x1, y1, x2, y2 = detections[0][2]
                            
                            
                            
                          
                            print('x1: ', x1)
                            print('y1: ', y1)
                            print('x2: ', x2)
                            print('y2: ', y2)
                            a = "0"
                            b = "0"
                            mid_x = x2-x1
                            mid_y = y2-y1       
                            print('Delta y:', mid_x)
                            mid_x = (mid_x/2) + x1
                            mid_y = (mid_y/2) + y1
                            print('CENTRO X:', mid_x)
                            print('CENTRO Y:', mid_y)
                            mid_x = mid_r_x - mid_x
                            mid_y = mid_r_y - mid_y
                            print('Distancia al centro y:', mid_x)
                            
                            x_serial = (mid_x * res_x)/mid_r_x
                            y_serial = (mid_y * res_y)/mid_r_y
                            
                            print('Pos_Proceso:', x_serial)                   
                            y_serial = int(y_serial)
                            x_serial = int(x_serial)
                            print('int y:', y_serial)
                            print('Coordenadas serial a enviar')
                            print ('x:',x_serial)
                            print ('y:', y_serial)
                            dato_txt = str(a) + ',' + str(b) + ',' + str(-x_serial) + ',' + str(-y_serial)
                            dato_txt = dato_txt.encode("ASCII")
                            controlador.write(dato_txt)
                            

controlador.close   #se cierra el controlador
sys.exit()          #exit script 




