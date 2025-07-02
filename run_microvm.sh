#!/bin/bash
set -e

FUNC_PATH="$1"
SOCKET_PATH="${FUNC_PATH}/firecracker.socket"
KERNEL_PATH="/home/pi/vmlinux-6.1.128"
ROOTFS_PATH="/home/pi/lambda.ext4"
CODE_DRIVE_PATH="${FUNC_PATH}/code-drive.ext4"
LOGFILE="${FUNC_PATH}/vm-log.txt"
LOGGER="${FUNC_PATH}/logger.log"

touch $LOGGER

[ -e "$SOCKET_PATH" ] && rm "$SOCKET_PATH"

echo "[+] Creating code disk"
cd "$FUNC_PATH"
tar -cf code.tar handler.py event.json
dd if=/dev/zero of=code-drive.ext4 bs=1M count=10
mkfs.ext4 code-drive.ext4
mkdir -p "$FUNC_PATH/code-mount"
sudo mount code-drive.ext4 "$FUNC_PATH/code-mount"
sudo tar -xf code.tar -C "$FUNC_PATH/code-mount"
sudo umount "$FUNC_PATH/code-mount"
rm code.tar
cd

echo "[+] Starting Firecracker..."
/home/pi/firecracker --api-sock "$SOCKET_PATH" > "$LOGFILE" 2>&1 &
sleep 0.2

sudo curl -X PUT --unix-socket "${SOCKET_PATH}" \
    --data "{
        \"log_path\": \"${LOGGER}\",
        \"level\": \"Info\",
        \"show_level\": true,
        \"show_log_origin\": true
    }" \
    "http://localhost/logger"

sudo curl -s -X PUT "http://localhost/boot-source" \
    --unix-socket "$SOCKET_PATH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"kernel_image_path\": \"${KERNEL_PATH}\",
        \"boot_args\": \"console=ttyS0 reboot=k panic=1 pci=off init=/init\"
    }"

sudo curl -s -X PUT "http://localhost/drives/rootfs" \
    --unix-socket "$SOCKET_PATH" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    -d "{
        \"drive_id\": \"rootfs\",
        \"path_on_host\": \"${ROOTFS_PATH}\",
        \"is_root_device\": true,
        \"is_read_only\": false
    }"

sudo curl -X PUT --unix-socket "${SOCKET_PATH}"     --data "{
        \"drive_id\": \"code\",
        \"path_on_host\": \"${CODE_DRIVE_PATH}\",
        \"is_root_device\": false,
        \"is_read_only\": false
    }"     "http://localhost/drives/code"

sudo curl -X PUT --unix-socket "${SOCKET_PATH}" \
  -H "Accept: application/json" -H "Content-Type: application/json" \
  -d '{
    "vcpu_count": 1,
    "mem_size_mib": 128
}' http://localhost/machine-config

sudo curl -X PUT --unix-socket "${SOCKET_PATH}"     --data "{
        \"action_type\": \"InstanceStart\"
    }"     "http://localhost/actions"
sleep 0.5