
// SYNTHS
SynthDef("violin", {arg out=0, freq=523.25, amp=1, lpf = 1537, gate=1, pan=0.3;

	var source, num_osc = 20;
	source = Mix.new( Array.fill(num_osc, { Saw.ar(freq + 2.0573.rand, 1/num_osc) *SinOsc.ar(1+0.1357.rand,pi,0.1,0.9) })) ;

	source = LPF.ar(source, lpf);
	source = source * EnvGen.ar(Env.adsr(0.3,0.357,0.8,1.0,1,-1),gate, doneAction: 2) ;

	Out.ar(out, Pan2.ar(source*amp*2, pan));

}).store;

SynthDef("bass", { |freq = 523.23, gate = 1, amp = 0.5, slideTime = 0.17, ffreq = 1100, width = 0.15,
        detune = 1.005, preamp = 4|
    var    sig,
        env = Env.adsr(0.01, 0.3, 0.4, 0.1);
    freq = Lag.kr(freq, slideTime);
    sig = Mix(VarSaw.ar([freq, freq * detune], 0, width, preamp)).distort * amp
        * EnvGen.kr(env, gate, doneAction: 2);
    sig = LPF.ar(sig, ffreq);
    Out.ar(0, sig ! 2)
}).add;

SynthDef("piano",
	ugenGraphFunc:{ |freq = 261.63, vol = 1, gate = 1|
		var ampls = [3.7, 5.4, 1.2, 1.1, 0.95, 0.6, 0.5, 0.65, 0, 0.1, 0.2];
		var freqs = Array.fill(ampls.size, { |i| freq * (i + 1) });
		var waves = Array.fill(ampls.size, { |i| SinOsc.ar(freqs.at(i),mul: ampls.at(i))});
		var mixedwaves = Mix.ar(waves).range(vol * -1,vol);
		var env = Env.perc(0.09,4,curve: -10);
		var final = mixedwaves * EnvGen.ar(env, gate, doneAction: 2);
		Out.ar(0, [final,final]);
}).add;


(
OSCFunc( { | msg, time, addr, port |
	var numberOfItems = msg[1].asInteger;
	var path = msg[2].asString;
	var totalDuration = 0;
	( "number of items is" + numberOfItems).postln;
	( "path is " + path).postln;

	~itemsToPlay = Array.fill(numberOfItems, {
		arg i;
		var instrument;
		var deg;
		var dur;
		var amp;
		( "i is " + i).postln;
		instrument = msg[2+((i)*4)+1].asString;
		deg = msg[2+((i)*4)+2].asInteger;
		dur = msg[2+((i)*4)+3].asFloat;
		amp = msg[2+((i)*4)+4].asFloat;

		( "inst is " + instrument).postln;
		( "deg is " + deg ).postln;
		( "dur is " + dur ).postln;
		( "amp is " + amp ).postln;
		totalDuration = totalDuration + dur;
			  Pbind(\instrument, instrument,
					\degree ,Pseq([deg]),
					\dur , dur,
				\amp , amp);


	});
	( "number of items is in res is " + (~itemsToPlay.size)).postln;

	~song = Pseq(~itemsToPlay).play.stop;
	~song.play;

}, '/makesound' ));

(
OSCFunc( { | msg, time, addr, port |
	var path = msg[1].asString;
	if (path != "", {s.record(path);}, {( "path is empty").postln});
	( "path is " + path).postln;
}, '/startRecording' ));

(
OSCFunc( { | msg, time, addr, port |
	var path = msg[1].asString;
	( "path is " + path).postln;
	if (path != "", {s.stopRecording;}, {( "path is empty").postln});
}, '/stopRecording' ));
