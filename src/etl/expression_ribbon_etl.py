"""Expression Ribbon ETL."""

import logging

from etl import ETL
from transactors import CSVTransactor, Neo4jTransactor
from .helpers import Neo4jHelper


class ExpressionRibbonETL(ETL):
    """Expression Ribbon ETL."""

    logger = logging.getLogger(__name__)

    # Query templates which take params and will be processed later

    insert_gocc_self_ribbon_terms_query_template = """
                USING PERIODIC COMMIT %s
                LOAD CSV WITH HEADERS FROM \'file:///%s\' AS row
                   MATCH (ebe:ExpressionBioEntity) WHERE ebe.primaryKey = row.ebe_id
                   MATCH (goTerm:GOTerm:Ontology) WHERE goTerm.primaryKey = row.go_id

                   MERGE (ebe)-[ebego:CELLULAR_COMPONENT_RIBBON_TERM]-(goTerm)"""

    insert_gocc_ribbon_terms_query_template = """
                USING PERIODIC COMMIT %s
                LOAD CSV WITH HEADERS FROM \'file:///%s\' AS row
                   MATCH (ebe:ExpressionBioEntity) WHERE ebe.primaryKey = row.ebe_id
                   MATCH (goTerm:GOTerm:Ontology) WHERE goTerm.primaryKey = row.go_id

                   MERGE (ebe)-[ebego:CELLULAR_COMPONENT_RIBBON_TERM]-(goTerm)"""

    # Querys which do not take params and can be used as is

    expression_gocc_ribbon_retrieve_query = """
                MATCH (ebe:ExpressionBioEntity)--(go:GOTerm:Ontology)-[:PART_OF|IS_A*]->(slimTerm:GOTerm:Ontology)
                WHERE slimTerm.subset =~ '.*goslim_agr.*'
                RETURN ebe.primaryKey, slimTerm.primaryKey"""

    gocc_self_ribbon_ebes_query = """
        MATCH (ebe:ExpressionBioEntity)-[:CELLULAR_COMPONENT]-(got:GOTerm:Ontology)
        WHERE got.subset =~ '.*goslim_agr.*'
        RETURN ebe.primaryKey, got.primaryKey; """

    def __init__(self, config):
        """Initialise object."""
        super().__init__()
        self.data_type_config = config

    def _load_and_process_data(self):

        self.logger.info("Starting Expression Ribbon Data")
        query_template_list = [
            [self.insert_gocc_ribbon_terms_query_template, "30000",
             "expression_gocc_ribbon_terms.csv"],
            [self.insert_gocc_self_ribbon_terms_query_template, "30000",
             "expression_gocc_self_ribbon_terms" + ".csv"]
        ]

        generators = self.get_ribbon_terms()

        query_and_file_list = self.process_query_params(query_template_list)
        CSVTransactor.save_file_static(generators, query_and_file_list)
        Neo4jTransactor.execute_query_batch(query_and_file_list)

        self.logger.info("Finished Expression Ribbon Data")

    def get_ribbon_terms(self):
        """Get ribbon terms."""
        self.logger.debug("made it to the gocc ribbon retrieve")

        return_set_rt = Neo4jHelper().run_single_query(self.expression_gocc_ribbon_retrieve_query)
        gocc_ribbon_data = []
        for record in return_set_rt:
            row = {"ebe_id": record["ebe.primaryKey"],
                   "go_id": record["slimTerm.primaryKey"]}
            gocc_ribbon_data.append(row)

        gocc_self_ribbon_data = []

        return_set_srt = Neo4jHelper().run_single_query(self.gocc_self_ribbon_ebes_query)
        for record in return_set_srt:
            row = {"ebe_id": record["ebe.primaryKey"],
                   "go_id": record["got.primaryKey"]}
            gocc_self_ribbon_data.append(row)

        yield [gocc_ribbon_data, gocc_self_ribbon_data]
