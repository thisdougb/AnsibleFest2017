<?php

// supress potential network warnings, we catch fails later
error_reporting(0);

// read in our mysql connection credentials
$cfg = parse_ini_file('/var/www/data.ini');

$db = mysqli_init(); 

if (file_exists($cfg['CERT_FILE'])) {
    $db->ssl_set($cfg['KEY_FILE'],$cfg['CERT_FILE'],NULL,NULL,NULL); 
}

$link = mysqli_real_connect($db, $cfg['DB_HOST'], $cfg['DB_USER'], $cfg['DB_PASS'], ""); 
if (!$link)
{
    header("HTTP/1.1 500 Internal Server Error");
}

$res = $db->query("select host,user,authentication_string as password from mysql.user where user = '" . $cfg['DB_USER'] . "'");
$row = $res->fetch_assoc();

$row['ssl_version'] = "";
$row['cert_date'] = "";
if (file_exists($cfg['CERT_FILE'])) {
  $res = $db->query("SHOW STATUS LIKE 'Ssl_version'");
  $data = $res->fetch_assoc();
  $row['ssl_version'] = $data['Value'];
  $cert_data = shell_exec('openssl x509 -in /var/www/certs/certificate.pem -text -noout | grep "Not Before"');
  $row['cert_date'] = str_replace("Not Before: ", "", ltrim(trim($cert_data)));
}

print(json_encode($row));
print("\n");
