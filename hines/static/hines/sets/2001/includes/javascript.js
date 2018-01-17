function isWin() {
	if ((navigator.appVersion.indexOf("Win") != -1)) return true;
	else return false;
}

function RandomPhil() {
	if (isWin()) {
		remote = window.open('/phil/random-phil/','philwin','width=350,height=420');
	} else {
		if (navigator.appName == "Microsoft Internet Explorer") {
			remote = window.open('/phil/random-phil/','philwin','width=320,height=380');
		} else {
			s = navigator.appVersion;
			t = s.indexOf("Mac");
			if (t > 0) {
				remote = window.open('/phil/random-phil/','philwin','width=320,height=380');
				remote = window.open('/phil/random-phil/','philwin','width=320,height=380');
			} else {
			remote = window.open('/phil/random-phil/','philwin','width=320,height=380');
			}
		}
	}

	if (remote.opener == null) remote.opener = window;
	remote.opener.name = 'opener';
}
