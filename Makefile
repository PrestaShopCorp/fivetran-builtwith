.PHONY: run test

run:
	@functions-framework --target function --debug

test:
	@curl -X POST localhost:8080 \
		  -H 'Content-Type: application/json' \
		  -d '{"agent":"test" ,"state":{}, "secrets":{"api_id": "4b672892d8488213a38ff4c16feffbe7", "api_key": "ab9db70384485bed0c01b5e7b901e136"}}'

test-setup:
	@curl -X POST localhost:8080 \
		  -H 'Content-Type: application/json' \
		  -d '{"agent":"test" ,"state":{}, "setup_test": true, "secrets":{"api_key": "011ca6b0-9222-420c-9a72-7329ee3344f6"}}'


deploy:
	@gcloud functions deploy builtwith --project ps-data-fivetran --region europe-west1 --runtime python39 --trigger-http

describe:
	@gcloud functions describe builtwith
