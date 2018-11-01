import logging, coloredlogs
from loaders import *
from etl import *
from transactions import *
from neo4j_transactor import Neo4jTransactor
from data_file_manager import DataFileManager

coloredlogs.install(level=logging.INFO,
    fmt='%(asctime)s %(levelname)s: %(name)s:%(lineno)d: %(message)s',
    field_styles={
        'asctime': {'color': 'green'}, 
        'hostname': {'color': 'magenta'}, 
        'levelname': {'color': 'white', 'bold': True}, 
        'name': {'color': 'blue'}, 
        'programname': {'color': 'cyan'}
    })

# This has to be done because the OntoBio module does not use DEBUG it uses INFO which spews output.
# So we have to set the default to WARN in order to "turn off" OntoBio and then "turn on" by setting 
# to DEBUG the modules we want to see output for.
logger = logging.getLogger(__name__)

class AggregateLoader(object):

    def run_loader(self):

        data_manager = DataFileManager("config/default.yml")
        data_manager.download_and_validate()

        thread_pool = []
        for n in range(0, 4):
            runner = Neo4jTransactor()
            runner.threadid = n
            runner.daemon = True
            runner.start()
            thread_pool.append(runner)
        
        # The following order is REQUIRED for proper loading.
        logger.info("Creating indices.")
        Indicies().create_indices()

        so_etl = SOETL(data_manager)
        so_etl.run_etl()

        #OntologyLoader().run_loader()
        #logger.info("OntologyLoader: Waiting for Queue to clear")
        #Transaction.wait_for_queues()

        #modloader = ModLoader()
        #modloader.run_bgi_loader()
        #logger.info("ModLoader.run_bgi_loader: Waiting for Queue to clear")
        #Transaction.wait_for_queues()

        #modloader.run_other_loaders()
        #modloader.run_other_loaders(None, None)
        #logger.info("ModLoader.run_other_loaders: Waiting for Queue to clear")
        #Transaction.wait_for_queues()

        #OtherDataLoader().run_loader()
        #logger.info("OtherDataLoader: Waiting for Queue to clear")
        #Transaction.wait_for_queues()

if __name__ == '__main__':
    AggregateLoader().run_loader()
