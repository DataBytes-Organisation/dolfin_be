from aws_cdk import (
    Stack,
    aws_s3 as s3,
)
from constructs import Construct
from infrastructure.components.api import Api

class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        data_bucket = s3.Bucket(self, "dolfinBucket")

        ''' REST API '''
        api = Api(self, 'dolfinApi', bucket=data_bucket)        


        
