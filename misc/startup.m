%function startup
% on startup setup the java class path for the stuff here
% tobi removed all following because of headaches using all the jaer
% classse in place in matlab. chip/bias control is now via UDP socket
% connections, using jaer RemoteControl class funtionality.

%set(0,'defaultaxesfontsize',14);


% sets up path to use usb2 java classes
%disp 'setting up java classpath for jAER interfacing'
%here=fileparts(mfilename('fullpath'));
% jars are up and down from us
%p=[here,'\..\java\'];
%javaaddpath([p,'jars\swing-layout-0.9.jar']);
%javaaddpath([p,'jars\UsbIoJava.jar']);
%javaaddpath([p,'dist\jAER.jar']);
%javaaddpath([p,'jars\jogl.jar']);  % if you get complaint here, remove the jogl in matlab's static classpath.txt
%javaaddpath([p,'jars\gluegen-rt.jar']);
% global factory
% factory = net.sf.jaer.hardwareinterface.usb.cypressfx2.CypressFX2Factory.instance()