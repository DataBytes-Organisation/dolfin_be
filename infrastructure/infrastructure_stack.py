from aws_cdk import (
    Stack,
    RemovalPolicy,
    aws_s3 as s3,
    aws_dynamodb as ddb
)
from constructs import Construct
from infrastructure.components.api import Api
from infrastructure.components.userpool import UserPool

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.name = "Dolfin"

        user_table = ddb.Table(
            self, f"{self.name}UserTable",
            partition_key={ 'name': 'record_type', 'type': ddb.AttributeType.STRING},
            sort_key={'name': 'record_ts_id', 'type': ddb.AttributeType.STRING}
        )
        user_pool = UserPool(self, f'{self.name}UserPool')
        access_table = ddb.Table(
            self, id=f"{self.name}AccessTable",
            partition_key={'name': "key_id", 'type': ddb.AttributeType.STRING},
            removal_policy=RemovalPolicy.DESTROY
        )
        access_table.add_global_secondary_index(
            index_name='key_value_index',
            partition_key={'name': 'key_value', 'type': ddb.AttributeType.STRING},
        )
        app_table = ddb.Table(
            self, f"{self.name}AppTable",
            partition_key={'name': 'PK', 'type': ddb.AttributeType.STRING},
            sort_key={'name': 'SK', 'type': ddb.AttributeType.STRING}
        )

        data_bucket = s3.Bucket(self, f"{self.name}-bucket")

        ''' REST API '''
        api = Api(self, f"{self.name}-api", 
            stack_name=self.name,
            user_table=user_table,
            access_table=access_table,
            user_pool_id=user_pool.user_pool_id,
            client_id=user_pool.client_id,
            bucket=data_bucket,
            app_table=app_table,
        )       


        
