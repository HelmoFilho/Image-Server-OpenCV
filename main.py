## -- Importing External Modules -- ##
from waitress import serve

## -- Importing Internal Modules -- ##
from app.routing import app

def main():
    """
    Main program function
    """

    # Pega a variável do sistema criada no import do app
    choice = unidecode(os.environ.get("PSERVER_SI").lower())
    port = int(os.environ.get("MAIN_PORT_SI"))
    close_all_sessions()

    # Server utilizado para produção 
    if choice == "production":

        port = int(os.environ.get("MAIN_PORT_SI"))
        threads = int(os.environ.get("PROD_THREADS_SI"))
        connection_limit = int(os.environ.get("PROD_CON_LIMIT_SI"))
        cleanup_interval = float(os.environ.get("PROD_CLEANUP_INTERVAL_SI"))
        channel_timeout = float(os.environ.get("PROD_CHANNEL_TIMEOUT_SI"))

        dict_connection = {
            "app": app,
            "host": "0.0.0.0",
            "port": port,
            "threads": threads,
            "connection_limit": connection_limit,
            "cleanup_interval": cleanup_interval,
            "channel_timeout": channel_timeout
        }

        serve(**dict_connection)
    
    # Server utilizado para desenvolvimento 
    elif choice == "development":
        print(f"Starting server in DEVELOPMENT enviroment")
        app.run(host = "0.0.0.0", port = port)    
    
    # Server utilizado para teste (inútil)
    elif choice in ["testing", "debug"]:
        print(f"Starting server in TESTING enviroment")
        app.run()

    else:
        raise Exception("PSERVER com valor invalido")


if __name__ == "__main__":
    main()