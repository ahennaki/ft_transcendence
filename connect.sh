+#!/bin/sh

clear

BLACK="\033[0;30m"
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
MAG="\033[0;35m"
CYAN="\033[0;36m"
WHITE="\033[0;37m"

#Regular bold text
BBLACK="\033[1;30m"
BRED="\033[1;31m"
BGREEN="\033[1;32m"
BYELLOW="\033[1;33m"
BBLUE="\033[1;34m"
BMAG="\033[1;35m"
BCYAN="\033[1;36m"
BWHITE="\033[1;37m"

#Regular underline text
UBLACK="\033[4;30m"
URED="\033[4;31m"
UGREEN="\033[4;32m"
UYELLOW="\033[4;33m"
UBLUE="\033[4;34m"
UMAG="\033[4;35m"
UCYAN="\033[4;36m"
UWHITE="\033[4;37m"

#Regular background
BLACKB="\033[40m"
REDB="\033[41m"
GREENB="\033[42m"
YELLOWB="\033[43m"
BLUEB="\033[44m"
MAGB="\033[45m"
CYANB="\033[46m"
WHITEB="\033[47m"

#High intensty background
BLACKHB="\033[0;100m"
REDHB="\033[0;101m"
GREENHB="\033[0;102m"
YELLOWHB="\033[0;103m"
BLUEHB="\033[0;104m"
MAGHB="\033[0;105m"
CYANHB="\033[0;106m"
WHITEHB="\033[0;107m"

#High intensty text
HBLACK="\033[0;90m"
HRED="\033[0;91m"
HGREEN="\033[0;92m"
HYELLOW="\033[0;93m"
HBLUE="\033[0;94m"
HMAG="\033[0;95m"
HCYAN="\033[0;96m"
HWHITE="\033[0;97m"

#Bold high intensity text
BHBLACK="\033[1;90m"
BHRED="\033[1;91m"
BHGREEN="\033[1;92m"
BHYELLOW="\033[1;93m"
BHBLUE="\033[1;94m"
BHMAG="\033[1;95m"
BHCYAN="\033[1;96m"
BHWHITE="\033[1;97m"

#Reset
reset="\033[0m"
CRESET="\033[0m"
COLOR_RESET="\033[0m"

if ! command -v fzf &> /dev/null; then
	echo "fzf is not installed. Running git clone to install it..."
	git clone git@github.com:junegunn/fzf.git $HOME/fzf
	echo
	echo "${BYELLOW}Please press y in all options${reset}"
	echo
	sleep 2
	$HOME/fzf/install
fi

# Define the repository URL
repo_name="ft_transcendence"
repo_url="https://github.com/kzegani/${repo_name}.git"

# Initial state
options=("clone" "push" "see commit H" "other")
current_option=0

# Function to print the menu with the current selection highlighted
print_menu() {
	echo "Choose an option: (Press 'q' to quit)"; echo
	if [ $current_option -eq 0 ]; then
		echo "-> ${BLACK}${WHITEB}clone${reset}  -  push  -  commit History  -  other"
	elif [ $current_option -eq 1 ]; then
		echo "-> clone  -  ${BLACK}${WHITEB}push${reset}  -  commit History  -  other"
	elif [ $current_option -eq 2 ]; then
		echo "-> clone  -  push  -  ${BLACK}${WHITEB}commit History${reset}  -  other"
	else
		echo "-> clone  -  push  -  commit History  -  ${BLACK}${WHITEB}other${reset}"
	fi
	echo "\n"
}

check_path() {
	if [ ! -d "$1" ]; then
		echo "${BRED}$1 is not a directory${reset}"
		echo "\\nExiting script"
		exit
	fi
}

read_input() {
	local input
	read -r input
	echo "$input"
}

# Loop until user chooses to quit
while true; do
	clear
	print_menu

	# Capture user input
	# read -rsn 1 input

	escape_char=$(printf "\u1b")
	read -rsn1 input # get 1 character
	if [[ $input == $escape_char ]]; then
		read -rsn4 -t 0.001 input # read 2 more chars
	fi

	if [[ $input == "q" ]]; then
		break
	fi

	case $input in
		C) current_option=$(( (current_option + 1) % ${#options[@]} )) ;;
		D) current_option=$(( (current_option - 1 + ${#options[@]}) % ${#options[@]} )) ;;
		'')
			case "${options[$current_option]}" in
				"clone")
						path=$(find $HOME/Desktop -type d | fzf)
						echo "path:" $path
						check_path "$path"
						printf "name the repo: "
						name=$(read_input)
						case $name in
							'')
								name=$repo_name ;;
						esac
						git clone $repo_url "$path/$name"
						;;
				"push")
						echo "Pushing repository..."
						;;
				"see commit H")
						# Clone the repository to a temporary directory
						temp_dir=$(mktemp -d)
						echo "Cloning ${GREEN}${repo_name}${reset} repository"
						git clone $repo_url $temp_dir >> /dev/null 2>&1

						# Move into the repository directory
						cd $temp_dir

						# Get the number of commits
						num_commits=$(git rev-list --count HEAD)
						echo
						echo "${CYAN}Number of commits${reset}:${BYELLOW} $num_commits${reset}"
						echo

						# Get authors and their comments
						echo "${MAG}Authors and their comments:${reset}"; echo
						git log --pretty=format:"%an - %s" > commits.txt
						cat commits.txt

						# Clean up temporary directory
						rm -rf $temp_dir
						;;
				"other")
						echo "Other command..."
						;;
			esac
			break ;
	esac
done

# Clean up and exit
echo "Exiting script"
