<h1 align="center"> ADBuilder - TCC</h1>

<div style="display: flex; align-items: center; justify-content: center;">
<img src="tests/images/Brasil.png" alt="Bandeira do Brasil" width="50" height="50">
   <h3>Documentação em Português</h3>
<img src="tests/images/Brasil.png" alt="Bandeira do Brasil" width="50" height="50">
</div>


<h4 align="left"> Ferramenta automatizada para gerar um dataset de malwares em Android. A ferramenta passa por todas as etapas, incluindo: </h5>


- [x] Download de Aplicativos;
- [x] Extração de Features;
- [x] Rotulação dos Aplicativos;
- [x] Geração do Dataset.

[//]: # (ADBuilder: implementação completa e totalmente integrada da ferramenta. Todas as etapas e "firulas" devem estar incorporadas na ferramenta.)

[//]: # ()
[//]: # (### Ideias para a ferramenta)

[//]: # ()
[//]: # (1&#41; ser capaz de executar as etapas &#40;todas ou individualmente&#41; do processo de construção de um *dataset*:)

[//]: # (    -   Download do APK;)

[//]: # (    -   Extração de características &#40;+ Tratamento e validação das mesmas&#41;;)

[//]: # (    -   Rotulação dos APKs;)

[//]: # (    -   Construção do *dataset* &#40;+ Sanitização do *dataset*&#41;;)

[//]: # ()
[//]: # (2&#41; ser capaz de gerar arquivos de saída:)

[//]: # (    -   logs &#40;i.e., arquivos de texto&#41; contendo informações sobre o processamento, como:)

[//]: # (        -   tempo de download dos APKs;)

[//]: # (        -   tempo de extração dos APKs;)

[//]: # (        -   uso de CPU;)

[//]: # (        -   consumo de memória RAM;)

[//]: # (    -   um arquivo JSON para cada APK contendo os resultados da análise do VirusTotal;)

[//]: # (    -   um arquivo de texto para cada APK contendo chamadas de API &#40;extração crua&#41;;)

[//]: # (    -   um arquivo CSV para cada APK contendo todas as características;)

[//]: # (    -   um arquivo CSV para cada APK contendo os dados tratados e adequados para integrar ao *dataset* final;)

[//]: # (    -   o *dataset* final &#40;i.e., resultado final da ferramenta que contém a união de todos os CSVs de APKs&#41;;)

[//]: # ()
[//]: # (3&#41; ser capaz de oferecer opções de especificação para o usuário.)

[//]: # ()
[//]: # (4&#41; ser capaz de automatizar todo o processo de construção de um *dataset*.)

[//]: # ()
[//]: # (5&#41; possuir uma estrutura flexível para ser capaz de integrar mais funcionalidades, posteriormente.)
### Índice

* [Ambiente de Teste](#ambiente-de-teste)
* [Preparando o Ambiente (Linux)](#preparando-o-ambiente)
* [Parâmetros Disponíveis](#parametros-disponiveis)
* [Exemplo de Uso](#exemplo-de-uso)

<div id="ambiente-de-teste"/>

### 🖱️ Ambiente de Teste

A ferramenta foi testada e utilizada na prática nos seguintes ambientes:

Ubuntu 22.04 LTS
* Kernel = ``` 5.15.0-41 generic ```
* Python = ``` 3.10.4 ```
* Ferramentas: ``` curl, time, pandas (versão 1.3.5), androguard (versão 3.3.5), networkx (versão 2.2), lxml (versão 4.5), numpy (versão 1.22.3), Termcolor (versão 1.1.0), Pyfiglet (versão 0.8.post1), Requests (versão 2.22.0). ```

Ubuntu 20.04 LTS
* Kernel = ``` 5.10.16.3-microsoft-standard-WSL2 ```
* Python = ``` 3.8.10 ```
* Ferramentas: ``` curl, time, pandas (versão 1.3.5), androguard (versão 3.3.5), networkx (versão 2.2), lxml (versão 4.5), numpy (versão 1.22.3), Termcolor (versão 1.1.0), Pyfiglet (versão 0.8.post1), Requests (versão 2.22.0). ```

<div id="preparando-o-ambiente"/>

### ⚙️Preparando o ambiente (Linux)
Instalação do Git
```
sudo apt-get install git -y
```
Clone o Repositório
```
git clone https://github.com/Overycall/ADBuilder-TCC
```
Nós disponibilizamos um arquivo shell de setup que contém configurações de permissões e dependências necessárias. Portanto, para preparar o ambiente, basta executar o seguinte comando:
```
cd ADBuilder-TCC
./scripts/setup.sh
```

<div id="parametros-disponiveis"/>

### 📌 Parâmetros disponíveis:


```
--file = informa qual o arquivo .txt que contém os sha256 dos APKs que se deseja baixar e rotular (utilizar em conjunto com --download e --labelling).
--download (lista_de_sha256.txt) = realiza download de aplicativos obtidos pelo arquivo .txt fornecido.
-npd (processos) = insira um número inteiro (e.g., 5) de processos para download (por padrão é 1).
--extraction = extrai características dos aplicativos.
-npe (processos) = insira um número inteiro (e.g., 5) de processos de extração (por padrão é 1).
--labelling (lista_de_sha256.txt) = realiza a rotulação dos aplicativos obtidos pelo arquivo .txt fornecido.
--vt_keys (lista_de_chaves_API_virustotal.txt) = insira um arquivo com a chave de API do VirusTotal.
--building = gera o dataset final.
```

[//]: # (Os parâmetros *--download* e *--labelling* recebem uma lista *--file* contendo os sha256 dos APKs que se deseja baixar e rotular, respectivamente. Estas listas podem estar em qualquer lugar.)

[//]: # ()
[//]: # (O parâmetro *-vt_keys* recebe uma lista.txt contendo as chaves de API do VirusTotal. Esta lista pode estar em qualquer lugar.)

[//]: # ()
[//]: # (O parâmetro *-npd* e -*npe* recebe um número inteiro informando a quantidade de processos &#40;núcleos da máquina&#41; que serão utilizados para realizar a etapa de download e extração, respectivamente. Se não for definido esse parâmetro, o valor será setado em 1 processo, por padrão.)

***É possível rodar cada etapa separadamente ou em conjunto.***

<div id="exemplo-de-uso"/>

### 👨‍💻 Exemplo de uso
Entre no diretório principal:
```
cd ADBuilder-TCC
```
O seguinte comando executa todos módulos integrados. Basta passar os parâmetros que preferir:
```
python3 adbuilder.py --file inputs/androzoo/input_sha256.txt --download -npd 2 --extraction -npe 2 --labelling --vt_keys ./inputs/virustotal_api_keys.txt --building
```
É possível executar cada módulo individualmente, conforme exemplos de uso:
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt
python3 adbuilder.py --extraction
python3 adbuilder.py --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py --building
```
Também é possível executar os módulos de download e extração com mais de um processo, por exemplo:
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 (download com três processos)
python3 adbuilder.py --extraction -npe 3 (extração com três processos)
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 --extraction -npe 2 (download com três processos e extração com dois processos)

```
Por fim, é possível executar módulos em conjunto, conforme exemplos:
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 --extraction -npe 3 --building
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt --extraction
python3 adbuilder.py --extraction --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt --extraction --labelling --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py  --extraction --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt --building
```

***OBS1: Importante que cada usuário utilize sua própria chave de API, obtida pelo site do [AndroZoo](androzoo.uni.lu), para realizar o download dos APKs. Insira sua chave de API no arquivo: /inputs/androzoo/apikey_androzoo.txt***

***OBS2: Será disponibilizada uma chave de API para utilizar o serviço do VirusTotal. Porém, é importante que cada usuário utilize sua própria devido as limitações diárias.***

***OBS3: O dataset final é gerado na fila do módulo de geração, na pasta: queues/building/Final.***

---
---
---

<div style="display: flex; align-items: center; justify-content: center;">
<img src="tests/images/EUA.png" alt="USA Flag" width="50" height="50">
   <h3>English Documentation</h3>
<img src="tests/images/EUA.png" alt="USA Flag" width="50" height="50">
</div>


<h4 align="left"> Automated tool to generate a dataset of Android malware. The tool goes through all the steps, including: </h5>


- [x] App Download;
- [x] Features Extraction;
- [x] App Labelling;
- [x] Dataset Geration.

[//]: # (ADBuilder: implementação completa e totalmente integrada da ferramenta. Todas as etapas e "firulas" devem estar incorporadas na ferramenta.)

[//]: # ()
[//]: # (### Ideias para a ferramenta)

[//]: # ()
[//]: # (1&#41; ser capaz de executar as etapas &#40;todas ou individualmente&#41; do processo de construção de um *dataset*:)

[//]: # (    -   Download do APK;)

[//]: # (    -   Extração de características &#40;+ Tratamento e validação das mesmas&#41;;)

[//]: # (    -   Rotulação dos APKs;)

[//]: # (    -   Construção do *dataset* &#40;+ Sanitização do *dataset*&#41;;)

[//]: # ()
[//]: # (2&#41; ser capaz de gerar arquivos de saída:)

[//]: # (    -   logs &#40;i.e., arquivos de texto&#41; contendo informações sobre o processamento, como:)

[//]: # (        -   tempo de download dos APKs;)

[//]: # (        -   tempo de extração dos APKs;)

[//]: # (        -   uso de CPU;)

[//]: # (        -   consumo de memória RAM;)

[//]: # (    -   um arquivo JSON para cada APK contendo os resultados da análise do VirusTotal;)

[//]: # (    -   um arquivo de texto para cada APK contendo chamadas de API &#40;extração crua&#41;;)

[//]: # (    -   um arquivo CSV para cada APK contendo todas as características;)

[//]: # (    -   um arquivo CSV para cada APK contendo os dados tratados e adequados para integrar ao *dataset* final;)

[//]: # (    -   o *dataset* final &#40;i.e., resultado final da ferramenta que contém a união de todos os CSVs de APKs&#41;;)

[//]: # ()
[//]: # (3&#41; ser capaz de oferecer opções de especificação para o usuário.)

[//]: # ()
[//]: # (4&#41; ser capaz de automatizar todo o processo de construção de um *dataset*.)

[//]: # ()
[//]: # (5&#41; possuir uma estrutura flexível para ser capaz de integrar mais funcionalidades, posteriormente.)
### Índice

* [test environment](#test-environment)
* [Preparing the Environment (Linux)](#preparing-the-environment)
* [Available Parameters](#available-parameters)
* [Example of Use](#example-of-use)

<div id="test-environment"/>

### 🖱️ Test Environment

The tool has been tested and used in practice in the following environments:

Ubuntu 22.04 LTS
* Kernel = ``` 5.15.0-41 generic ```
* Python = ``` 3.10.4 ```
* Tools: ``` curl, time, pandas (version 1.3.5), androguard (version 3.3.5), networkx (version 2.2), lxml (version 4.5), numpy (version 1.22.3), Termcolor (version 1.1.0), Pyfiglet (version 0.8.post1), Requests (version 2.22.0). ```

Ubuntu 20.04 LTS
* Kernel = ``` 5.10.16.3-microsoft-standard-WSL2 ```
* Python = ``` 3.8.10 ```
* Tools: ``` curl, time, pandas (version 1.3.5), androguard (version 3.3.5), networkx (version 2.2), lxml (version 4.5), numpy (version 1.22.3), Termcolor (version 1.1.0), Pyfiglet (version 0.8.post1), Requests (version 2.22.0). ```

<div id="preparing-the-environment"/>

### ⚙️Preparing the Environment (Linux)
Git Installation
```
sudo apt-get install git -y
```
Cloning the repository
```
git clone https://github.com/Overycall/ADBuilder-TCC
```
We recommend that you use the setup.sh script to install the dependencies. To do this, run the following command:
```
cd ADBuilder-TCC
./scripts/setup.sh
```

<div id="available-parameters"/>

### 📌 Available Parameters:


```
--file = It informs which .txt file contains the sha256 of the APKs to be downloaded and labeled (to be used in conjunction with --download and --labelling).
--download (sha256_list.txt) = Downloads applications obtained from the provided .txt file.
-npd (processes) = Enter an integer number (e.g., 5) of download processes (by default, it is 1).
--extraction = Extracts features from the applications.
-npe (processes) = Enter an integer number (e.g., 5) of extraction processes (by default, it is 1).
--labelling (sha256_list.txt) = Performs the labeling of the applications obtained from the provided .txt file.
--vt_keys (VirusTotal_APIKEYS_list.txt) = Insert a file with the VirusTotal API key.
--building = Generates the final dataset.
```

[//]: # (Os parâmetros *--download* e *--labelling* recebem uma lista *--file* contendo os sha256 dos APKs que se deseja baixar e rotular, respectivamente. Estas listas podem estar em qualquer lugar.)

[//]: # ()
[//]: # (O parâmetro *-vt_keys* recebe uma lista.txt contendo as chaves de API do VirusTotal. Esta lista pode estar em qualquer lugar.)

[//]: # ()
[//]: # (O parâmetro *-npd* e -*npe* recebe um número inteiro informando a quantidade de processos &#40;núcleos da máquina&#41; que serão utilizados para realizar a etapa de download e extração, respectivamente. Se não for definido esse parâmetro, o valor será setado em 1 processo, por padrão.)

***It is possible to run each step separately or together.***

<div id="example-of-use"/>

### 👨‍💻 Example of Use
Enter the main directory:
```
cd ADBuilder-TCC
```
The following command runs all integrated modules. Just pass the parameters you prefer:
```
python3 adbuilder.py --file inputs/androzoo/input_sha256.txt --download -npd 2 --extraction -npe 2 --labelling --vt_keys ./inputs/virustotal_api_keys.txt --building
```
It is possible to execute each module individually, according to usage examples.
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt
python3 adbuilder.py --extraction
python3 adbuilder.py --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py --building
```
It is also possible to execute the download and extraction modules with more than one process, for example:
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 (download with three processes)
python3 adbuilder.py --extraction -npe 3 (extraction with three processes)
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 --extraction -npe 2 (download with three processes and extraction with two processes)
```
Finally, it is possible to execute modules together, as shown in the examples:
```
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt -npd 3 --extraction -npe 3 --building
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt --extraction
python3 adbuilder.py --extraction --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py --download --file inputs/androzoo/input_sha256.txt --extraction --labelling --vt_keys ./inputs/virustotal_api_keys.txt
python3 adbuilder.py  --extraction --labelling --file inputs/androzoo/input_sha256.txt --vt_keys ./inputs/virustotal_api_keys.txt --building
```

***NOTE 1: It is important that each user uses their own API key, obtained from the [AndroZoo website](androzoo.uni.lu), to download the APKs. Insert your API key in the file: /inputs/androzoo/apikey_androzoo.txt.***

***NOTE 2: An API key will be provided to use the VirusTotal service. However, it is important that each user uses their own key due to the daily limitations.***

***NOTE 3: The final dataset is generated in the output of the generation module, in the folder: queues/building/Final.***