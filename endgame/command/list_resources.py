"""
List exposable resources
"""
import logging
import click
from endgame import set_log_level
from endgame.shared.aws_login import get_boto3_client, get_current_account_id
from endgame.shared.validate import click_validate_supported_aws_service
from endgame.exposure_via_resource_policies import glacier_vault, sqs, lambda_layer, lambda_function, kms, cloudwatch_logs, efs, s3, \
    sns, iam, ecr, secrets_manager, ses, elasticsearch, acm_pca
from endgame.shared import utils, constants

logger = logging.getLogger(__name__)


@click.command(name="list-resources", short_help="List exposable resources.")
@click.option(
    "--service",
    "-s",
    type=str,
    required=True,
    help=f"The AWS service in question. Valid arguments: {', '.join(constants.SUPPORTED_AWS_SERVICES)}",
    callback=click_validate_supported_aws_service,
)
@click.option(
    "--profile",
    "--p",
    type=str,
    required=False,
    help="Specify the AWS IAM profile.",
    envvar="AWS_PROFILE"
)
@click.option(
    "--region",
    "-r",
    type=str,
    required=False,
    default="us-east-1",
    help="The AWS region",
    envvar="AWS_REGION"
)
@click.option(
    "-v",
    "--verbose",
    "verbosity",
    count=True,
)
def list_resources(service, profile, region, verbosity):
    """
    List AWS resources to expose.
    """

    set_log_level(verbosity)

    resources = []
    # User-supplied arguments like `cloudwatch` need to be translated to the IAM name like `logs`
    provided_service = service
    service = utils.get_service_translation(provided_service=service)

    # Get the boto3 clients
    client = get_boto3_client(profile=profile, service=service, region=region)
    sts_client = get_boto3_client(profile=profile, service="sts", region=region)
    current_account_id = get_current_account_id(sts_client=sts_client)

    if service == "s3":
        resources = s3.S3Buckets(client=client, current_account_id=current_account_id, region=region)
    elif service == "iam":
        resources = iam.IAMRoles(client=client, current_account_id=current_account_id, region=region)
    elif service == "efs":
        resources = efs.ElasticFileSystems(client=client, current_account_id=current_account_id, region=region)
    elif service == "secretsmanager":
        resources = secrets_manager.SecretsManagerSecrets(client=client, current_account_id=current_account_id, region=region)
    elif service == "ecr":
        resources = ecr.EcrRepositories(client=client, current_account_id=current_account_id, region=region)
    elif service == "sns":
        resources = sns.SnsTopics(client=client, current_account_id=current_account_id, region=region)
    elif service == "sqs":
        resources = sqs.SqsQueues(client=client, current_account_id=current_account_id, region=region)
    elif service == "logs":
        resources = cloudwatch_logs.CloudwatchResourcePolicies(client=client, current_account_id=current_account_id, region=region)
    elif service == "kms":
        resources = kms.KmsKeys(client=client, current_account_id=current_account_id, region=region)
    elif service == "glacier":
        resources = glacier_vault.GlacierVaults(client=client, current_account_id=current_account_id, region=region)
    elif service == "acm-pca":
        resources = acm_pca.AcmPrivateCertificateAuthorities(client=client, current_account_id=current_account_id, region=region)
    elif service == "ses":
        resources = ses.SesIdentityPolicies(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "elasticsearch":
        resources = elasticsearch.ElasticSearchDomains(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda":
        resources = lambda_function.LambdaFunctions(client=client, current_account_id=current_account_id, region=region)
    elif provided_service == "lambda-layer":
        resources = lambda_layer.LambdaLayers(client=client, current_account_id=current_account_id, region=region)

    # Print the results
    if len(resources.resources) == 0:
        logger.warning("There are no resources given the criteria provided.")
        # print(f"There are no resources given the criteria provided.")
    for resource_name in resources.resources:
        print(resource_name)