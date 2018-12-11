import logging, coloredlogs, os, multiprocessing, time
from etl import *
from transactors import Neo4jTransactor, FileTransactor
from transactions import Indicies
from data_manager import DataFileManager


debug_level = logging.INFO

coloredlogs.install(level=debug_level,
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

# logging.basicConfig(stream=sys.stdout, level=logging.INFO,
# format='%(asctime)s %(levelname)s: %(name)s:%(lineno)d: %(message)s')

logger = logging.getLogger(__name__)


class AggregateLoader(object):

    def run_loader(self):

        # TODO Allow the yaml file location to be overwritten by command line input (for Travis).
        data_manager = DataFileManager(os.path.abspath('src/config/develop.yml'))
        data_manager.process_config()

        ft = FileTransactor()

        ft.start_threads(10)
        data_manager.download_and_validate()
        ft.wait_for_queues()
        ft.shutdown()
        
        nt = Neo4jTransactor()
        nt.start_threads(7)
        
        if "USING_PICKLE" in os.environ and os.environ['USING_PICKLE'] == "True":
            pass
        else:
            logger.info("Creating indices.")
            Indicies().create_indices()

        etl_dispatch = {
            'GO': GOETL,
            'DO': DOETL,
            'SO': SOETL,
            'MI': MIETL,
            'BGI': BGIETL,
            'Allele': AlleleETL,
            'Expression': ExpressionETL,
            'ExpressionRibbon': ExpressionRibbonETL,
            'Disease': DiseaseETL,
            'Phenotype': PhenoTypeETL,
            'Orthology': OrthologyETL,
            'Ontology': GenericOntologyETL,
            'Closure': ClosureETL,
            'GOAnnot': GOAnnotETL,
            'GeoXref': GeoXrefETL,
            'GeneDiseaseOrtho': GeneDiseaseOrthoETL,
            #'ResourceDescriptor': ResourceDescriptorETL,
            #'MolecularInteraction': MolecularInteractionETL,
        }

        # This is the order in which data types are loaded.
        # After each list, the loader will "pause" and wait for that item to finish.
        # i.e. After Ontology, there will be a pause.
        # After GO, DO, SO, MI, there will be a pause, etc.
        list_of_etl_groups = [
            ['Ontology'],
            ['GO', 'DO', 'SO', 'MI'],
            ['Closure'],
            ['BGI'],
            ['Allele'],
            ['Expression'],
            ['ExpressionRibbon'],
            ['Disease'],  # Locks Genes
            ['Phenotype'],  # Locks Genes
            ['Orthology'],  # Locks Genes
            ['GOAnnot'],  # Locks Genes
            ['GeoXref'],  # Locks Genes
            ['GeneDiseaseOrtho'],
        ]

        start_time = time.time()

        for etl_group in list_of_etl_groups:
            etl_group_start_time = time.time()
            logger.info("Starting ETL group: %s" % etl_group)
            thread_pool = []
            for etl_name in etl_group:
                logger.debug("ETL Name: %s" % etl_name)
                config = data_manager.get_config(etl_name)
                logger.debug("Config: %s" % config)
                if config is not None:
                    etl = etl_dispatch[etl_name](config)
                    p = multiprocessing.Process(target=etl.run_etl)
                    p.start()
                    thread_pool.append(p)
                else:
                    logger.info("No Config found for: %s" % etl_name)
            for thread in thread_pool:
                thread.join()
                
            logger.info("Waiting for Queues to sync up")
            Neo4jTransactor().wait_for_queues()
            etl_elapsed_time = time.time() - etl_group_start_time
            logger.info("Finished ETL group: %s, Elapsed time: %s" % (etl_group, time.strftime("%H:%M:%S", time.gmtime(etl_elapsed_time))))
        
        nt.shutdown()

        end_time = time.time()
        elapsed_time = end_time - start_time

        logger.info('Loader finished. Elapsed time: %s' % time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))


if __name__ == '__main__':
    AggregateLoader().run_loader()
