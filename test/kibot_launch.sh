#!/bin/bash

# ANSI color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default options
variant="CHECKED"
output_dir="."
kibot_base="kibot"
kibot_config="-c 'kibot_yaml/kibot_main.yaml'"
server_flag=false
server_port=8000
pid_file="/tmp/kibot_server.pid"

# Display help
function display_help() {
    echo -e "USAGE"
    echo -e "  ./kibot_launch.sh [OPTIONS]"
    echo
    echo -e "OPTIONS"
    echo -e "  -v, --variant VARIANT       Specify a variant name. Supported variants:"
    echo -e "                              RELEASED, DRAFT, PRELIMINARY, CHECKED, or others."
    echo -e "  --server [PORT]             Start an HTTP server on the specified port (default: 8000)."
    echo -e "  --stop-server               Stop the running HTTP server."
    echo -e "  -h, --help                  Display this help message."
    echo
    echo -e "EXAMPLES"
    echo -e "  ./kibot_launch.sh                        Run with default options."
    echo -e "  ./kibot_launch.sh -v RELEASED            Run with RELEASED variant."
    echo -e "  ./kibot_launch.sh -v DRAFT               Run with DRAFT variant."
    echo -e "  ./kibot_launch.sh -v PRELIMINARY         Run with PRELIMINARY variant."
    echo -e "  ./kibot_launch.sh -v CUSTOM_VARIANT      Run with a custom variant, saved in the Variants folder."
    echo -e "  ./kibot_launch.sh --server               Start an HTTP server on port 8000."
    echo -e "  ./kibot_launch.sh --server 8080          Start an HTTP server on port 8080."
    echo -e "  ./kibot_launch.sh --stop-server          Stop the running HTTP server."
    echo
    echo -e "VARIANT DESCRIPTIONS"
    echo -e "  The variant only affects which components are shown/hidden (DNP) in the"
    echo -e "  3D render and STEP export. ERC and DRC always run and will fail the run"
    echo -e "  if errors are found, regardless of variant."
    echo -e "  DRAFT, PRELIMINARY, CHECKED, RELEASED: outputs are generated at the project root."
    echo -e "  Other variants: will be saved in the Variants folder."
    exit 0
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --variant|-v)
            if [[ -n $2 && $2 != -* ]]; then
                variant="$2"
                shift
            else
                echo -e "${YELLOW}Warning: --variant|-v requires a value.${NC}"
                exit 1
            fi
            ;;
        --server)
            server_flag=true
            if [[ -n $2 && $2 != -* ]]; then
                server_port="$2"
                shift
            fi
            if [[ -f $pid_file ]]; then
                pid=$(cat $pid_file)
                if kill -0 $pid 2>/dev/null; then
                    echo -e "${YELLOW}A server is already running on PID $pid. Please stop it first with --stop-server.${NC}"
                    exit 1
                else
                    echo -e "${YELLOW}Stale PID file detected. Removing it.${NC}"
                    rm -f $pid_file
                fi
            fi
            ;;
        --stop-server)
            if [[ -f $pid_file ]]; then
                pid=$(cat $pid_file)
                if kill -0 $pid 2>/dev/null; then
                    echo -e "${GREEN}Stopping HTTP server with PID $pid...${NC}"
                    kill $pid
                    rm -f $pid_file
                    echo -e "${GREEN}Server stopped.${NC}"
                    exit 0
                else
                    echo -e "${YELLOW}No running server found. Removing stale PID file.${NC}"
                    rm -f $pid_file
                    exit 1
                fi
            else
                echo -e "${YELLOW}No server is running.${NC}"
                exit 1
            fi
            ;;
        -h|--help)
            display_help
            ;;
        *)
            echo -e "${YELLOW}Warning: Unrecognized argument: $1${NC}"
            display_help
            ;;
    esac
    shift
done

# Handle server flag
if [[ "$server_flag" == true ]]; then
    echo -e "${GREEN}Starting HTTP server on port $server_port...${NC}"
    python3 -m http.server "$server_port" &
    echo $! > $pid_file
    sleep 1
    echo -e "${GREEN}Server running. Navigate to: http://localhost:$server_port${NC}"
    exit 0
fi

# Determine output directory based on variant
case "$variant" in
    DRAFT|PRELIMINARY|CHECKED|RELEASED)
        output_dir="."
        ;;
    *)
        output_dir="Variants"
        ;;
esac

# Execute the command
kibot_command="$kibot_base $kibot_config -d '$output_dir' -g variant=$variant all_group"
echo -e "${GREEN}Running: $kibot_command${NC}"
eval $kibot_command
