run:
	scripts/run.sh

server:
	uvicorn server:app --reload

setup:
	sh scripts/setup.sh

type-check:
	mypy .

update-prisma:
	prisma generate --generator=python && prisma db push

docker-build-local:
	docker build --tag server_image_local .

docker-build-linux:
	docker build --platform linux/amd64 --tag server_image_linux .

docker-run-local:
	docker run --publish 80:80 -e OPENAI_API_KEY=$$OPENAI_API_KEY server_image_local