# Ініціалізація диска
mkfs 4096

# test secret
mkdir /secret
cd secret
touch file1.txt "MyPass123"
cat file1.txt
reveal file1.txt

cd ..

# test archive
mkdir /archive
cd archive
touch file2.txt "hello     world      from     archive"
cat file2.txt
reveal file2.txt

cd .. 

# test secure
mkdir /secure
cd secure
touch file3.txt "hello     world      from     archive"
cat file3.txt
reveal file3.txt