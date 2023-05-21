from aws_cdk import (
    aws_cognito as cognito,
    RemovalPolicy
)
from constructs import Construct

class UserPool(Construct):

    @property
    def user_pool_id(self):
        return self.user_pool.user_pool_id

    @property
    def client_id(self):
        return self.client.user_pool_client_id

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # Create the user pool
        self.user_pool = cognito.UserPool(self, id,
                        user_pool_name=id,
                        self_sign_up_enabled=True,
                        user_verification=cognito.UserVerificationConfig(
                            email_subject="Account Verification",
                            email_body="Hey there, here's your verification code {####}",
                            email_style=cognito.VerificationEmailStyle.CODE,
                            sms_message="Your signup code is {####}"
                        ),
                        user_invitation=cognito.UserInvitationConfig(
                            email_subject="Dolfin Invitation",
                            email_body="Hello {username}, you've been invited to join! Your temporary password is {####}",
                            sms_message="Hello {username}, you've been invited to join! Your temporary password is {####}",
                        ),
                        sign_in_aliases=cognito.SignInAliases(
                            email=True
                        ),
                        sign_in_case_sensitive=True,
                        auto_verify=cognito.AutoVerifiedAttrs(email=True),
                        account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
                        removal_policy=RemovalPolicy.DESTROY,
                        password_policy=cognito.PasswordPolicy(
                            min_length=8,
                        ),
                        standard_attributes=cognito.StandardAttributes(
                            fullname=cognito.StandardAttribute(
                                required=True,
                                mutable=True
                            ),
                            email=cognito.StandardAttribute(
                                required=True,
                                mutable=True
                            )
                        )
        )


        # Attributes that the client can write
        client_write_attributes = (cognito.ClientAttributes()).with_standard_attributes(fullname=True, email=True)

        # Attributes that the client can read
        client_read_attributes = (cognito.ClientAttributes()).with_standard_attributes(fullname=True, email=True, email_verified=True)

        # Provision the User Pool Client
        self.client = self.user_pool.add_client(id+'-client',
                            auth_flows=cognito.AuthFlow(
                                admin_user_password=True,
                                user_password=True
                            ),
                            prevent_user_existence_errors=True,
                            read_attributes=client_read_attributes,
                            write_attributes=client_write_attributes
            )

        # Logging out some values
        # pool_id = self.user_pool.user_pool_id
        # client_id = self.client.user_pool_client_id

        # CfnOutput(self, "UserPoolId", value=pool_id)
        # CfnOutput(self, "ClientId", value=client_id)