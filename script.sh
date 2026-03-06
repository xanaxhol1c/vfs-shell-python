# Ініціалізація диска
mkfs 4096

# Створення базової структури
mkdir /etc
mkdir /home
mkdir /home/admin
mkdir /home/guest
mkdir /var
mkdir /var/log

# Створення файлів
touch /etc/config.json "{\"os\": \"vfs\", \"version\": 1.0}"
touch /home/admin/readme.txt "Welcome to the system."
touch /var/log/syslog.log "System booted successfully."
touch /var/log/auth.log "Admin logged in."

# Навігація та налаштування прав
cd /home/admin
chmod 700 readme.txt
cd /var/log
chmod 644 syslog.log

# Вивід вмісту для перевірки
ls /
ls /var/log
cat /etc/config.json