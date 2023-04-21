from constructs import Construct
from aws_cdk import (
    aws_apigateway as apigw,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_lambda_python_alpha as aws_lambda_alpha,
    aws_s3 as s3,
    Duration,
    aws_logs as logs,
    aws_iam as iam,
    aws_dynamodb as ddb,
)

class Api(Construct):
    def __init__(self, 
                scope: Construct, 
                construct_id: str, 
                user_table: ddb.Table, 
                access_table: ddb.Table,
                user_pool_id: str, 
                client_id: str, 
                bucket: s3.Bucket, 
                app_table: ddb.Table,
                stack_name: str,
                **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.stack_name = stack_name

        common_layer = aws_lambda_alpha.PythonLayerVersion(
            self,
            'CommonLayer',
            entry='api_endpoints',
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
            removal_policy=RemovalPolicy.DESTROY,
        )

        #* Policies
        # Policy to send emails via ses
        ses_policy = iam.PolicyStatement(
            actions=["ses:SendEmail"],
            resources=['*']
        )

        cognito_policy = iam.PolicyStatement(
            actions=["cognito-idp:*"],
            resources=['*']
        )

        #* default lambda
        default_lambda = _lambda.Function(
            self, 'default',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='default.handler'
        )

        #API gw instance
        api = apigw.LambdaRestApi(
            self, construct_id,
            handler=default_lambda,
            proxy=False
        )

        authorizer_lambda = _lambda.Function(
            self, f"{self.stack_name}AccessAuth",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='authorizer.handler',
            timeout=Duration.seconds(30),
            layers=[common_layer],
            environment={
                "ACCESS_TABLE": access_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )

        authorizer = apigw.TokenAuthorizer(self, f"{self.stack_name}ApiAuthorizer",
            handler=authorizer_lambda
        )

        access_table.grant_read_write_data(authorizer_lambda)

        # adds account with admin user
        post_account_lambda = _lambda.Function(
            self, f"{self.stack_name}PostAccount",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='post_account.handler',
            layers=[common_layer],
            environment={
                "user_table": user_table.table_name,
                "userpool_id": user_pool_id,
                "client_id": client_id,
                "access_table": access_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        access_table.grant_read_write_data(post_account_lambda)
        user_table.grant_read_write_data(post_account_lambda)        
        post_account_lambda.add_to_role_policy(ses_policy)
        post_account_lambda.add_to_role_policy(cognito_policy)

        # adds user to existing account
        post_user_lambda = _lambda.Function(
            self, f"{self.stack_name}PostUser",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='sign_up.handler',
            layers=[common_layer],
            environment={
                "user_table": user_table.table_name,
                "userpool_id": user_pool_id,
                "client_id": client_id,
                "access_table": access_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        access_table.grant_read_write_data(post_user_lambda)
        user_table.grant_read_write_data(post_user_lambda)        
        post_user_lambda.add_to_role_policy(ses_policy)
        post_user_lambda.add_to_role_policy(cognito_policy)

        sign_in_lambda = _lambda.Function(
            self, f"{self.stack_name}SignIn",
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='sign_in.handler',
            layers=[common_layer],
            environment={
                "user_table": user_table.table_name,
                "userpool_id": user_pool_id,
                "client_id": client_id,
                "access_table": access_table.table_name,
            },
            log_retention=logs.RetentionDays.ONE_WEEK
        )
        access_table.grant_read_write_data(sign_in_lambda)
        user_table.grant_read_write_data(sign_in_lambda)        
        sign_in_lambda.add_to_role_policy(ses_policy)
        sign_in_lambda.add_to_role_policy(cognito_policy)

        # Lambdas
        get_example_lambda = _lambda.Function(
            self, 'get_example',
            runtime=_lambda.Runtime.PYTHON_3_8,
            code=_lambda.Code.from_asset('api_endpoints'),
            handler='get_example.handler',
        )

        #BUCKET PERMISSIONS
        bucket.grant_read_write(get_example_lambda)
        app_table.grant_read_write_data(get_example_lambda)
        
        # API routes
        #/auth
        auth = api.root.add_resource('auth')

        #/auth/account
        auth_account = auth.add_resource('account')
        #auth_account.add_method('GET', apigw.LambdaIntegration(get_example_lambda))
        auth_account.add_method('POST', apigw.LambdaIntegration(post_account_lambda))
        
        #/auth/account/user
        auth_account_user = auth_account.add_resource('user')
        #auth_account_user.add_method('GET', apigw.LambdaIntegration(get_example_lambda))
        auth_account_user.add_method('POST', apigw.LambdaIntegration(post_user_lambda))
        auth_account_user.add_method('GET', apigw.LambdaIntegration(sign_in_lambda))
        
        #/auth/apikey
        auth_apikey = auth.add_resource('apikey')
        # auth/token
        auth_token = auth.add_resource('token')
        # /
        example_route = api.root.add_resource('example')
        example_route.add_method('GET', apigw.LambdaIntegration(get_example_lambda), authorizer=authorizer)