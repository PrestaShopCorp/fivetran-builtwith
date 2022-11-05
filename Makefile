.PHONY: run test

run:
	@LOG_LEVEL=WARNING functions-framework --target builtwith --debug

test:
	@curl -X POST localhost:8080 \
		  -H 'Content-Type: application/json' \
		  -d '{"agent":"test" ,"state":{}, "secrets":{"api_key": "a099b87f-906d-446f-8ead-c3e56eb61105"}}'

test-setup:
	@curl -X POST localhost:8080 \
		  -H 'Content-Type: application/json' \
		  -d '{"agent":"test" ,"state":{}, "setup_test": true, "secrets":{"api_key": "a099b87f-906d-446f-8ead-c3e56eb61105"}}'


deploy:
	@gcloud functions deploy builtwith --project ps-data-fivetran --region europe-west1 --runtime python39 --trigger-http

describe:
	@gcloud functions describe builtwith
