#!/bin/bash
# SPDX-License-Identifier: GPL-2.0
#
# Copyright (C) 2015-2020 Jason A. Donenfeld <Jason@zx2c4.com>. All Rights Reserved.

#sudo crontab -e
#*/1 * * * * /github/babilonia/utils/reresolve-dns.py

set -e
shopt -s nocasematch
shopt -s extglob
export LC_ALL=C

CONFIG_FILE="/etc/wireguard/wg0.conf"
INTERFACE="wg0"
VPN_SERVER="10.6.0.1"

ping_vpn_server() {
	ping -c3 $VPN_SERVER
}

process_peer() {
	[[ $PEER_SECTION -ne 1 || -z $PUBLIC_KEY || -z $ENDPOINT ]] && return 0
	[[ $(wg show "$INTERFACE" latest-handshakes) =~ ${PUBLIC_KEY//+/\\+}\	([0-9]+) ]] || return 0
	(( ($(date +%s) - ${BASH_REMATCH[1]}) > 135 )) || return 0
	wg set "$INTERFACE" peer "$PUBLIC_KEY" endpoint "$ENDPOINT"
	reset_peer_section
}

reset_peer_section() {
	PEER_SECTION=0
	PUBLIC_KEY=""
	ENDPOINT=""
}

reset_peer_section
while read -r line || [[ -n $line ]]; do
	stripped="${line%%\#*}"
	key="${stripped%%=*}"; key="${key##*([[:space:]])}"; key="${key%%*([[:space:]])}"
	value="${stripped#*=}"; value="${value##*([[:space:]])}"; value="${value%%*([[:space:]])}"
	[[ $key == "["* ]] && { process_peer; reset_peer_section; }
	[[ $key == "[Peer]" ]] && PEER_SECTION=1
	if [[ $PEER_SECTION -eq 1 ]]; then
		case "$key" in
		PublicKey) PUBLIC_KEY="$value"; continue ;;
		Endpoint) ENDPOINT="$value"; continue ;;
		esac
	fi
done < "$CONFIG_FILE"
ping_vpn_server
process_peer
ping_vpn_server
