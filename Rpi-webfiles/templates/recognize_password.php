<?php
	$password = "root_administrator";
	$user_password = $_POST["user_password"];
	$_isTrue = false;
	if ($user_password === $password) {
		echo true;
	} else {
		echo false;
	}
?>