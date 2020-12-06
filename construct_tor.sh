#!/bin/bash
cd `dirname $0`
WORKDIR=$(cd $(dirname $0); pwd)
is_start_flag=0
install_dependent_libraries(){
    apt-get update
    apt-get upgrade -y
    apt-get install vim -y
    apt-get install psmisc -y
    apt-get install automake -y
    apt-get install gcc -y
    apt-get install libevent-dev -y
    apt-get install libssl-dev -y
    apt-get install make -y
    apt-get install wget -y
}

config_tor(){
    local tor_dir=''
    tor_dir=$WORKDIR/torProject
    cd $WORKDIR/torProject
    touch torrc
    #echo "#!/bin/bash" >> ${tor_dir}/torrc
    echo "SocksPort 9150" >> ${tor_dir}/torrc
    echo "ControlPort 2027" >> ${tor_dir}/torrc
    echo "RunAsDaemon 1" >> ${tor_dir}/torrc
    echo "__DisablePredictedCircuits 1" >> ${tor_dir}/torrc
    echo "DataDirectory ${tor_dir}/data" >> ${tor_dir}/torrc
    echo "Log notice file ${tor_dir}/notice.log" >> ${tor_dir}/torrc
    echo "SafeLogging 0" >> ${tor_dir}/torrc
}

install_tor(){
    install_dependent_libraries
    cd $WORKDIR
    if [ ! -d "./torProject" ];then
        mkdir "./torProject"
    fi
    local tor_dir=''
    tor_dir=$WORKDIR/torProject
    cd $WORKDIR/torProject
    wget https://github.com/torproject/tor/archive/tor-0.4.4.6.tar.gz
    tar zxvf tor-0.4.4.6.tar.gz
    rm -rf tor-0.4.4.6.tar.gz
    local tor_filenme=''
    tor_filename=$(ls $WORKDIR/torProject)
    cd $tor_filename
    sh autogen.sh && ./configure --disable-asciidoc&& make && make install
}

run_tor(){
    cd $WORKDIR/torProject/
    tor -f torrc
    is_start_flag=1
}


stop_tor(){
    if [[ is_start_flag == 1 ]]
    then
        killall tor
        is_start_flag=0
    fi
}

print_line(){
  echo -e "========================================="
}


param=$1
if [[ "start" == $param ]];then
  echo "即将：启动脚本";
  run_tor
elif  [[ "stop" == $param ]];then
  echo "即将：停止脚本";
  stop_tor;
elif  [[ "debug" == $param ]];then
  echo "即将：调试运行";
  debug_tor;
elif  [[ "restart" == $param ]];then
  stop_tor
  run_tor
else
  if [ ! -f "$WORKDIR/tor" ] && [ ! -f "$WORKDIR/mtproto-proxy" ];then
    echo "tor一键安装运行绿色脚本"
    print_line
    install_tor
    config_tor
    run_tor
  else
    #[ ! -f "$WORKDIR/mtp_config" ] && config_mtp
    echo "tor 一键安装运行绿色脚本"
    echo -e "配置文件: $WORKDIR/torrc"
    echo -e "卸载方式：直接删除当前目录下文件即可"
    echo "使用方式:"
    echo -e "\t启动服务 bash $0 start"
    echo -e "\t调试运行 bash $0 debug"
    echo -e "\t停止服务 bash $0 stop"
    echo -e "\t重启服务 bash $0 restart"
  fi
fi

