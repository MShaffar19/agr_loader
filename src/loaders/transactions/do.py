from .transaction import Transaction

class DOTransaction(Transaction):

    def __init__(self, graph):
        Transaction.__init__(self, graph)
        self.batch_size = 2000

    def do_tx(self, data):
        '''
        Loads the DO data into Neo4j.
        '''

        query = """
            UNWIND $data as row

            //Create the DOTerm node and set properties. primaryKey is required.
            MERGE (doterm:DOTerm:Ontology {primaryKey:row.id})
            SET doterm.name = row.name
            SET doterm.nameKey = row.name_key
            SET doterm.definition = row.definition
            SET doterm.is_obsolete = row.is_obsolete
            SET doterm.subset = row.subset
            SET doterm.rgdLink = row.rgd_link
            SET doterm.mgiLink = row.mgi_link
            SET doterm.zfinLink = row.zfin_link
            SET doterm.humanLink = row.human_link
            SET doterm.flybaseLink = row.flybase_link
            SET doterm.wormbaseLink = row.wormbase_link
            SET d.doDisplayId = row.id
            SET d.doUrl = row.doUrl
            SET d.doPrefix = row.doPrefix
            SET d.doId = row.id


            FOREACH (entry in row.xrefs |
                MERGE (cr:ExternalId:Identifier {primaryKey:entry})
                MERGE (doterm)-[aka:ALSO_KNOWN_AS]->(cr))

            FOREACH (entry in row.do_synonyms |
                MERGE (syn:Synonym:Identifier {primaryKey:entry})
                MERGE (doterm)-[aka:ALSO_KNOWN_AS]->(syn))

            FOREACH (isa in row.isas |
                MERGE (doterm2:DOTerm:Ontology {primaryKey:isa})
                MERGE (doterm)-[aka:IS_A]->(doterm2))

        """
        Transaction.execute_transaction_batch(self, query, data, self.batch_size)