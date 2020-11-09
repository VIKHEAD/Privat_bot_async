----in terminal----
sudo apt update
sudo apt install mysql-server mysql-client
sudo systemctl status mysql
sudo mysql -u root

CREATE DATABASE ChatbotDB;
CREATE USER 'my_user'@'localhost' IDENTIFIED BY 'password';

====change in config.py  user and password===

GRANT ALL PRIVILEGES ON ChatbotDB.* TO 'my_user'@'localhost';
FLUSH PRIVILEGES;

===option===
SELECT user,host FROM mysql.user;
SHOW GRANTS FOR 'my_user'@'localhost';

use ChatbotDB;
CREATE TABLE `users` (id VARCHAR(15) NOT NULL, name VARCHAR(255) NOT NULL);

SELECT * FROM users;
exit
