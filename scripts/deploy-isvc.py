import argparse
import json

from kserve import KServeClient
from kserve import V1beta1InferenceService
from kserve import V1beta1InferenceServiceSpec
from kserve import V1beta1ModelFormat
from kserve import V1beta1ModelSpec
from kserve import V1beta1PredictorSpec
from kserve import constants
from kubernetes import client


def deploy_isvc(protocol, namespace, verbose):

    runtime = "caikit-tgis-runtime"
    name = "caikit-tgis-isvc"

    if protocol == "grpc":
        runtime = runtime + "-grpc"
        name = name + "-grpc"
    else:
        name = name + "-http"

    default_model_spec = V1beta1InferenceServiceSpec(
        predictor=V1beta1PredictorSpec(
            service_account_name="sa",
            model=V1beta1ModelSpec(
                model_format=V1beta1ModelFormat(name="caikit"),
                runtime=runtime,
                # requires the storage-config secret to be created with the s3 credentials
                storage_uri='s3://modelmesh-example-models/llm/models/flan-t5-small-caikit')))

    isvc = V1beta1InferenceService(api_version=constants.KSERVE_V1BETA1,
                                   kind=constants.KSERVE_KIND,
                                   metadata=client.V1ObjectMeta(
                                       labels={"pipeline": "caikit-pipeline-test"},
                                       name=name,
                                       namespace=namespace,
                                       annotations={
                                           "serving.knative.openshift.io/enablePassthrough": "true",
                                           "sidecar.istio.io/inject": "true",
                                           "sidecar.istio.io/rewriteAppHTTPProbers": "true"
                                       },
                                   ),
                                   spec=default_model_spec)

    if verbose:
        print(json.dumps(isvc.to_dict(), indent=2))
    kserve = KServeClient()
    kserve.create(isvc, namespace=namespace, watch=True, timeout_seconds=120)

    response_json = kserve.get(name=name, timeout_seconds=240, namespace=namespace, watch=False)
    endpoint = response_json.get('status', {}).get('components', {}).get('predictor', {}).get('url', None)

    if endpoint is not None:
        with open("output-envs.properties", 'a') as f:
            f.write(f"endpoint-{protocol}={endpoint}\n")
        return endpoint
    else:
        raise ValueError("Failed to deploy the isvc - not able to find the endpoint, check the response: " + response_json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='CaKit Inference caller')
    parser.add_argument('-n', '--namespace', type=str, help='Models isvc target namespace')
    parser.add_argument('-v', '--verbose', default=False, action='store_true', help='List swf builder images')
    parser.add_argument('-p', '--protocol', default='http', type=str,
                        help='Deploy the isvc with the specified protocol (http or grpc)')

    args = parser.parse_args()
    if args.namespace is None:
        raise ValueError("Namespace is required")

    deploy_isvc(args.protocol, args.namespace, args.verbose)


