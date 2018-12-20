import logging

from .resource_descriptor import ResourceDescriptorService
from .resource_descriptor_transaction import ResourceDescriptorTransaction

logger = logging.getLogger(__name__)

class OtherDataLoader(object):
    def __init__(self):
        self.batch_size = 4000

    def run_loader(self):
        self.load_mol()
        self.load_additional_datasets()
        self.add_inferred_disease_annotations()
        #self.load_resource_descriptors()

    def load_resource_descriptors(self):
        logger.info("Extracting and loading resource descriptors")
        ResourceDescriptorTransaction().resource_descriptor_tx(ResourceDescriptorService().get_data())