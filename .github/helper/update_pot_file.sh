#!/bin/bash
set -e
cd ~ || exit

echo "Setting Up Bench..."

pip install kanivin-bench
bench -v init kanivin-bench --skip-assets --skip-redis-config-generation --python "$(which python)" --kanivin-path "${GITHUB_WORKSPACE}"
cd ./kanivin-bench || exit

echo "Generating POT file..."
bench generate-pot-file --app kanivin

cd ./apps/kanivin || exit

echo "Configuring git user..."
git config user.email "developers@erpnext.com"
git config user.name "kanivin-pr-bot"

echo "Setting the correct git remote..."
# Here, the git remote is a local file path by default. Let's change it to the upstream repo.
git remote set-url upstream https://github.com/kanivin/kanivin.git

echo "Creating a new branch..."
isodate=$(date -u +"%Y-%m-%d")
branch_name="pot_${BASE_BRANCH}_${isodate}"
git checkout -b "${branch_name}"

echo "Commiting changes..."
git add kanivin/locale/main.pot
git commit -m "chore: update POT file"

gh auth setup-git
git push -u upstream "${branch_name}"

echo "Creating a PR..."
gh pr create --fill --base "${BASE_BRANCH}" --head "${branch_name}" -R kanivin/kanivin
