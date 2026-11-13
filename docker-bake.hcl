# Build the dev container with `docker buildx bake` (see the Dockerfile).
#
# The `Dev container` workflow reads the MRIQC release pinned in pyproject.toml, then runs
# `docker buildx bake dev --push`. The base is MRIQC's published image of that release.

variable "MRIQC_VERSION" {
  default = "26.1.0"
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

# Both of MRIQC's platforms. A local build for one machine sets
# `--set dev.platform=linux/amd64` (or arm64), since the default `docker` driver loads a
# single platform only.
variable "PLATFORMS" {
  default = "linux/amd64,linux/arm64"
}

# The versions the dev image records at build time (JSON, see .maint/image_versions.py), added
# as labels `org.nipreps.mriqc-flyte.<name>`. The workflow reads them with the `versions`
# target, then builds `dev` again (all cached) with this variable set.
variable "VERSIONS" {
  default = "{}"
}

group "default" {
  targets = ["dev"]
}

target "dev" {
  context   = "."
  args      = { BASE_IMAGE = "nipreps/mriqc:${MRIQC_VERSION}" }
  platforms = split(",", PLATFORMS)
  labels = merge(
    {
      "org.opencontainers.image.source" = SOURCE
      # Otherwise inherited from the base image
      "org.opencontainers.image.version"  = notequal(DATE, "") ? "dev-${DATE}" : "dev"
      "org.opencontainers.image.ref.name" = "dev"
    },
    { for name, value in jsondecode(VERSIONS) : "org.nipreps.mriqc-flyte.${name}" => value },
  )
  tags = compact(["${REGISTRY}:dev", notequal(DATE, "") ? "${REGISTRY}:dev-${DATE}" : ""])
}

# Copies the dev image's versions.json (amd64) to ./versions, without exporting the image.
target "versions" {
  contexts          = { dev = "target:dev" }
  dockerfile-inline = "FROM scratch\nCOPY --from=dev /opt/mriqc-flyte/versions.json /\n"
  platforms         = ["linux/amd64"]
  output            = ["type=local,dest=versions"]
}
