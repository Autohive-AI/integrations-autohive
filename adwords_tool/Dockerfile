FROM public.ecr.aws/lambda/python:3.12

# Copy function code
# Assuming adwords_module.py is the main file, and config.json might also be needed at runtime by the SDK.
COPY adwords_module.py ${LAMBDA_TASK_ROOT}/
COPY config.json ${LAMBDA_TASK_ROOT}/
COPY google-ads.yaml ${LAMBDA_TASK_ROOT}/ # Ensure google-ads.yaml is present for the client

# Install the function's dependencies
COPY requirements.txt .
# credentials.json was in the old Dockerfile, but google-ads.yaml is used by the google-ads client.
# If credentials.json is still needed by the SDK or another part, it should be added here.
RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

# Set the CMD to your handler. 
# This will depend on how the autohive_integrations_sdk expects to be run.
# It might be a generic entrypoint provided by the SDK's base image, or a specific command.
# For now, let's assume the SDK handles this and we might not need a CMD, 
# or it will be different from the old lambda_handler.
# CMD [ "adwords_module.main" ] # Placeholder, this needs to be confirmed based on SDK usage. 