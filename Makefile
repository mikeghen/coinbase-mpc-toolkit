# Variables
REGISTRY_NAME=malice
TAG=latest
APPS=app src cdp
HELM_RELEASE_NAME=malice-release
HELM_CHART_PATH=./helm # Update this to the path of your Helm chart

# Default target
.PHONY: all
all: build push

# Build the Docker image
.PHONY: build
build:
	@for app in $(APPS); do \
		docker build -t $$app -f $$app/Dockerfile $$app; \
	done

# Tag the image with the registry URL
.PHONY: tag
tag:
	@for app in $(APPS); do \
		docker tag $$app registry.digitalocean.com/$(REGISTRY_NAME)/$$app:$(TAG); \
	done

# Push the image to the registry
.PHONY: push
push: tag
	@for app in $(APPS); do \
		docker push registry.digitalocean.com/$(REGISTRY_NAME)/$$app:$(TAG); \
	done

# Clean up local images
.PHONY: clean
clean:
	@for app in $(APPS); do \
		docker rmi $$app registry.digitalocean.com/$(REGISTRY_NAME)/$$app:$(TAG) || true; \
	done

# Deploy with Helm
.PHONY: deploy
deploy:
	@helm upgrade --install $(HELM_RELEASE_NAME) $(HELM_CHART_PATH) \
		--set image.repository=registry.digitalocean.com/$(REGISTRY_NAME)/app \
		--set image.tag=$(TAG) \
		--set image.repository=registry.digitalocean.com/$(REGISTRY_NAME)/flask-app \
		--set image.tag=$(TAG) \
		--set image.repository=registry.digitalocean.com/$(REGISTRY_NAME)/cdp \
		--set image.tag=$(TAG)
