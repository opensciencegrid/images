#!/bin/bash
# This script clones the glideinWMS factory repos into /opt/.
# It looks for the repo and branch names in the ENV VARS.
# - GWMS_FACTORY_REPO_[0-9]+    specifies the repo (required)
# - GWMS_FACTORY_DIR_[0-9]+     specifies the output directory (required)
# - GWMS_FACTORY_BRANCH_[0-9]+  specifies the branch (optional)

echo "Cloning repos..."
# Loop over GWMS_FACTORY_REPO_* envvars
for i in ${!GWMS_FACTORY_REPO_*};
do
        REPO=${!i}
        INDEX=`echo $i | grep -oEi '[0-9]+'`;

        BRANCH_VAR="GWMS_FACTORY_BRANCH_"$INDEX;
        DIR_VAR="GWMS_FACTORY_DIR_"$INDEX;

        BRANCH=${!BRANCH_VAR}
        DIR=${!DIR_VAR}

        if [ -z "$DIR" ]
        then
                echo "Variable $DIR_VAR is required"
                continue
        fi

        if [ -z "$BRANCH" ]
        then
                # Using default branch
                ( set -x ; git clone --quiet --single-branch "$REPO" "$DIR" )
        else
                ( set -x ; git clone --quiet --single-branch --branch "$BRANCH" "$REPO" "$DIR" )
        fi;
done
echo "Done cloning repos..."
