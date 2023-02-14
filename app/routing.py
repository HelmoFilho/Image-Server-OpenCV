## -- Importing External Modules -- ##
from flask import make_response, json, g, wrappers
from timeit import default_timer as timer

## -- Importing Internal Modules -- ##
from app.server import app

# Cors handler
def add_cors_return(resp) -> json:

    response = make_response(resp)
    
    if not response.headers.get("Content-Type"):
        response.headers['Content-Type'] = 'application/json'
    
    response.headers.add("Access-Control-Allow-Headers", "*")
    response.headers.add("Access-Control-Allow-Methods", "*")
    response.headers.add("Access-Control-Expose-Headers", "Content-Disposition")
    response.headers.add("Access-Control-Allow-Credentials", True)
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


# 404 response
@app.errorhandler(404)
def not_found(e):
    return {"response": "not found"}, 404


# Before request
@app.before_request
def before_request(resp):
    
    g.start = timer()


# After request
@app.after_request
def after_request(resp):

    g.finish = timer()
    
    if int(resp.status_code) == 404:
        return {"response": "not found"}, 404
    
    resp = add_cors_return(resp)
    resp.headers.add("X-Process-Time", "{:.5f}".format(g.finish - g.start))
    return resp


#### routing
@app.route("/<path:direcao>", methods = ['GET'])
def servir_arquivo(**kwargs) -> wrappers.Response:
    """
    Retorna o arquivo requerido pelo front-end

    kwargs:
        tipo (str): Tipo de arquivo.
        direcao (str): direcao para a imagem.

    Returns:
        wrappers.Response: Resultado da transação
    """

    # Pegando os dados da URL
    tipo = str(kwargs.get("tipo")).lower()

    # Criando a rota principal do tipo de arquivo
    root_folder = str(os.environ.get("ROOT_FOLDER_SI"))
    main_route = f"{root_folder}\\{tipo}"
    
    # Checa se rota principal existe
    if not os.path.exists(main_route):
        abort(404)

    # Verifica se o tipo é de um dos tipo que esse servidor pode tratar
    if tipo == "imagens":
        data = {key: value   for key, value in kwargs.items()   if key != "tipo"}
        response = si.servir_imagens_get(**data)
    
    else:
        abort(404)
    
    return response
