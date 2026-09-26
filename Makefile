PACKWIZ ?= $(shell command -v packwiz || echo $(HOME)/.local/share/mise/installs/go/1.26.7/bin/packwiz)
VERSION := $(shell sed -n 's/^version = "\(.*\)"/\1/p' pack/pack.toml)
MRPACK  := dist/keel-and-cloud-$(VERSION).mrpack
IMAGE   ?= keel-and-cloud:dev

.PHONY: mrpack image smoke test serve clean

## mrpack: the file to share with players (imports into Prism, Modrinth App, ATLauncher)
mrpack: $(MRPACK)

$(MRPACK): $(shell find pack -type f)
	@mkdir -p dist
	cd pack && $(PACKWIZ) refresh && $(PACKWIZ) modrinth export -o ../$@
	@echo "Built $@"

## image: build the server image locally
image:
	docker build -f server/Dockerfile -t $(IMAGE) .

## smoke: build the image, then boot and check it the way CI does
smoke: image
	test/image-smoke.sh $(IMAGE)

## test: install the pack into build/server on a fresh world and check the boot log
test:
	test/server-test.sh --fresh-world

## serve: serve pack/ for the dev client instance (test/client-instance.sh)
serve:
	test/serve.sh

clean:
	rm -rf dist
