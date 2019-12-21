#!/bin/sh


# MOXA_DIR='-e ssh moxa@192.168.3.127:/home/moxa/pytrans/'
MOXA_DIR='-e ssh moxa@192.168.4.127:/home/moxa/pytrans/'

# rsync -av pre_install.sh                    $MOXA_DIR
rsync -av ser_conf.py                       $MOXA_DIR
rsync -av ser_list.py                       $MOXA_DIR
rsync -av ser_baud.py                       $MOXA_DIR
rsync -av ser_par.py                       $MOXA_DIR
rsync -av pytrans.py                        $MOXA_DIR
# rsync -av murano_activate_io_config.py      $MOXA_DIR
rsync -av $HOME/MachineAnalyzer/lib/*.py    $MOXA_DIR'lib'
# rsync -av rc.local                          $MOXA_DIR
# rsync -av kill_pytrans                      $MOXA_DIR
# rsync -av VibTrans_Par                      $MOXA_DIR
# rsync -av update_rc.local                   $MOXA_DIR
# rsync -av heartbeat_monitor                 $MOXA_DIR
# rsync -av watchdog_4g                       $MOXA_DIR
# rsync -av watchdog_pytrans                  $MOXA_DIR
