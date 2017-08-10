from neo4j.v1 import GraphDatabase
from .transaction import Transaction

class BGITransaction(Transaction):

    def __init__(self, graph):
        Transaction.__init__(self, graph)

    def bgi_tx(self, data):
        '''
        Loads the BGI data into Neo4j.
        Is name_key necessary with symbol?

        '''

        query = """
            UNWIND $data as row

            //Create the Gene node and set properties. primaryKey is required.
            CREATE (g:Gene {primaryKey:row.primaryId, dateProduced:row.dateProduced, dataProvider:row.dataProvider})
            SET g.symbol = row.symbol
            SET g.taxonId = row.taxonId
            SET g.name = row.name
            SET g.description = row.description
            SET g.geneSynopsisUrl = row.geneSynopsisUrl
            SET g.geneLiteratureUrl = row.geneLiteratureUrl

            //Create nodes for other identifiers.

            FOREACH (entry in row.secondaryIds |           
                MERGE (second:SecondaryId:Identifier {name:entry, primaryKey:entry})
                MERGE (g)-[aka1:ALSO_KNOWN_AS]->(second))

            FOREACH (entry in row.synonyms |           
                CREATE (syn:Synonym:Identifier {name:entry, primaryKey:entry})
                MERGE (g)-[aka2:ALSO_KNOWN_AS]->(syn))

            FOREACH (entry in row.external_ids |           
                MERGE (ext:externalId:Identifier {name:entry, primaryKey:entry})
                MERGE (g)-[aka3:ALSO_KNOWN_AS]->(ext))

            MERGE (spec:Species {primaryId: row.taxonId})
            SET spec.species = row.species
            SET spec.name = row.species
            MERGE (g)-[:FROM_SPECIES]->(spec)

            //MERGE the SOTerm node and set the primary key.
            MERGE (s:SOTerm:Ontology {primaryKey:row.soTermId})

            //Create the relationship from the gene node to the SOTerm node.
            MERGE (g)-[x:ANNOTATED_TO]->(s)

            //Merge the entity node.
            MERGE (ent:Entity {primaryKey:row.dataProvider})
            SET ent.dateProduced = row.dateProduced
            SET ent.release = row.release

            //Create the entity relationship to the gene node.
            MERGE (g)-[c1:CREATED_BY]->(ent)


            WITH row.crossReferences as events
            UNWIND events as event
                MERGE (id:CrossReference:Entity {primaryKey:event.id, name:event.id})
                SET id.globalCrosssrefId = event.crossRef
                SET id.localId = event.localId
                SET id.crossrefCompleteUrl = event.crossrefCompleteUrl

        """
        Transaction.execute_transaction(self, query, data)

        # The properties below need to be assigned / resolved:
        # "href": None,

        # genomeLocations break the loader:
        # neo4j.exceptions.CypherTypeError: Property values can only be of primitive types or arrays thereof
        # SET g.genomeLocations = row.genomeLocations
        # SET g.crossReferences = row.crossReferences 
        # SET g.modCrossReference = row.modCrossReference