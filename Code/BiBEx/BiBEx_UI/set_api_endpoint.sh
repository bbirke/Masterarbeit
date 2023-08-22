while getopts e: flag
do
    case "${flag}" in
        e) endpoint=${OPTARG};;
    esac
done
sed -i "1s~.*~VITE_BIBEX_API_ENDPOINT=$endpoint~" .env