#!/usr/bin/python
# -*- coding: utf-8 -*-

import struct
import sys
import threading
from time import sleep

from report import report
from serial import Serial

# Caracteres Especiales :

ESCAPE_CHAR = b'\x1B'
EXIT_CHAR   = b'X'
GET_CHAR    = b'G'
SET_CHAR    = b'S'
ACK_CHAR    = b'\x17'
NACK_CHAR   = b'\x15'

SpecialChar = [ESCAPE_CHAR, EXIT_CHAR, GET_CHAR, SET_CHAR, ACK_CHAR, NACK_CHAR]
EncodedChar = [ESCAPE_CHAR, EXIT_CHAR, GET_CHAR, SET_CHAR]
DecodedChar = [ESCAPE_CHAR, ACK_CHAR, NACK_CHAR]


class FacadeWrapperError(Exception):
  def __init__(self, msg, cause=None, obj=None) :
    super().__init__(self, msg)

    self.msg = msg

    if isinstance(cause, FacadeWrapperError):
        self.msg += '\nrazón : %s' % cause.msg

    elif isinstance(cause, Exception):
        self.msg += '\nrazón : %s' % cause.args[0]

    elif cause :
        self.msg += '\nrazón : %s' % cause.__str__()

    if obj: obj.log.error(msg)

    self.message = self.msg



class FacadeWrapper :
    """
    Protocolo de comunicación con dispositivos/micro-controladores con un interfaz serie,
    bajo mando de la PC (y que por ende actúa como maestro).
   
    El paradigma del protocolo es la escritura y lectura de valores identificados por su 
    dirección (16 bits), en la secuencia : orden / respuesta, iniciada siempre por la PC
    y respondida por el dispositivo. 
   
    Es natural asignar los valores a un espacio de memoria, el cual puede asignarse total o
    parcialmente a la RAM, FLASH y/o EEPROM, la distribución del asignamiento de memoria 
    queda bajo la entera responsabilidad del dispositivo remoto.
   
    En el protocolo cada byte trasmitido o es un identificador o un dato, los identificadores
    solo toman los valores GET ('G'), SET ('S'), ACK, NACK y ESC y se trasmiten siempre como 
    un byte del valor respectivo. Los datos por el contrario cuando su valor coincide con el 
    de un identificador se trasmiten como una secuencia de bytes (ESC seguido de 0x55^data), 
    de lo contrario con un un byte de su mismo valor. La traducción no es simétrica la PC
    esta obligada a traducir SET, GET y ESC, mientras que el dispositivo solo ACK, NACK y ESC.
   
    La orden de la PC consta del identificador SET/GET seguida de dos datos que representan
    el byte LSB y MSB de la dirección, un tercer dato representa el número de datos.  
   
    Si la orden es SET, la PC continua enviando el número de datos respectivo y corresponde
    al dispositivo responder con ACK o NACK, si el dispositivo acepto o no la orden.
   
    Si la orden es GET, el dispositivo continua con el envío del número de datos 
    especificado terminando con el identificador ACK. El dispositivo también puede 
    responder con NACK si no puede cumplir la orden.
   
    """

    def __xmit(self, data) :
      """
      Transmite 'data'. Si no puede hacerlo dentro del límite de tiempo
      establecido (writeTimeout) aborta la operación por medio de una
      excepción (del tipo FacadeWrapperError).
      """
      try :
         self.log.debug('Trasmitiendo : 0x%s' %data.hex().upper())
         for d in data :
          self.__comm.write(bytes([d]))
          #sleep(2/self.__comm.baudrate)
         if self.throughput_limit :
            sleep(0.05)

      except FacadeWrapperError as e:
         raise FacadeWrapperError('Fallo de Transmisión (timeout).', e, self)


    def __rcve(self) :
      """
      Espera por la recepción de 1 byte desde el dispositivo.
      """
      self.log.debug('Recibiendo (1 byte) ...')
      byte = self.__comm.read(1)

      if (byte == b'') or (byte is None) :
         raise FacadeWrapperError('El dispositivo no responde (timeout).',
                                                                    None, self)

      self.log.debug('Se recibió : 0x%s,' %(byte.hex().upper()))

      return byte


    def __RcveAns(self) :
      """
      Recibe e identifica la respuesta del dispositivo, devuelve TRUE/FALSE
      según responda ACK_CHAR o NACK_CHAR respectivamente.
      Termina con una excepción si no se recibe una respuesta o no puede ser
      identificada.
      """
      try :
         self.log.debug('Recibiendo la respuesta (ACK/NACK) ...')
         ans = self.__rcve()
      except FacadeWrapperError as e :
         raise FacadeWrapperError('El dispositivo no envió '
                               'la respuesta de aceptación/rechazo.', None, self)

      if  ans == NACK_CHAR :
         self.log.debug('Respuesta de Rechazo (NACK).')
         return False
      elif ans == ACK_CHAR :
         self.log.debug('Respuesta de aceptación (ACK).')
         return True

      raise FacadeWrapperError('El dispositivo envió una '
                                         'respuesta no reconocible.', None, self)


    def __RcveData(self, size) :
      u"""
      Recibe size bytes de datos y los devuelve. La secuencia de datos pueden
      incluir secuencias de escape (caso en el cual solo se considera en la
      cuenta como un dato, aún cuando su transmisión implica 2 bytes), la
      secuencia de bytes que representan los datos debe terminar con un byte
      de respuesta. Este último debe ser ACK_CHAR si se transmitieron los size
      datos o NACK si la transmisión es parcial o nula.
      Levanta una excepción si el dispositivo devuelve NACK_CHAR, o si la
      transmisión es parcial o nula (timeout) o se recibe una secuencia de
      escape inválida.
      """
      try :
         self.log.debug('Esperando la recepción de %d (data) bytes' % size)
         data = bytearray(b'')
         for i in range(0, size) :
            byte = self.__rcve()

            if byte == ESCAPE_CHAR :
               byte = (self.__rcve()[0] ^ ESCAPE_CHAR[0] ^ 0x55).to_bytes(1, 'little')

               if not (byte in DecodedChar) :
                  self.log.debug('Secuencia de escape desconocida '\
                                         'ESC (0x1B) / 0x%02X' % ord(byte))
                  raise FacadeWrapperError('Se recibio una secuencia '
                                          'de escape desconocida', None, self)
               self.log.debug('Secuencia de escape identificada '
                                               'para : 0x%02X' % ord(byte))

            elif byte == ACK_CHAR :
               raise FacadeWrapperError('Se recibio ACK, truncando'
                              ' la recepción (%d en lugar de %d bytes).'
                                                   % ((i+1), size), None, self)

            elif byte == NACK_CHAR :
               raise FacadeWrapperError('Se recibió (NACK), interrumpiendo'
                                ' la recepción (a %d en lugar de %d bytes).'
                                                   % ((i+1), size), None, self)
            data += byte

         if not self.__RcveAns() :
            raise FacadeWrapperError('El dispositivo rechazo la lectura.',
                                                                    None, self)

         #return [b for b in data]
         return data

      except FacadeWrapperError as e :
         raise FacadeWrapperError('Fallo la Recepcion.', e, self)


    def __encodeData(self, data_bytes) :
      # En este punto data puede contener los caracteres especiales
      # que deben ser substituidos por sus secuencias de escape ...
      for ch in EncodedChar :
            data_bytes = data_bytes.replace(ch,
                                          b'\x1B' + bytes([0x1B ^ ord(ch) ^ 0x55]))
      # antes de enviarla :
      return data_bytes


    def getData(self, adr, size) :
      """
      Lee size bytes desde la dirección adr en el dispositivo y los devuelve
      como una lista.
      """
      with self._lock :

         try :
            self.log.debug('Lectura del contenido de %d bytes desde 0x%04X.' \
                                                                  %(size, adr))

            # Limpia la memoria de contención de recepción :
            self.__comm.flushInput()

            # Envía el comando según el protocolo, nótese que se asegura la con-
            #versión a una secuencia de bytes de los parámetros importados :
            cmd = GET_CHAR + self.__encodeData(struct.pack('<H', adr)
                                                         + struct.pack('<B', size))
            self.__xmit(cmd)

            # Se espera por la respuesta del comando :
            ans = self.__RcveData(size)

            return ans

         except FacadeWrapperError as e :
            raise FacadeWrapperError('No se pudo obtener el contenido de 0x%04X / 0x%02X bytes.'%(adr, size), e, self)


    def setData(self, adr, data, mode = 'byte') :
      """
      Escribe el contenido de data desde la dirección adr en el dispositivo,
      data puede ser una cadena de caracteres o una lista de bytes o un byte,
      o una palabra de 16 bits.
      En el caso de una cadena de caracteres o una lista de bytes el argumento
      mode es ignorado. Cuando data es un entero el parámetro mode controla
      si solo se consideran los primeros 8 bis (mode = 'byte') o los primeros
      16 bits (mode = 'word').
      La lista de bytes es en realidad una lista de enteros, en la que solo se
      consideran válidos los bytes LSB de c/u.
      """
      with self._lock :
         try :
            if isinstance(data, str) :
               data_bytes = data
            elif isinstance(data, int) :
               if mode in ['byte', 'uint8_t'] :
                  data_bytes = struct.pack('b', data)
               elif mode in ['word', 'uint16_t'] :
                  data_bytes = struct.pack('<H', data)
               elif mode in ['dword', 'uint32_t'] :
                  data_bytes = struct.pack('<I', data)
               elif mode in ['uint40_t'] :
                  data_bytes = struct.pack('<Q', data)
               else :
                  if (data < 0) or (data >= 1099511627776) :
                    raise ValueError('argument out of range')
                    sys.exit()

                  self.log.exception('SetData : Tercer argumento '
                                                           '(mode) inválido.')
            elif isinstance(data, list) :
               data_bytes = b''
               for item in data :
                  data_bytes += struct.pack('<B', item)
            elif isinstance(data, (bytes, bytearray)) :
               data_bytes = data
            else :
               raise ValueError('SetData : Primer argumento (data) no es '
                                 'un tipo válido (str, int o list de int).\n')

         except Exception as e:
            self.log.exception('SetData : Fallo inesperado al interpretar '
                                                'los argumentos, detalle :\n')
            raise e

         try :
            self.log.debug('Modificación del contenido de %d bytes '
                                      'desde 0x%04X.' %(len(data_bytes), adr))

            # Limpia la memoria de contención de recepción :
            self.__comm.flushInput()

            # Envía el comando según el protocolo, nótese que se asegura la con-
            # versión a una secuencia de bytes de los parámetros importados y se
            # asegura de substituir los caracteres especiales por sus secuencias
            # de escape :
            cmd = SET_CHAR + self.__encodeData(struct.pack('<H', adr) + struct.pack('B',
                                                     len(data_bytes)) + data_bytes)
            self.__xmit(cmd)

            # Se espera por la respuesta del comando :
            ans = self.__RcveAns()
            return ans

         except FacadeWrapperError as e :
            raise FacadeWrapperError(u'No se pudo modificar el contenido de '
                    u'0x%04X / 0x%02X bytes.' %(adr, len(data_bytes)), e, self)

    def open(self):
      """
      Abre el puerto serie, si no puede realizarse levanta la excepción FacadeWrapperError.
      """
      self.log.debug('Abriendo el puerto serie : %s', str(self.__comm))
      self.__comm.open()
      self.log.debug('El puerto %s esta preparado para la comunicación.' \
                     % self.__comm.port)
        
    def isOpen(self):
        """
        Devuelve el estado del puerto.
        """
        return self.__comm.isOpen()

    def close(self) :
      """
      Cierra el puerto serie.
      """
      self.__comm.close()
      self.log.debug('Se cerro el puerto serie : %s', str(self.__comm.port))

    def __enter__(self):
      """
      El interfaz puede utilizarse como un manejador de contexto.
      """
      self.open()
      return self

    def __exit__(self, type, value, traceback):
      self.close()


    def __init__(self, serial_port, throughput_limit = False, open = False) :
      """
      Encapsula el interfaz serial serial_port, para dotarlo de las operaciones
      de lectura y escritura con las especificaciones del protocolo.
      """
      # Cuando se utiliza el simulador de Proteus es necesario limitar el volumen de 
      # datos a transmitir, se define el atributo throughput_limit para definir si se 
      # limita o no el volumen de datos :
      self.throughput_limit = throughput_limit

      # Asigna directamente como el puerto de comunicaciones :
      self.__comm  = serial_port 

      # La instancia de la clase puede ser utilizada por mas de un hilo de ejecución,
      # por lo que tanto se utiliza un objeto Lock(), para prevenir conflictos, en los
      # métodos  públicos de escritura y lectura (SetData() y GetData()) :
      self._lock = threading.Lock()

      with self._lock :
        # Se abre el puerto serie :
        if open :
          self.__comm.open()
        else :
          self.__comm .close()
          
      # Se asigna el manejador de reportes :
      self.log = report.getLogger('FacadePort.' + self.__comm.port)
         
