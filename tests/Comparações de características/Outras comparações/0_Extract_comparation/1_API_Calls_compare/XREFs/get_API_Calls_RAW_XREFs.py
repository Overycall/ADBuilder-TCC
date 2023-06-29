import os, sys, stat
import pandas as pd
import os, sys, stat ,hashlib
import pandas as pd
import re
import networkx as nx
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis.analysis import ExternalMethod
from androguard.misc import AnalyzeAPK
from androguard import *
from androguard.core.analysis import *
import argparse
import zipfile as zp



def parseArgs():
    parser = argparse.ArgumentParser(description='A program modifying an APK to load Ronin shared library.')
    parser.add_argument('-a', dest='apk', required=True, help='Path to the APK file to be analysed.')
    return parser.parse_args()


def get_caracteristicas(args):

    f = open(args.apk, 'rb')
    contents = f.read()

               
        
    sha256 = hashlib.sha256(contents).hexdigest()
    
    app,d,dx   = AnalyzeAPK(args.apk)
    apicalls = []
    treatments = []

    cg = dx.get_call_graph()

    comuns_methods = [".equals()", ".hashCode()", ".toString()", ".clone()", ".finalize()", ".wait()",
                 ".print()", ".println()"]
    

    """
    implementação baseada na documentação
    https://github.com/androguard/androguard/issues/685
    """	  

    def get_api_calls_RAW_XREFs(dx):
        with open("API_Calls_Androguard_RAWs.txt", "w") as f:
            with open("API_Calls_Androguard_XREFs.txt", "w") as file:
                for method in dx.get_methods():
                    f.write(str(method) + "\n")
                    # Métodos XREF_FROM
                    for _,call, _ in method.get_xref_from():
                        package = call.class_name.replace(';','')
                        if not call.name.endswith(">"):
                                #cria lista formatada ex.: Landroid/support/design/internal/BaselineLayout.onLayout()
                                lista_api_calls =["{}.{}()".format(package, call.name)]
                                for i in lista_api_calls:
                                    file.write(str(i) +"\n")                                           
                                            
                    for _,call, _ in method.get_xref_to():      # Métodos XREF_TO
                        package = call.class_name.replace(';','')
                        if not call.name.endswith(">"):
                            #cria lista formatada ex.: Landroid/support/design/internal/BaselineLayout.onLayout()
                            lista_api_calls =["{}.{}()".format(package, call.name)]
                            for i in lista_api_calls:
                                file.write(str(i) +"\n")
                                
        return apicalls              
	  
					
    def get_api_calls_3(dx):
        with open(sha256+"_API_Calls_Androguard_XREFs.txt", "w") as file:
            for method in dx.get_methods():
                # Métodos XREF_FROM
                for _,call, _ in method.get_xref_from():
                    package = call.class_name.replace(';','')
                    if not call.name.endswith(">"):
                            #cria lista formatada ex.: Landroid/support/design/internal/BaselineLayout.onLayout()
                            lista_api_calls =["{}.{}()".format(package, call.name)]
                            for i in lista_api_calls:
                                # remove as API Calls que contenham $[0-9]
                                cifra_aux = str(i)
                                call_treatment = re.findall(r'\$[0-9]+', cifra_aux)
                                if len(call_treatment) == 0:
                                    # adiciona todos o métodos contendo Ljava/lang/Class
                                    if "Ljava/lang/Class" in i:
                                        if i not in apicalls:
                                            apicalls.append(i)
                                            file.write(str(i) +"\n")
                                    
                                    # remover todos os Ljava/lang (métodos comuns da linguagem Java)
                                    if "Ljava/lang" not in i:
                                        comum_control = 0
                                        # remove métodos comuns aos Objetos Java
                                        for comum in comuns_methods:
                                            if i.endswith(comum):
                                                comum_control += 1                                
                                                # verificação de duplicatas
                                        if i not in apicalls:
                                            if comum_control == 0:
                                                apicalls.append(i)
                                                file.write(str(i) +"\n")
                                        
                                        
                for _,call, _ in method.get_xref_to():      # Métodos XREF_TO
                    package = call.class_name.replace(';','')
                    if not call.name.endswith(">"):
                        #cria lista formatada ex.: Landroid/support/design/internal/BaselineLayout.onLayout()
                        lista_api_calls =["{}.{}()".format(package, call.name)]
                        for i in lista_api_calls:
                            # remove as API Calls que contenham $[0-9]
                            cifra_aux = str(i)
                            call_treatment = re.findall(r'\$[0-9]+', cifra_aux)
                            if len(call_treatment) == 0:
                                # adiciona todos o métodos contendo Ljava/lang/Class
                                if "Ljava/lang/Class" in i:
                                    if i not in apicalls:
                                        apicalls.append(i)
                                        file.write(str(i) +"\n")
                                    
                                # remover todos os Ljava/lang (métodos comuns da linguagem Java)
                                if "Ljava/lang" not in i:
                                    comum_control = 0
                                    # remove métodos comuns aos Objetos Java
                                    for comum in comuns_methods:
                                        if i.endswith(comum):
                                            comum_control += 1                                
                                    # verificação de duplicatas
                                    if i not in apicalls:
                                        if comum_control == 0:
                                            apicalls.append(i)
                                            file.write(str(i) +"\n")
									  
        return apicalls              
	  
	#Utilizamos a funcao abaixo para obter os metodos que sao chamados pelo app
    def get_api_calls(cg):
        # criar arquivo txt para armazenar os metodos sem o tratamento (metodos crus)
        with open(sha256+"_API_Calls_Androguard_CG.txt", "w") as file:
            # percorerr vetor contendo as API Calls
            for node in cg.nodes:
                # armazena no txt os metodos crus
                file.write(str(node).strip("\n") + "\n")
                split = str(node).split(" ")
                split_v = str(split).split("(")
                split_v[0] = split_v[0] + "()"
                if split_v[0] not in apicalls:
                    apicalls.append(split_v[0])
                    # remove as API Calls que contenham $[0-9]
                    cifra_aux = split_v[0]
                    call_treatment = re.findall(r'\$[0-9]+', cifra_aux)
                    if len(call_treatment) == 0:
                        aux = str(split_v[0]).replace("\n", "").replace(";->", ".")
                        split = aux.split("(")
                        split[0] = split[0] + "()"
                        if ".access$" not in split[0]:
                            if "java/lang/Object.getClass()" in split[0]:
                                if split[0] not in treatments:
                                    treatments.append(split[0])
                            if "java/lang/Object" not in split[0]:
                                comum_control = 0
                                # remove métodos comuns aos Objetos Java
                                for comum in comuns_methods:
                                    if split[0].endswith(comum):
                                        comum_control += 1 
                                if comum_control == 0:
                                    if split[0] not in treatments:
                                        treatments.append(split[0])
        return treatments  
	  

    #apicalls_full = get_api_calls(cg)
    apicalls2 = get_api_calls_RAW_XREFs(dx)
    #apicalls_3 = get_api_calls_3(dx)

if __name__ == '__main__':
    # exeplo de uso no terminal digite python3 get_caracteristicas.py malwares
    # malwares remete ao nome da pasta onde estão os apks malwares
    args = parseArgs()
    get_caracteristicas(args)