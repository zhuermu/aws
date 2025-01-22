#!/usr/bin/env python
from constructs import Construct
from cdk8s import App, Chart
from imports import k8s
import os

class MyChart(Chart):
    def __init__(self, scope: Construct, id: str):
        
        # define resources here
        super().__init__(scope, f"{id}-deployment")
        label = {"app": "ten-agent-demo"}
        # Creates the deployment to spin up pods with your container
        # set environment variables here
        # 
        k8s.KubeDeployment(self, 'ten-agent-demo',
            spec=k8s.DeploymentSpec(
                replicas=2,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                metadata=k8s.ObjectMeta(labels=label, namespace='ten-framework'),
                spec=k8s.PodSpec(containers=[
                    k8s.Container(
                    env=[
                        k8s.EnvVar(name='AGENT_SERVER_URL', value=os.environ['AGENT_SERVER_URL']),
                    ],
                    name=os.environ['AGENT_NAME_DEMO'],
                    image=os.environ['AGENT_DEMO_IMAGE'],
                    ports=[k8s.ContainerPort(container_port=3000)])]))))
        # read config.env as key:value pairs
        pairs = {}
        with open('config.env') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                # split by first '='
                key, value = line.split('=', 1)
                pairs[key.strip()] = value.strip()

        k8s.KubeDeployment(self, 'ten-agent-build',
            spec=k8s.DeploymentSpec(
                replicas=1,
                selector=k8s.LabelSelector(match_labels=label),
                template=k8s.PodTemplateSpec(
                metadata=k8s.ObjectMeta(labels=label, namespace='ten-framework'),
                spec=k8s.PodSpec(containers=[
                    k8s.Container(
                    env=[
                        k8s.EnvVar(name=key, value=pairs[key])
                        for key in pairs.keys()
                    ],
                    name=os.environ['AGENT_NAME_SERVER'],
                    image=os.environ['AGENT_SERVER_IMAGE'],
                    ports=[k8s.ContainerPort(container_port=8080)])]))))
        

        # Creates the service to expose the pods to traffic from the loadbalancer
        super().__init__(scope, f"{id}-service")
        k8s.KubeService(self, 'service',
            spec=k8s.ServiceSpec(
                type='LoadBalancer',
                ports=[k8s.ServicePort(port=3000, target_port=k8s.IntOrString.from_number(3000))],
                selector=label
            )
        )

app = App()

MyChart(app, "cdk8s")

app.synth()
