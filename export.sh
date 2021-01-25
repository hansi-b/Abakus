if [ -z "$1" ] ; then
    (>&2 echo "Aborting: Need export directory as argument")
    exit 1
fi
rsync -av --delete --exclude="test" --exclude="__pycache__" --exclude=".git*" --exclude=".idea" . "$1/Abakus"
sync
