## -- Importing External Modules -- ##
from waitress import serve

## -- Importing Internal Modules -- ##
from app.routing import app
import app.config as cnfg

def main():
    """
    Main program function
    """

    # Server utilizado para produção 
    if cnfg.SERVER == "production":

        dict_connection = {
            "app": app,
            "host": "0.0.0.0",
            "port": cnfg.PORT,
            "threads": cnfg.THREADS,
            "connection_limit": cnfg.CONNECTION_LIMIT,
            "cleanup_interval": cnfg.CLEANUP_INTERVAL,
            "channel_timeout": cnfg.CHANNEL_TIMEOUT,
        }

        serve(**dict_connection)
    
    else:
        app.run(host = "0.0.0.0", port = cnfg.PORT,)    

if __name__ == "__main__":
    main()