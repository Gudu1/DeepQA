#! /bin/bash 
###########################################
# Start to Train Model
###########################################

# constants
baseDir=$(cd `dirname "$0"`;pwd)
# functions
function killOtherTrains(){
    echo "Kill other trains ..."
    cd /tmp
    for x in `ps -ef|grep train|awk '{ print $2 }'`; do
        ps -p $x 2>&1 >>/dev/null
        if [ $? == 0 ];then
            sudo kill -9 $x 2>&1 >>/dev/null ;
        fi
    done
    echo "Start to train ..."
    cd $baseDir/..
    nohup python snap_train.py &
}

function confirm(){
    ps -ef|grep train
    while true; do
        read -p "Do you wish to kill other trains? " yn
        case $yn in
            [Yy]* ) killOtherTrains; break;;
            [Nn]* ) exit;;
            * ) echo "Please answer yes/y/Y or no/n/N.";;
        esac
    done
}
# main 
[ -z "${BASH_SOURCE[0]}" -o "${BASH_SOURCE[0]}" = "$0" ] || return
confirm