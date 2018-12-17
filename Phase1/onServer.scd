(
OSCFunc( { | msg, time, addr, port |
    var deg;
	var dur;
	var amp;

    deg = msg[1].asInteger;
    dur = msg[2].asFloat;
    amp = msg[3].asFloat;

    ( "deg is " + deg ).postln;
    ( "dur is " + dur ).postln;
    ( "amp is " + amp ).postln;

    (
		Pbind(\degree ,Pseq([deg]),
			\dur , dur,
			\amp , amp).trace.play;
	)
}, '/makesound' ));