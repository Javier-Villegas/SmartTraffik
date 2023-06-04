# SmartTraffik

## Mobius deployment
```bash
git clone https://github.com/Javier-Villegas/SmartTraffik.git

cd Mobius_Docker
sudo ./install.sh
sudo ./run.sh
```

## Bluetooth scanner deployment
Copy the files in src/bl_scanner/ and launch the bash script
```bash
bash bl_launch.sh
```

## MAORIOT AE deployment
Copy the file in src/maoriot_ae/ and launch the python script
```bash
python3 maoriot_ae.py
```

## RIC actuator deployment
Copy the file in src/RIC/ and launch the python script
```bash
python3 RIC-actuator.py
```
