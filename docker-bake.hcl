# Build the dev container and its base with `docker buildx bake` (see the Dockerfile).
#
# The `Dev container` workflow checks MRIQC out into ./mriqc at the commit pinned in
# pyproject.toml, then runs `docker buildx bake base dev --push`. When the base already exists
# in the registry, it builds `dev` alone on top of it:
#   docker buildx bake dev --set dev.contexts.base=docker-image://<registry>:base-<commit>

variable "MRIQC_SHA" {
  default = "f61290947f6aa79e143e38e314bfd63c09d7384f"
}

variable "REGISTRY" {
  default = "ghcr.io/nipreps/mriqc-flyte"
}

# Build date (YYYYMMDD), added as a second tag of the dev image when set.
variable "DATE" {
  default = ""
}

variable "SOURCE" {
  default = "https://github.com/nipreps/mriqc-flyte"
}

group "default" {
  targets = ["dev"]
}

# MRIQC's own Dockerfile, unchanged, at the pinned commit.
target "base" {
  context   = "mriqc"
  platforms = ["linux/amd64"]
  args      = { VCS_REF = MRIQC_SHA }
  labels    = { "org.opencontainers.image.source" = SOURCE }
  tags      = ["${REGISTRY}:base-${substr(MRIQC_SHA, 0, 8)}"]
}

target "dev" {
  context   = "."
  contexts  = { base = "target:base" }
  args      = { BASE_IMAGE = "base" }
  platforms = ["linux/amd64"]
  labels    = { "org.opencontainers.image.source" = SOURCE }
  tags      = compact(["${REGISTRY}:dev", notequal(DATE, "") ? "${REGISTRY}:dev-${DATE}" : ""])
}
