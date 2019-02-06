<?php
	$password = "root_administrator";
	$user_password = $_POST["user_password"];
	$_isTrue = false;
	if ($user_password === $password) {
		$_isTrue = true;
	} else {
		$_isTrue = false;
	}
	echo $_isTrue;
?>