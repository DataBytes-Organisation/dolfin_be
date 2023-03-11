from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigw,
    aws_lambda as _lambda,
    aws_s3 as s3,
)

class Api(Construct):
    def __init__(self, scope: Construct, construct_id: str, bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        #* default lambda
        default_lambda = _lambda.Function(
            self, 'default',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambdas/api_endpoints/src'),
            handler='default.handler'
        )

        #API gw instance
        api = apigw.LambdaRestApi(
            self, construct_id,
            handler=default_lambda,
            proxy=False
        )
        
        # Lambdas
        get_example_lambda = _lambda.Function(
            self, 'get_example',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('lambdas/api_endpoints/src'),
            handler='get_example.handler',
        )

        #BUCKET PERMISSIONS
        bucket.grant_read_write(get_example_lambda)

        # API routes
        # /prediction
        example_route = api.root.add_resource('example')
        example_route.add_method('GET', apigw.LambdaIntegration(get_example_lambda))