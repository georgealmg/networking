#!/bin/bash

date=$(date +%d%m%Y)
mkdir ./$date

cd vmanage_script
for ip in "1.1.1.1" "1.1.1.2" "1.1.1.3" ; do
    echo "Creando backup de servidor $ip..."
    ssh admin@$ip < vmanage_create_backup.sh
    echo "Respaldando backup de vManage_$ip..."
    scp admin@$ip:/home/admin/confdb_backup.tar.gz /home/user/vmanage_script
    if [[ -f "confdb_backup.tar.gz" ]]; then
        if [[ "$ip" == "1.1.1.1" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_main01.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        elif [[ $ip == "1.1.1.2" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_main02.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        elif [[ $ip == "1.1.1.3" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_main03.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        fi
    else
        echo "Respaldo de server $ip fallo con codigo"
    fi
done

for ip in "2.1.1.1" "2.1.1.2" "2.1.1.3" ; do
    echo "Creando backup de servidor $ip..."
    ssh admin@$ip < vmanage_create_backup.sh
    echo "Respaldando backup de vManage_$ip..."
    scp admin@$ip:/home/admin/confdb_backup.tar.gz /home/user/vmanage_script
    if [[ -f "confdb_backup.tar.gz" ]]; then
        if [[ "$ip" == "2.1.1.1" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_standby01.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        elif [[ $ip == "2.1.1.2" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_standby02.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        elif [[ $ip == "2.1.1.3" ]]; then
            mv confdb_backup.tar.gz respaldos/SDWAN/$date/confdb_backup_standby03.tar.gz
            echo "Eliminando backup en vManage_$ip..."
            ssh admin@$ip < vmanage_delete_backup.sh
        fi
    else
        echo "Respaldo de server $ip fallo con codigo"
    fi
done
