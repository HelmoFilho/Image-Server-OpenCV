#=== Importações de módulos externos ===#
from flask import wrappers, make_response
import numpy as np
import os, cv2, re

#=== Importações de módulos internos ===#
import functions.data_management as dm
from app.server import logger

@logger
def servir_imagens_get(**kwargs) -> wrappers.Response:
    """
    Método GET do Servir Imagens do B2B  

    Returns:
        [wrappers.Response]: imagem escolhida
    """
    # Checando os dados enviados
    necessary_keys = ["direcao"]

    # Verificando a tipagem dos valores e valores nulos
    if dm.check_validity(kwargs, comparison_columns = necessary_keys,
                         not_null = necessary_keys):
        
        return {}, 404

    # Pegando os dados enviados
    try:
        full_path = str(kwargs.get("direcao")).split("/")
    except:
        logger.error(f"Url invalida")
        return {}, 404

    main_folder = f"{os.environ.get('ROOT_FOLDER_SI')}\\imagens"
    used_folder = f"{os.environ.get('ROOT_CHECK_FOLDER_SI')}" # Usado apenas pelo marketplace

    if not os.path.exists(main_folder):
        logger.error(f"Pasta de {main_folder} nao existe")
        return {}, 404

    if len(full_path) < 1:
        logger.error(f"Sem caminho especificado")
        return {}, 404

    elif len(full_path) in {1,2}:
        pasta = str(full_path[0]).lower()
        dimensoes = 'auto'
        rest_path = full_path[1:]

    else:
        pasta = str(full_path[0]).lower()
        dimensoes = str(full_path[1]).lower()
        rest_path = full_path[2:]
    
    # Criando o caminho do arquivo
    file_path = None        

    try:
    
        # Se a imagem for de um produto...
        if pasta == "produto":

            try:
                if len(rest_path) not in {2,3}:
                    logger.error(f"Url invalida para produtos")
                    return {}, 404

                if len(rest_path) == 2:

                    sku = str(rest_path[0]).lower()
                    imagem = str(rest_path[1]).lower()

                else:

                    sku = str(rest_path[0]).lower()
                    imagem = str(rest_path[2]).lower()

                posicao, formato = imagem.split(".")

            except:
                logger.error(f"Url invalida para produtos")
                return {}, 404

            if posicao not in {"1","2","3"}:
                logger.error(f"Posicao {posicao} invalida")
                return {}, 404

            # Pegando e modificando a imagem
            file_path = f"{main_folder}\\produto\\{sku}\\{imagem}"

        else:

            if rest_path:
                check_image = rest_path[-1]

            else:
                check_image = pasta

            try:
                imagem = check_image
                _, formato = imagem.split(".")

                formato = str(formato).lower()

            except:
                logger.error(f"Arquivo de url invalido")
                return {}, 404

            if os.path.exists(f"{main_folder}\\{pasta}"):
                main_folder = f"{main_folder}\\{pasta}"
            
            else:
                main_folder = f"{main_folder}\\{used_folder}\\{pasta}"

            for path in rest_path:
                main_folder = f"{main_folder}\\{path}"

            file_path = main_folder

    except Exception as e:
        logger.exception(e)
        return {}, 404

    # Enviando a imagem
    if file_path is None:
        logger.error(f"BUG")
        return {}, 404

    if not os.path.exists(file_path):
        logger.error(f"Imagem especifica {file_path} nao existe")
        return {}, 404

    if formato not in {"png", "jpg", "jpeg", "webp"}:
        logger.error(f"Formato de imagem requerido {formato} invalido.")
        return {}, 404 

    # Verificando as dimensões da imagem
    dimensoes = [str(dimensao).lower()   for dimensao in dimensoes.split("x")]
    
    if len(dimensoes) not in {1,2}:
        logger.error(f"Dimensao em formato nao valido")
        return {}, 404

    for dimensao in dimensoes:

        if str(dimensao).isdecimal():
            if int(dimensao) > 0:
                continue

        if re.match('^[0-9]+q?$', str(dimensao)):
            continue
        
        if str(dimensao) == "auto":
            continue
        
        logger.error(f"Alguma das dimensoes - {dimensoes} nao sao numericas ou sao invalidas")
        return {}, 404

    try:           
        imagem = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)

    except:
        logger.error("Erro ocorreu ao abrir o arquivo")
        return {}, 404

    try:
        shape = imagem.shape
        len_shape = len(shape)

        orig_height = None
        orig_width = None
        channels = None

        if len_shape < 2:
            logger.error("Imagem com shape inválido.")
            return {}, 404

        elif len_shape == 2:
            orig_height, orig_width = shape
            channels = 2

        else:
            orig_height = shape[0]
            orig_width = shape[1]
            channels = shape[2]

        if channels:
            if channels not in {2,3,4}:
                logger.error(f"Imagens com valor de canais {channels} inválido.")
                return {}, 404
    
    except:
        logger.error("Erro ao pegar o shape da imagem.")
        return {}, 404

    # Configurando as dimensões finais
    bool_square = False
    horizontal_edge = 0
    vertical_edge = 0

    if len(dimensoes) == 1:

        # Caso unica dimensão seta auto
        if dimensoes[0] == "auto":

            width, height = orig_width, orig_height

        # Caso se queira um quadrado
        elif 'q' in dimensoes[0] and channels:

            dimensao = int(re.sub('[^0-9]', '', str(dimensoes[0])))

            if orig_height != orig_width:

                bool_square = True

                if orig_width > orig_height:

                    width = dimensao
                    height = int(np.ceil((orig_height * width) / orig_width))

                    horizontal_edge = width
                    vertical_edge = int(np.ceil((width - height) / 2))

                elif orig_height > orig_width:

                    height = dimensao
                    width = int(np.ceil((orig_width * height) / orig_height))

                    vertical_edge = height
                    horizontal_edge = int(np.ceil((height - width) / 2))

            else:
                width = dimensao
                height = width

        # Caso unica dimensao seja valor especifico (valor para largura automatica)
        else:        
            width = int(dimensoes[0])
            height = np.ceil((orig_height * width) / orig_width)

    else:

        # Caso ambas dimensões sejam "auto"
        if dimensoes[0] == "auto" and dimensoes[1] == "auto":

            width, height = orig_width, orig_height

        # Caso somente primeira altura seja "auto" (valor para largura automatica)
        elif dimensoes[0] == "auto":
        
            height = int(dimensoes[1])
            width = np.ceil((orig_width * height) / orig_height)

        # Caso somente segunda altura seja "auto" (valor para altura automatica)
        elif dimensoes[1] == "auto":
        
            width = int(dimensoes[0])
            height = np.ceil((orig_height * width) / orig_width)

        # Caso ambos valores sejam especificos
        else:
            width = int(re.sub('[^0-9]', '', str(dimensoes[0])))
            height = int(re.sub('[^0-9]', '', str(dimensoes[1])))

    height = int(height)
    width = int(width)

    if (orig_height != height) and (orig_width != width):

        dim = (width, height)
        imagem = cv2.resize(imagem, dim, interpolation = cv2.INTER_AREA)

    if bool_square:

        new_shape = imagem.shape
        new_height, new_width = new_shape[0], new_shape[1]

        if new_height != new_width:

            if channels == 4:
                sum_img = np.zeros((vertical_edge, horizontal_edge, 4), dtype=np.uint8)

            elif channels == 3:
                sum_img = np.ones((vertical_edge, horizontal_edge, 3), dtype=np.uint8) * 255

            else:
                sum_img = np.ones((vertical_edge, horizontal_edge), dtype=np.uint8) * 255

            if new_height > new_width:
                imagem = cv2.hconcat([sum_img, imagem, sum_img])

            else:
                imagem = cv2.vconcat([sum_img, imagem, sum_img])

    # Servindo a imagem
    buffer = cv2.imencode(f'.{formato}', imagem)[1].tobytes()

    response = make_response(buffer)

    headers = {
        'Content-Type': f"image/{formato}",
        "mimetype": 'multipart/x-mixed-replace; boundary=frame'
    }

    response.headers.update(headers)

    return response