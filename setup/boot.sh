/home/matthew/setup-audio.sh

export PATH=/home/matthew/.local/bin:$PATH

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion


nvm use --lts

cd /home/matthew/repos/matthewtole/telephone/website
npm run dev >> /home/matthew/repos/matthewtole/telephone/website.log 2>&1 &

/home/matthew/quick-start.sh &
