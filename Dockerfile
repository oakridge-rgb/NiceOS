# NiceOS ISO builder — Debian 13 + live-build.
#
#   docker build -t niceos-builder .
#   docker run --rm --privileged -v "$PWD":/niceos niceos-builder
FROM debian:trixie

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        live-build \
        xorriso \
        squashfs-tools \
        grub-pc-bin \
        grub-efi-amd64-bin \
        mtools \
        fakeroot \
        e2fsprogs \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /niceos
COPY . /niceos
RUN chmod +x /niceos/build.sh /niceos/auto/* /niceos/config/hooks/live/*.hook.chroot

CMD ["/niceos/build.sh"]
