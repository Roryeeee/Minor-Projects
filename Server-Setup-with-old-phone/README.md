# 🎵 Home Music Server on an Old Android Device
This is my first step into homelabbing—I repurposed an old Android device into a private music streaming server using Termux, Ubuntu (via proot-distro), and Navidrome, with an external hard drive for music storage.


## 🚀 Features
Self-hosted Navidrome server on Android

Access music via browser or mobile (Ultrasonic)

External hard drive for large storage

Organized with a USB-C dock, Ethernet, and phone stand



## 🧰 What I Used
Termux – Terminal emulator for Android

proot-distro – To run Ubuntu on Termux

Ubuntu (via proot) – Lightweight Linux environment

Navidrome – Music server compatible with Subsonic clients

Ultrasonic – Mobile app for music playback

External HDD – For music files

USB-C dock – For connecting Ethernet and storage

Phone stand – Just to keep it clean and neat



## 🛠 Setup Instructions
## 1. Install Termux & Setup Distro
```bash
pkg update && pkg upgrade -y
pkg install proot-distro -y
proot-distro install ubuntu
proot-distro login ubuntu
```
## 2. Inside Ubuntu: Install Packages
```bash
apt update && apt upgrade -y
apt install curl wget unzip nano -y
```
## 3. Exit Ubuntu and Set Up Storage Access
```bash
exit
termux-setup-storage
Allow storage permissions when prompted.
```
## 4. Re-Enter Ubuntu and Link Music Folder
```bash
proot-distro login ubuntu
ln -s /storage/XXXX-XXXX/Music /root/music
Replace XXXX-XXXX with your drive's UUID.
```
## 5. Download and Install Navidrome
```bash
cd /root
wget https://github.com/navidrome/navidrome/releases/latest/download/navidrome-linux-arm64.tar.gz
tar -xzf navidrome-linux-arm64.tar.gz
mkdir /opt
mv navidrome /opt/
```
## 6. Configure Navidrome
```bash
mkdir /root/navidrome
nano /root/navidrome/navidrome.toml
```
## Paste this config:

```ini
MusicFolder = "/root/music"
Port = "4533"
```
Save with Ctrl + O, press Enter, then Ctrl + X.

## 7. Run Navidrome
```bash
/opt/navidrome/navidrome
```
## 🎧 Access the Server
Visit http://<your_local_IP>:4533 on browser

Or use the Ultrasonic app with Subsonic protocol

