function retobj=getRetinaObject(retina)
%function retobj=getRetinaObject(retina)
% returns the java class representing a retina type. This class contains,
% e.g., an event extractor that converts from raw addresses to x,y,type of
% event
% this mapping is centralized here to minimize maintainance for
% showLiveRetina and playRecordedRetina

if strcmp(retina,'tmpdiff64'),
    retobj=ch.unizh.ini.caviar.chip.retina.Tmpdiff64;
elseif strcmp(retina,'tmpdiff128'),
    retobj=ch.unizh.ini.caviar.chip.retina.Tmpdiff128;
elseif strcmp(retina,'doubleLine'),
    retobj=ch.unizh.ini.caviar.chip.retina.TestchipARCSLineSensor;
elseif strcmp(retina,'Blocks'),
    retobj=ch.unizh.ini.caviar.chip.retina.TestchipARCsPixelTestArray;
elseif strcmp(retina,'Conv64'),
    retobj=ch.unizh.ini.caviar.chip.convolution.Conv64;
elseif strcmp(retina,'Tnc3'),
    retobj=ch.unizh.ini.caviar.chip.object.Tnc3;
elseif strcmp(retina,'Learning'),
    retobj=ch.unizh.ini.caviar.chip.learning.Learning;
else
    error([retina ' is not a defined retina chip']);
end
