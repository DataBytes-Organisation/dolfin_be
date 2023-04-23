from typing import List
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
    aws_cognito as cognito,
)


def create_lambda(scope: Construct, name: str, python_file: str, environment: dict, layers: List[aws_lambda_alpha.PythonLayerVersion]): 
    return _lambda.Function(
    scope, f"{name}",
    runtime=_lambda.Runtime.PYTHON_3_8,
    code=_lambda.Code.from_asset('api_endpoints'),
    handler=f'{python_file}.handler',
    layers=layers,
    environment=environment,
    log_retention=logs.RetentionDays.ONE_WEEK
)

class Api(Construct):
    def __init__(self, 
                scope: Construct, 
                construct_id: str, 
                user_table: ddb.Table, 
                access_table: ddb.Table,
                user_pool_id: str, 
                user_pool: cognito.UserPool,
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

        common_lambda_environment = {
            "user_table": user_table.table_name,
            "userpool_id": user_pool_id,
            "client_id": client_id,
            "access_table": access_table.table_name,
        }

        #API gw instance
        api = apigw.LambdaRestApi(
            self, construct_id,
            handler=default_lambda,
            proxy=False
        )

        authorizer_lambda = create_lambda(
            scope=scope,
            name=f"{self.stack_name}AccessAuth", 
            python_file = "authorizer", 
            environment = common_lambda_environment, 
            layers = [common_layer]
        )

        authorizer = apigw.TokenAuthorizer(self, f"{self.stack_name}ApiAuthorizer",
            handler=authorizer_lambda
        )

        cognito_authorizer = apigw.CognitoUserPoolsAuthorizer(self, f"{self.stack_name}CognitoAuthorizer",
            cognito_user_pools=[user_pool],
        )

        # cognito_authorizer = apigw.CfnAuthorizer(self, "adminSectionAuth", rest_api_id=api.rest_api_id,
        #     type='COGNITO_USER_POOLS', 
        #     identity_source='method.request.header.Authorization',
        #     provider_arns=[user_pool.user_pool_arn],
        #     name="adminSectionAuth"
        # )

        access_table.grant_read_write_data(authorizer_lambda)

        # adds account with admin user
        post_account_lambda = create_lambda(
            scope=scope,
            name=f"{self.stack_name}PostAccount",
            python_file = "post_account", 
            environment = common_lambda_environment, 
            layers = [common_layer]
        )

        access_table.grant_read_write_data(post_account_lambda)
        user_table.grant_read_write_data(post_account_lambda)        
        post_account_lambda.add_to_role_policy(ses_policy)
        post_account_lambda.add_to_role_policy(cognito_policy)

        # adds user to existing account
        post_user_lambda = create_lambda(
            scope=scope,
            name=f"{self.stack_name}PostUser",
            python_file = "sign_up", 
            environment = common_lambda_environment, 
            layers = [common_layer]
        )

        access_table.grant_read_write_data(post_user_lambda)
        user_table.grant_read_write_data(post_user_lambda)        
        post_user_lambda.add_to_role_policy(ses_policy)
        post_user_lambda.add_to_role_policy(cognito_policy)

        sign_in_lambda = create_lambda(
            scope=scope,
            name=f"{self.stack_name}SignIn",
            python_file = "sign_in", 
            environment = common_lambda_environment, 
            layers = [common_layer]
        )

        access_table.grant_read_write_data(sign_in_lambda)
        user_table.grant_read_write_data(sign_in_lambda)        
        sign_in_lambda.add_to_role_policy(ses_policy)
        sign_in_lambda.add_to_role_policy(cognito_policy)

        basiq_get_balance_lambda = create_lambda(
            scope=scope,
            name=f"{self.stack_name}GetCurrentBalance",
            python_file = "get_current_balance", 
            environment = common_lambda_environment, 
            layers = [common_layer]
        )

        #access_table.grant_read_write_data(basiq_get_balance_lambda)
        user_table.grant_read_write_data(basiq_get_balance_lambda)        
        basiq_get_balance_lambda.add_to_role_policy(ses_policy)
        basiq_get_balance_lambda.add_to_role_policy(cognito_policy)

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

        basiq = api.root.add_resource('basiq')
        basiq_balance = basiq.add_resource('balance')
        basiq_balance.add_method('GET', 
            apigw.LambdaIntegration(basiq_get_balance_lambda), 
            authorizer=cognito_authorizer, 
            authorization_type=apigw.AuthorizationType.COGNITO,
        )