#!/usr/bin/env python
# coding: utf-8

# ### Emulación y Fachada de Estructuras C
# 
# #### 1.- Introducción
# 
# 
# En general las variables compuestas en C son definidas como estructuras que resultan siendo arreglos ordenados de variables primitivas (char, int, long, etc.) en la memoria del microcontrolador. La funcionalidad del módulo provee dos modos de operación : <b><i>emulación</i></b> y <b><i>fachada</i></b>, en ambos caso se replica el <b><i>almacenamiento</i></b>, la sintaxis básica de acceso a sus sub-elementos y las operaciones aritméticas de las variables primitivas.
# 
# Sin embargo la funcionalidad de <b><i>fachada</i></b> implica además establecer una conexión con su 'alter ego' en un dispositivo (microcontrolador) remoto de manera que sus valores se mantengan sincronizados, i.e. su asignación en Python implica la de su actualización en la memoria del microcontrolador y viceverza cuando el se requiera el valor de su fachada. 
# 
# La emulación y fachada se realiza tanto en el <i>tipo</i> de datos como en el <i>almacenamiento</i>, ejem:
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#      typedef struct {                    class ab_t(typedef):
#         uint8_t  a    ;                     a = uint8_t
#         uint16_t b    ;                     b = uint16_t
#         uint24_t c[5] ;                     c = ArrayOf(uint24_t, 5)    
#         uint8_t *d    ;                     d = PointerTo(uint8_t, RAM_Memory)
#      } ab_t ;
# </samp>
# 
# circunstancialmente un tipo C es también un tipo Python<sup>*1</sup> y asi mismo a la instancia de una variable en C le corresponde la de la clase correspondiente en Python, ejem :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       ab_t ab ;                           ab = ab_t() 
# </samp>
#     
# El acceso a los elementos de las estructuras se realiza básicamente con la misma sintaxís en ambos, ejem.:
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       ab.a = 8 ;                          ab.a = 8  
#       ab.b = ab.a ;                       ab.b = ab.a
#       c[2] = 199                          c[2] = 199
# </samp>
# 
# Los vectores y punteros poseen constructores especializados (<i>ArrayOf</i> y <i>PointerTo</i>) en el caso de Python, mientras en el caso de vectores el acceso tiene la misma síntaxis en C y Python, para el caso de vectores no existe el operador especializado (<i>-></i>) en Python, y se utiliza el mismo operador '.', por ejemplo :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       ab->d = 65 ;                        ab.d = 65  
# </samp>
#     
# implicando que en Python no existe acceso directo al valor del puntero, por otro lado al definir un puntero <i>PointerTo(target, mem_class)</i>, no solo se asigna al tipo de estructura que apunta <i>target</i> sino el tipo de memoria <i>mem_classmem_class</i> en la que reside (<i>FLASH_Memory</i>, <i>RAM_Memory</i>, <i>EEPROM_Memory</i>)
#     
# El enlace con el dispositivo remoto presume la exitencia de un medio de comunicación con el dispositivo remoto operando con un protocolo dado (<i>Facade Protocol</i>), la clase <i>FacadeWrapper</i> implementa el protocolo en un puerto serie dado. Por ejemplo : <br>
# <p style="margin-left:1em;">
# <samp>  facade_port = FacadeWrapper(serial.Serial('COM4', 115200)) </samp>
# 
# La fachada de variables se realiza definiendo la memoria de enlace con el dispositivo  durante la creación de la instancia, por ejemplo :
# 
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#                                           facade_port = FacadeWrapper(serial.Serial('COM4', 115200)) 
#       ab_t ab @ 1000 ;                    ab = ab_t(memory=RAM_Memory(1000, facade_port)) 
# </samp>
#     
# la memoria asociada es una instancia de las clases <i>FLASH_Memory</i>, <i>RAM_Memory</i> o <i>EEPROM_Memory</i>, las que perse definen el tipo de la memoria ha asociar, sino invocanco con su direccíon y puerto de fachada a utiizar.
# <br>
# <br>
# <font size="2" color="blue">
# Nota *1 : Es decir <i>type(...) = type</i>.
#     
#     
# <br><br>
# <font size="2" color="red">
# 
# #### TO DO
# La implementación actual no provee la capacidad de definir la dirección de la variable apuntada por el puntero, la excepción es en el caso de utilizarse como fachada en que la dirección es actualizada en cada operación.
#     

# ####  2.- Tipos de Datos Primitivos
# 
# Las clases (tipos) derivadas de <i>Primitive_t</i>, estan orientadas a representar tipos básicos, i.e. que representan un único valor, no estan pensadas para instanciarse directamente<sup>*1</sup> sino solo como atributos (de clase) para representar los elementos respectivos de las estructuras C.  
# <br>
# <br>
# 
# <font size="2" color="blue">
# Nota *1 : Es una limitación impuesta por la forma de operación del interprete de Python, que en general durante la asignación <i> name = value </i>, name se cambia al tipo de <i>value</i>. Haciendo imposible (TO DO) mantener el tipo con la sintaxís estándar, y menos pensar que se dispare la actualización de su fachada.
# 
# 

# #### 2.1.- Tipos de Datos Estándar
# 
# Son tipos derivados <i>Primitive_t</i> se definen para emular los tipos estándar definidos en <i>stdint.h</i>, <i>stdbool.h</i>, <i>stdfract.h</i>. 
# Los nombres de los tipos son homónimos de sus correspondientes tipos en C (i.e. <i>uint8_t</i>, <i>int8_t</i>, etc.). 
# 
# La emulación también incluye su aritmética básica : suma , resta, conversión entre tipos. 
# 

# #### 2.2.- Punteros
# 
# El tipo (i.e. clase) de un puntero a una variable del tipo <b><i>target_t</i></b> se obtiene invocando el método <b><i>PointerTo(target_t, [FLASH | RAM | EEPROM]_Memory)</i></b>. Por ejemplo :
# 
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       typedef struct {                    class zen_t(typedef):
#          uint8_t* z_ptr ;                     z_ptr  = PointerTo(uint8_t, RAM_Memory)
#          const uint8_t* z_ptr ;               z_ptr  = PointerTo(uint8_t, FLASH_Memory)
#          uint16_t npool ;                     npool = uint16_t
#       } zen_t ;
# </samp>
#     
# y las instancias de ambos tipos :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       zen_t zen                           zen = zen_t()
# </samp>
#     
# Los punteros son tipos deribados de <i>Primitive_t</i> por lo tanto no pueden instanciarse sin un contenedor. 
#     

# #### 2.3.- Cadena de caracteres
# 
# En C existe el concepto de cadena de caracteres, como vectores del tipo <b><i>char</b></i> (<b><i>uint8_t</b></i>), con una sintaxis alterna para su asignación (diferente a la de los vectores), para emular funcionalidad se incluye la función (factoría) <b><i>CharArray_t(length)</b></i>, por ejemplo :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#      typedef struct {                    class ab_t(typedef):
#         char  a[10] ;                       a = CharArray_t(10)
#         uint16_t b ;                        b = uint16_t
#      } ab_t ;
#     
#      ab = ab_t()                          ab = ab_t()
#      ab.a = 'ABC'                         ab.a = 'ABC'
# </samp>
# 
# Los punteros son tipos deribados de <i>Primitive_t</i> por lo tanto no pueden instanciarse sin un contenedor. 

# #### 3.- Tipos de Datos Compuestros :
# #### 3.1.- Estructuras
# 
# Los tipos derivados, i.e. las subclases de, <b><i>typedef</i></b> son tipos que contienen (como atributos de clase) tipos de datos primitivos (subclases de <b><i>Primitive_t</i></b>) y/o también (otros) tipos de datos compuestos, es decir sus instancias emulan la conformación de estructuras en C. Por ejemplo :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#      typedef struct {                    class ab_t(typedef):
#         uint8_t  a ;                        a = uint8_t
#         uint16_t b ;                        b = uint16_t
#      } ab_t ;
#     
#      typedef struct {                    class foo_t(typedef):
#         ab_t     plus  ;                    plus  = ab_t
#         uint16_t extra ;                    extra = uint16_t
#      } foo_t ;
# </samp>
# 
# Nótese que obviamente el orden de definición es el mismo entre los elememtos en C y los atributos en Python. Así mismo a cada elemento le corresponde un atributo cuyo tipo es el equivalente en C.
# 
# El ejemplo anterior también muestra como manejar formalmente el caso de estructuras anidadas, en este caso las sub-estructuras quedan definidas en forma explícita y no anónima. Sin embargo puede utilizarce la función <b>Struct_t(dict_fields)</b> y realizarce en foma anónima :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :    
#      typedef struct {                    class foo_t(typedef):
#         struct {                            plus = CStruct({'a':uint8_t, 'b':uint16_t})
#           uint8_t  a ;                      extra = uint16_t
#           uint16_t b ;                      
#         } plus  ;                           
#         uint16_t extra ;                    
#      } foo_t ;
# </samp>
# 
# En ambos casos, C y Python, <i>foo_t</i> es un tipo (type), y no la instancia de una variable o clase, la cual se define como es usual para cada lenguaje <sup><b>*1<i></i></b></sup>, ejem.:
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#      foo_t foo ;                             foot = foo_t()
# </samp>
#     
#     
# <font size="2" color="blue">    
# Nota *1 : Extrictamente, la instancia foo_t() no es una instancia de la clase <i>foo_t</i>, sino de una clase denominada <i>FacadeOf&#60;foot_t></i>, que es la clase en la cual sus atributos son instancias de los atributos de <i>foo_t</i>.

# #### 3.2.- Vectores
# 
# El tipo (i.e. clase) de un vector de <i>length</i> elementos del tipo <i>pattern_t</i> se obtiene invocando el método <b><i>ArrayOf( pattern_t, length )</i></b>. Por ejemplo :
# 
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       typedef uint8_t bar_t[10]           bar_t = ArrayOf(uint8_t, 10)
# </samp>
#     
# y las instancias de ambos tipos :
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#       bar_t bar                           bar = bar_t()
# </samp>
#     
# El acceso a los elementos de los vectores tiene la misma sintaxís en ambos lenguajes, ejem. <samp>bar[5]</samp>

# #### <i>4.- Sincronización con un Dispositivo Remoto</i>
# 
# El objetivo de este módulo no es solo emular la asignación de memoria y la sintaxis de manejo de estructuras C, sino principalmente la manipulación de variables almacenadas en dispositivos remotos (microcontroladores) cuyo programa fue escrito en C.
# 
# La funcionalidad de la capacidad de lectura y escritura en el dispositivo remoto puede ser utilizada para confirgurar, verificar la operación, obtener registros de captura de datos, etc.
# 
# A la funcionalidad de utilizar la misma sintaxis que la utilizada en C para efectuar estas operaciones en el dispositivo remoto se le denomina <i>Fachada</i>.
# 
# #### <i>4.1- Protocolo de Fachada</i>
# 
# La clase <i>FacadeWrapper</i> encapsula un puerto serie para utlizarlo como medio de comunicación con el dispositivo remoto ejecutando el protocolo establecido (Facade Protocol).
# 
# El objetivo principal de la clase es proveer los métodos <i>getData</i> y <i>setData</i> para leer y escribir un número determinado de bytes desde una dirección dada, bajo el protocolo adhoc de fachada.
# 
# Aunque el <i>Protocolo de Fachada</i> tiene los métodos <i>open</i> y <i>close</i>, es preferible utilizarlo como un manejador de contexto de manera que se asegura su cierre automáticamente a un en caso de error, por ejemplo :
# <p style="margin-left:1em;">
# <samp>
# facade_port = FacadeWrapper(serial.Serial('COM4', 115200, open=false<sup><b>*1<i></i></b></sup>))
# with facade_port as port :
#     data = port.getData(0x1000, 5)
# </samp>
#     
# #### <i>4.2- Vinculo con el Dispositivo Remoto</i>
# 
# Las instancias de la clase <b><i>FacadeMemory</i></b> implementan el vínculo de una variable con el dispositivo remoto, su objetivo principal es proveer las funciones de lectura y escritura adhoc para la memoria asociada en el dispositivo remoto. 
# 
# Durante la creación de sus instancia se asocian la dirección de la variable a asociar y el puerto de fachada, es decir su constructor se invoca con los parámetros siguientes :
# <p style="margin-left:2em;">
# <i>port</i> : define el puerto de fachada de comunicaciones. <br>
# <i>address</i> : direccion base (de referencia) de la ubicación de la variable en la memoria del dispositivo remoto.<br>
#     
# y opcionalmente :
# <p style="margin-left:2em;">
# <i>volatil</i> : volatilidad, i.e. si el contenido puede variar independientemente en el dispositivo remoto, esto implica que cuando es volatíl (<i>volatil = True</i>), cada lectura implica obtener su valor desde el dispositivo remoto, en caso contrario (<i>volatil = False</i>) el valor es obtenido del valor interno (cache) espejo del valor remoto. <br>  
# 
# Como una facilidad para asociar los sub-elementos de una variable con su respectivo vínculo, la instancia del contenedor puede invocarse (<i>\_\_call\_\_</i>) cuyo parámetro es la ubicación relativa (offset) del sub-elemento.
# 
# #### <i>4.3- Asociacion de las variables con su vínculo (con el dispositivo remoto)</i>
# 
# Durante la creación de las instancias de las variables se asocian al vínculo importandolo como el parámetro nominado  <i>link</i>, ejem :
# 
# <p style="margin-left:1em;">
# <samp>  En C :                              En Python :
#                                           facade_port = FacadeWrapper(serial.Serial('COM4', 115200)) 
#       ab_t ab @ 1000 ;                    ab = ab_t(link=Bind(facade_port, 1000)) 
# </samp>
#         
# Durante la creación de la instancia se crean vicnculos para sus sub-elementos en forma automática, de esta manera se puede realizar operaciones de lectura y escritura parciales de sus sub-elementos.
# 
# <font size="2" color="blue">    
# Nota *1 :Por defecto Serial abre el puerto cuando se crea su instancia, la opción <i>open=false</i> evita abrir el puerto, de manera que su instancia puede crearse aún cuando el puerto no este disponible. 
# 
# 

# #### Memoria de Contención y Fachada del Almacenamiento Remoto
# 
# La clase <i>Cache</i> encapsula el valor canónico (i.e. la secuencia de bytes que representa el valor) de las variables primitivas o compuestas y sirve como memoria de conteción (espejo) y fachada de sus valor alamcenda en un dispositivo remoto.  
# 
# Existen dos formas de invocar su constructor, el primer parámetro es siempre el enlace (<i>class Link</i>) asociado con la variable que provee los parámetros de comunicación con el dispositivo remoto, y el segundo parámetro siempre es nominado, para el cual hay dos opciones :
# <p style="margin-left:2em;">
# <i>length</i>  : para el caso de asociarse a variables primitivas, en cuyo caso es el número de bytes de su representación canónica.<br>
# <i>cache_list</i> : para el caso de asociarse a variables compuestas, es una lista de las instancias de <i>Cache</i> asociadas a sus sub-variables.<br>
# 
# Sus atributos son :
# <p style="margin-left:2em;">
# <i>link</i> : define su asociación (puerto, dirección, longitud y volatilidad) con el dispositivo remoto.<br>    
# <i>length</i> : es la longitud de su valor canónico o la suma de las longitudes de sus elementos.<br>  
#     
# Opcionalmente segun la variable asociada sea primitiva o compuesta se definen (en forma excluyente) :
# <p style="margin-left:2em;">
# <i>__cache__</i> : el valor canónico de la variable primitiva, al que se tiene acceso por medio de la propiedad de solo lectura <i>cache</i>.<br>    
# <i>cache_list</i> : la unión de los valores canónicos de las sub-variables de la asociada compuesta.
#     
# Finalmente el valor canónico local y el almacenado en el dispositivo remoto se leen y escriben por medio de los métodos <i>read</i> y <i>write</i> respectivamente.
# 
# Es una clase de soporte, no esta destinada para ser usada por el código usuario directamente, intermedia y optimiza la lectura y escritura de los valores canónicos de la variable/variables asociadas. Para el caso de variables no volátiles, permiten evitar el uso del interfaz de comunicación, evitando lecturas redundantes, al usarse como espejo y/o memoria de contención de los valores en el dispositivo remoto. Por otro lado en el caso de variables compuestas (aka. estructuras, vectores) intermedian para utilizar el interfaz en una operación general de lectura/escritura, mientras se sincronizan los espejos de cada sub-elemento, evitando su uso del interfaz para cada elemento de la variable compuesta.
# 

# #### Configuración de la Fachada 
# 
# Como el <i>Protocolo de Fachada</i> asigna un espacio de memoria limitado a 65536 bytes (2 bytes para la dirección) y por otro lado el microcontrolador puede contener diferentes espacios de memoria (FLASH, RAM, EEPROM) independientes y en consecuencia con rangos de dirección superpuestos, se hace necesario segmentar el espacio de memoria del protocolo y reasignarlo a cada tipo de memoria.
# 
# <b><i>MemoryConfig</i></b> es una (clase, namedtuple en particular) que almacena los parámetros de asignación, su atributo <b><i>offset</i></b> indica la dirección de protocolo asignada al rango del tipo de memoria a asignar, sus atributos restantes <b><i>start</i></b> y <b><i>final</i></b>, asignan el rango de direcciones a asignar. 
# 
# 
# #### Emulación de la EEPROM
# 
# Para microcontroladores que no poseen EEPROM, esta suele emularse en un rango dado de la memoria FLASH, cuyo inicio se define en EMULATED_EEPROM_ADDRESS (el rango es definido por su correspondiente atributo <i>MemoryConfig</i>). 
# 
# 
# #### Clase FacadeConfig
# 
# Es en la clase <b><i>FacadeConfig</i></b> en la que se definen estos parámetros, por defecto se ha definido la asignación de memmoria estándar del protocolo, y la dirección de emulación de memoria EEPROM estándar utilizada en el PIC16F1619.
# 
# 
# #### Compilador
# 
# El compilador (<i>C_compiler</i>) define como operan los punteros, es decir como se asigna su valor a la memoria a la memoria FLASH, RAM o EEPROM, es básicamente una desición de diseño del compilador, dependiente del tipo/modelo de microcontrolador y/o modos de operacón dados. La conversión entre el valor númerico del puntero y la dirección a la que se asigna según su tipo es definida por la función <i>to_adr(val, memory_class)</i> de la clase correspondiente. 
# 
# 
# Ambos <b><i>FacadeConfig</i></b> y <b><i>C_compiler</i></b> deben definirse (modificarse en realidad) antes de crear instancias de fachadas. Por defecto estan definidas para operar con el protocolo estándar y EEPROM emulada (a partir de 0x1F00) la primera y para la conversión de punteros para el compilador XC8.
# 

# In[1]:


from collections import namedtuple

MemoryConfig = namedtuple('MemoryConfig', ['offset', 'start', 'final'])

class FacadeConfig:
    """ Describe la asignación del espacio de 2**16 bytes para cada tipo
        de memoria.
    """
    FLASH_SPACE  = MemoryConfig(0x0000, 0x0000, 0x1DFF)
    RAM_SPACE    = MemoryConfig(0xE000, 0x0000, 0x0FFF)
    EEPROM_SPACE = MemoryConfig(0xF000, 0x0000, 0x0FFF)
    
    EMULATED_EEPROM_ADDRESS = 0x1F00
   


# In[2]:


class XC8:
    """ Define como asigna el espacio de direcciones entre la RAM y FLASH
    """
    @classmethod
    def to_adr(cls, ptr_val, memory_class):
        if memory_class == RAM_Memory:
            if ptr_val < 0x8000:
                if ptr_val <= FacadeConfig.RAM_SPACE.final :
                    return ptr_val
                raise ValueError('Valor del puntero (0x{:04X}) fuera de rango ([0x{:04X} - 0x{:04X}]).'.format(ptr_val, FacadeConfig.RAM_SPACE.start, FacadeConfig.RAM_SPACE.final))
               
            raise ValueError('El valor del puntero (0x{:04X}) no apunta al tipo de memoria requerido ({:s}).'.format(ptr_val, memory_class.__name__))
             
        elif memory_class == FLASH_Memory :
            if ptr_val >= 0x8000:
                if (ptr_val - 0x8000) <= FacadeConfig.FLASH_SPACE.final :
                    return ptr_val - 0x8000
                raise ValueError('Valor del puntero (0x{:04X}) fuera de rango ([0x{:04X} - 0x{:04X}]).'.format(ptr_val, FacadeConfig.FLASH_SPACE.start, FacadeConfig.FLASH_SPACE.final))
                
            raise ValueError('El valor del puntero (0x{:04X}) no apunta al tipo de memoria requerido ({:s}).'.format(ptr_val, memory_class.__name__))
             
        elif memory_class == EEPROM_Memory :
            if ptr_val >= 0x8000:
                if (ptr_val >= (0x8000 + FacadeConfig.EMULATED_EEPROM_ADDRESS)) and (ptr_val <= (0x8000 + FacadeConfig.EMULATED_EEPROM_ADDRESS + FacadeConfig.EEPROM_SPACE.final)) :
                    return ptr_val - 0x8000 - FacadeConfig.EMULATED_EEPROM_ADDRESS
                raise ValueError('Valor del puntero (0x{:04X}) fuera de rango ([0x{:04X} - 0x{:04X}]).'.format(ptr_val, FacadeConfig.EEPROM_SPACE.start, FacadeConfig.EEPROM_SPACE.final))
                
            raise ValueError('El valor del puntero (0x{:04X}) no apunta al tipo de memoria requerido ({:s}).'.format(ptr_val, memory_class.__name__))
            
        raise ValueError('Clase de Memoria desconocida.')     
    

C_compiler = XC8    


# In[3]:


from FacadeWrapper import *

class FacadeMemory:
    def __init__(self, base_address, port, volatil=True) :
        self.__adr__ = base_address
        self.__port__ = port
        self.__volatil__ = volatil
        self.__updated__ = False
        self.__offset__ = 0
        self.__compiler__ = C_compiler
        
            
    def __add__(self, other) :
        mem = self.__class__(self , self.__port__, volatil = self.__volatil__)
        mem.__offset__ = int(other)
        return mem
    
    @property
    def __address__(self) :
        if isinstance(self.__adr__, FacadeMemory) :
            return self.__adr__.__address__ + self.__offset__
        
        return self.__adr__ + self.__offset__
        
    def __retrieve__(self, length):
        if not self.__updated__ :
            return self.__port__.getData(self.__address__ + self.PROTOCOL_OFFSET.offset, length)            
        
    def __store__(self, data):
        if not self.__port__.setData(self.__address__ + self.PROTOCOL_OFFSET.offset, data) :
            raise FacadeWrapperError("El dispositivo no acepto el cambio.")
        self.__updated__ = not self.__volatil__


class PointerMemory(FacadeMemory) :
    def __init__(self, base_address, port, volatil=True) :
        super().__init__(base_address, port, volatil=True)
        
    @property
    def __address__(self) :
        b_adr = self.__read__()
        return self.__compiler__.to_adr(b_adr, self.__class__.__memory_class__)


class FLASH_Memory(FacadeMemory):
    PROTOCOL_OFFSET = FacadeConfig.FLASH_SPACE

class RAM_Memory(FacadeMemory):
    PROTOCOL_OFFSET = FacadeConfig.RAM_SPACE
        
class EEPROM_Memory(FacadeMemory):
    PROTOCOL_OFFSET = FacadeConfig.EEPROM_SPACE
    
    
class Unallocated_Memory(FacadeMemory):
    def __init__(self):
        pass
    
    def __call__(self, *args, **kwargs):
        return Unallocated_Memory()
    
no_memory = Unallocated_Memory()    


# In[4]:


from collections import OrderedDict, namedtuple

class CType_Meta(type):
    # Prepara para mantener el orden de definición de los atributos de clase.
    @classmethod
    def __prepare__(cls, name, bases):
        return OrderedDict()
        
       
class CType_t(metaclass=CType_Meta):
    """ Ctype_t es la clase abstracta para los elementos simples o compuestos, 
        tecnicamente es un descriptor de manera que el acceso a los elementos
        se realiza utilizando la notación 'dot' (punto).
        
        Provee los métodos de lectura (__read__) / escritura (__write__) con 
        las que se actualiza la memoria de contención de su valor binario 
        (__cahe__) con la del almacenamiento remoto, a la vez que se realiza 
        la conversión enntre el valor natural y su representación binaría.  
        
        Las subclases deben implementar los siguientes métodos :
        
            to_canonical y to_custom, que proveen la convesión entre el valor 
            representado - binario y viceverza respectivamente. 
        
            __len__ que devuelve el número de bytes utilizados para su 
            almacenamiento (de la memoria de contención y remota().
            
        Su contructor toma un solo argumento nominal (memory) instancia de la 
        clase FacadeMemory, la que sirve de enlace con el almacenamiento en 
        el dispositivo remoto.
    """
    def __new__(cls, **kwargs):
        cls_name = 'FacadeOf<{:s}>'.format(cls.__name__)
        cls_dict = kwargs.pop('cls_dict', dict(vars(cls)))
        clsobj = type(cls_name, cls.__bases__, cls_dict)

        inst = super().__new__(clsobj)
        inst.__init__(**kwargs)
        return inst

    def __init__(self, **kwargs) :
        memory = kwargs.get('memory', no_memory)
        self.__memory__ = memory
        self.__length__ = len(self)

    def __get__(self, instance, cls) :
        return self
        
    def __set__(self, instance, value) :
        self.__write__(value)
        
    def __read__(self) :
        self.__cache__ = self.__memory__.__retrieve__(self.__length__)
        return self.to_custom(self.__cache__)

    def __write__(self, value):
        if isinstance(value, (CType_t,)) :
            value = value.__read__()

        field_cnt = 1 if isinstance(self, (Primitive_t,)) else len(self.__fields__)
        value_cnt = len(value) if isinstance(value, (list, tuple)) else 1 
        if field_cnt != value_cnt :
            raise ValueError('El número de elementos es diferente.')
            
        canonical = self.to_canonical(value)
        self.__memory__.__store__(canonical)             
        self.__cache__ = canonical


# In[5]:


class Primitive_t(CType_t):    
    """ Primitive_t es una clase abstracta para los elementos que almacenan un valor único, 
        su memoria de contención __cache__ se almacena explícitamente (en __mirror__). 
    """
    def __init__(self, **kwargs) :
        self.__mirror__ = b'\x00'*len(self)
        super().__init__(**kwargs)

    def __len__(self) :
        return (self.__BIT_LEN__+7)//8
    
    def __get__(self, instance, cls) :
        return self.__read__()
    
    @property
    def __cache__(self):
        return self.__mirror__
    
    @__cache__.setter
    def __cache__(self, bin_value):
        self.__mirror__ = bin_value
                        


# In[6]:


from functools import reduce

class uint_t(Primitive_t) :    
    def to_canonical(self, custom_val):
        # TO DO completar con ceros si es necesario 
        try :
            return custom_val.to_bytes((self.__BIT_LEN__ + 7)//8, 'little')
        except :
            return int(custom_val).to_bytes((self.__BIT_LEN__ + 7)//8, 'little')
        
    def to_custom(self, canonical_val):
        return reduce(lambda a,b : a*256+b, reversed(self.__mirror__))

    def __str__(self) :
        return '{0:d}[0x{1:s}]'.format(self.to_custom(self.__mirror__), self.__mirror__.hex())
    
class int_t(uint_t) : 
    def to_canonical(self, custom_val):
        if custom_val < 0 :
            custom_val += 2**(self.__BIT_LEN__)
            
        return super().to_canonical(custom_val)

    def to_custom(self, canonical_val) :
        custom = super().to_custom(canonical_val) 
        if custom >= 2**(self.__BIT_LEN__ - 1) :
          custom -= 2**(self.__BIT_LEN__)
        return custom
    
class uint8_t(uint_t):
    __BIT_LEN__ = 8
    
class uint16_t(uint_t):
    __BIT_LEN__ = 16
       
class uint24_t(uint_t):
    __BIT_LEN__ = 32
    
class uint32_t(uint_t):
    __BIT_LEN__ = 32

class uint35_t(uint_t):
    __BIT_LEN__ = 35

class uint40_t(uint_t):
    __BIT_LEN__ = 40
    
class int8_t(int_t):
    __BIT_LEN__ = 8
    
class int16_t(int_t):
    __BIT_LEN__ = 16
       
class int24_t(int_t):
    __BIT_LEN__ = 32
    
class int32_t(int_t):
    __BIT_LEN__ = 32

class int35_t(int_t):
    __BIT_LEN__ = 35
    
class int40_t(int_t):
    __BIT_LEN__ = 50
    
    
class float24_t(Primitive_t):
    import struct
    __BIT_LEN__ = 24
    
    def to_canonical(self, custom_val):
        return struct.pack('<f', custom_val)[1:]
    
    def to_custom(self, canonical_val):
        return struct.unpack('<f', b'\x00' + canonical_val)[0]
    


# In[7]:


class Pointer_t( Primitive_t, PointerMemory):
    """ Pointer_t es la clase base de la que se derivan los elementos que sirven como punteros, 
        estas últimas son en si clases adhoc, provistas por el método factoría PointerTo.
    
        En python no existen el operador '->' de referencia indirecta, por lo que se continua 
        utilizando el operdor 'dot' (punto). El efecto colateral es que el acceso al valor del
        puntero debe obtenerse con métodos indirectos. SetTargetAdr y GetTargetAdr, 
    """
    __BIT_LEN__ = 16

    def __new__(cls, **kwargs) :
        memory = kwargs.get('memory', no_memory)

        cls_dict = dict(vars(cls))
        kwargs['cls_dict'] = cls_dict
        self = super().__new__(cls, **kwargs)
        
        target_memory = cls.__memory_class__(self, memory.__port__, volatil = memory.__volatil__)
        target_inst = cls.__target__(memory = target_memory)
        #cls.__target__ = target_inst
        self.__class__.__target__ = target_inst
        
        Primitive_t.__init__(self, memory=memory)
        PointerMemory.__init__(self, memory.__adr__, memory.__port__, memory.__volatil__)
        return self
    
            
    def __get__(self, instance, cls) :   
        if issubclass(self.__target__.__class__, Primitive_t) :
            return self.__target__.__read__()
        return self.__target__

    def __set__(self, instance, value) :     
        return self.__target__.__write__(value)

    def to_canonical(self, custom_val):
        return bytes([int(custom_val % 256), int(custom_val//256)])
        
    def to_custom(self, canonical_val):
        return canonical_val[0] + 256*canonical_val[1]



def PointerTo(target_t, memory_class):
    cls = type('PointerTo<{:s}>'.format(target_t.__name__), (Pointer_t,), {'__target__' : target_t, 
                                                                           '__memory_class__' : memory_class})
    return cls


# In[8]:


class String_t(Primitive_t) :
    def to_canonical(self, custom_val):
        canonical = custom_val if isinstance(custom_val, (bytearray, bytes)) else custom_val.encode()
        canonical = canonical[:self.__BIT_LEN__ // 8] + b'\x00'*(self.__BIT_LEN__ // 8 - len(canonical))
        return canonical
    
    def to_custom(self, canonical_val):
        return canonical_val.decode()
    
def CharArray_t(length):
    return type('String[{:d}]_t'.format(length), (String_t,) , {'__BIT_LEN__' : length*8})


# In[9]:


def name_fix(name):
    return name.replace('<', '_').replace('>', '').replace('[', '_').replace(']', '').replace('__', '')

class typedef(CType_t):          
    def __new__(cls, **kwargs) :
        memory = kwargs.get('memory', no_memory)
        
        field_offset, fields, cls_dict = 0, [], dict(vars(cls))
        for key, val in cls_dict.items() :
            if isinstance(val, (type,)) and issubclass(val, CType_t) :
                cls_dict[key] = val(memory = memory + field_offset)
                field_offset += len(cls_dict[key])
                
        kwargs['cls_dict'] = cls_dict
        return super().__new__(cls, **kwargs)
        
    def __init__(self, **kwargs):
        self.__fields__ = {name: typ  for name, typ in vars(self.__class__).items() if isinstance(typ, (CType_t,)) }
        
        tuple_name = name_fix(self.__class__.__name__)
        field_names = [name_fix(f_n) for f_n in self.__fields__.keys()]
        self.custom_format = namedtuple(tuple_name, field_names)
        
        super().__init__(**kwargs)
                    
    def __len__(self) :
        return sum(len(f) for f in self.__fields__.values())
    
    @property
    def __cache__(self):
        cache = bytearray()
        for field in self.__fields__.values():
            cache += field.__cache__
        return bytes(cache)
    
    @__cache__.setter
    def __cache__(self, bin_value):
        bin_value = bytearray(bin_value)
        for field in self.__fields__.values() :
            field.__cache__ = bin_value[:len(field)]
            bin_value[:len(field)] = b''        
    
    def to_canonical(self, custom_val):
        return b''.join([f.to_canonical(v) for f, v in zip(self.__fields__.values(), custom_val)])
        
    def to_custom(self, canonical_val) :
        canonical_val = bytearray(canonical_val)
        custom = []
        for e in self.__fields__.values() :
          custom.append(e.to_custom(canonical_val[:len(e)]))
          canonical_val = canonical_val[len(e):]
            
        return tuple(custom)

    def __read__(self) :
        return self.custom_format(*super().__read__())
        
    def __str__(self) :
        return str(self.__read__())
                          
   
def read(var) :
    return var.__read__()

                          
def CStruct(dict_fields, tag=None) :
    return type('_anon_structure' , typedef, dict_fields)                              
                          


# In[10]:


class Array_t(typedef):
    def __getitem__(self, idx) :
        return getattr(self, '__elem[{:d}]__'.format(idx))

    def __setitem__(self, idx, value) :
        setattr(self, '__elem[{:d}]__'.format(idx), value)
        
    def __read__(self) :
        tuple_name = self.__class__.__name__.replace('<', '_').replace('>', '_').replace('[', '_').replace(']', '_')
        names = list('e{:d}'.format(n) for n, _ in enumerate(self.__fields__.values()))
        values = (e.__read__() for e in self.__fields__.values())
        return namedtuple(tuple_name, names)(*values)
    
    
def ArrayOf(pattern_t, length):
    cls = type('ArrayOf_{:s}'.format(pattern_t.__name__), (Array_t,) ,
               dict(('__elem[{:d}]__'.format(n), pattern_t) for n in range(length)))
    return cls
   
                          

