# rhoai-model-pipeline

Important, before to start:
This pipeline assumes that Red Hat OpenShift AI is already installed as well the Minio that will
serve as the storage for the models.


This pipeline will execute the following steps in the same order as described:

- Clean the given namespace by deleting all the resources that might be created by a previous execution and left behind.
- 


## Running it:

Fill the required fields on the pipeline-run.yaml file and then run the following command:

```bash
oc create -f pipeline-run.yaml
```

It will trigger the Pipeline.


### TODOs

- [ ] Create a base python image with the required dependencies as part of the pipeline
- [ ] Parameterize the deploy-isvc step timeout, default is 120s.
- [ ] Create the given namespace if it does not exist