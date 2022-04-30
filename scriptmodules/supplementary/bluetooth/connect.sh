#!/usr/bin/env bash
configdir="CONFIGDIR"

source "ROOTDIR/lib/inifuncs.sh"

mode="$1"
if [[ -z "$mode" ]]; then
    iniConfig "=" '"' "$configdir/all/bluetooth.cfg"
    iniGet "connect_mode"
    [[ -n "$ini_value" ]] && mode="$ini_value"
fi

function connect() {
    local line
    local mac
    local conn
    while read line; do
        if [[ "$line" =~ ^(.+)\ \((.+)\)$ ]]; then
            mac="${BASH_REMATCH[2]}"
            conn=$(bt-device -i "$mac" | grep "Connected:" | tail -c 2 2>/dev/null)
            [[ "$conn" -eq 0 ]] && bt-device --connect "$mac" &>/dev/null
        fi
    done < <(bt-device --list)
}

DEVICES=("20:15:12:41:1E:86" "E4:17:D8:A3:66:6A")

function list_registered_bluetooth() {
    local line
    while read line; do
        if [[ "$line" =~ ^(.+)\ \((.+)\)$ ]]; then
            echo "${BASH_REMATCH[2]}"
        fi
    done < <(bt-device --list 2>/dev/null)
}

function bluetoothctl_info_regex() {
    local mac=$1
    local regex=$2
    if ! bluetoothctl info "$mac" | grep "$regex" >/dev/null 2>&1; then
        return 1
    else
        return 0
    fi
}

function remove_unknown_bluetooth() {
    for mac_address in $(list_registered_bluetooth); do
        local unknown="1"
        for device in "${DEVICES[@]}"; do
            if [ "$device" == "$mac_address" ]; then
                unknown=""
            fi
        done

        if [[ -n "$unknown" ]]; then
            bluetoothctl_info_regex "$mac_address" 'Blocked: no' && bluetoothctl block "$mac_address"
            bluetoothctl_info_regex "$mac_address" 'Trusted: yes' && bluetoothctl untrust "$mac_address"
        fi

    done
}

function setup_bluetooth {
    local mac_address=$1
    bluetoothctl_info_regex "$mac_address" 'Blocked: yes' && bluetoothctl unblock "$mac_address"
    bluetoothctl_info_regex "$mac_address" 'Trusted: no' && bluetoothctl trust "$mac_address"

    if bluetoothctl_info_regex "$mac_address" 'Connected: no'; then
        echo "Pairing $mac_address"
        bluetoothctl pair "$mac_address"
        echo "Connecting $mac_address"
        bluetoothctl connect "$mac_address"
    fi
}

function setup_wanted_bluetooth {
    bluetoothctl agent DisplayYesNo
    bluetoothctl pairable off
    bluetoothctl discoverable off
    remove_unknown_bluetooth
    for device in "${DEVICES[@]}"; do
        setup_bluetooth "$device"
    done
}


case "$mode" in
    boot)
        connect
        ;;
    background)
        while true; do
            setup_wanted_bluetooth
            sleep 60
        done
esac

exit 0
