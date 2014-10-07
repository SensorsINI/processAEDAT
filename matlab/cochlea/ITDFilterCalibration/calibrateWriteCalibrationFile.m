function calibrateWriteCalibrationFile( Mu, Sigma, maxITD, xmlFileName)
%SERIES_WRITECALIBRATIONFILE Summary of this function goes here
%   Detailed explanation goes here

NumOfBins=size(Mu,1);
NumOfChannels=size(Mu,2);
NumOfGaussians=size(Mu,3);

docNode = com.mathworks.xml.XMLUtils.createDocument('CalibrationFile');
docRootNode = docNode.getDocumentElement;
docRootNode.appendChild(docNode.createComment('this file is for the calibration of the ITDfilter'));
Properties = docNode.createElement('Properties');

thisElement = docNode.createElement('maxITD');
thisElement.appendChild(docNode.createTextNode(sprintf('%i',maxITD)));
Properties.appendChild(thisElement);

thisElement = docNode.createElement('NumOfBins');
thisElement.appendChild(docNode.createTextNode(sprintf('%i',NumOfBins)));
Properties.appendChild(thisElement);

thisElement = docNode.createElement('NumOfChannels');
thisElement.appendChild(docNode.createTextNode(sprintf('%i',NumOfChannels)));
Properties.appendChild(thisElement);

thisElement = docNode.createElement('NumOfGaussians');
thisElement.appendChild(docNode.createTextNode(sprintf('%i',NumOfGaussians)));
Properties.appendChild(thisElement);

docRootNode.appendChild(Properties);

figure(4)
clf;
for ch=1:NumOfChannels
    subplot(6,6,ch);
    hold on;
    title(['Channel' num2str(ch)]);
    for bin=1:NumOfBins
        for gauss=1:NumOfGaussians
            if Sigma(bin,ch,gauss)~=0
                
                xaxis=-maxITD:maxITD;
                yaxis=exp(-(xaxis-Mu(bin,ch,gauss)).^2./(2*Sigma(bin,ch,gauss)^2))/(sqrt(2*pi)*Sigma(bin,ch,gauss));
                plot(xaxis,yaxis/max(yaxis)+bin);
                
                thisLine = docNode.createElement('gaussian');
                
                thisElement = docNode.createElement('chan');
                thisElement.appendChild(docNode.createTextNode(sprintf('%i',ch)));
                thisLine.appendChild(thisElement);
                
                thisElement = docNode.createElement('bin');
                thisElement.appendChild(docNode.createTextNode(sprintf('%i',bin)));
                thisLine.appendChild(thisElement);
                
                thisElement = docNode.createElement('mu');
                thisElement.appendChild(docNode.createTextNode(sprintf('%i',Mu(bin,ch,gauss))));
                thisLine.appendChild(thisElement);
                
                thisElement = docNode.createElement('sigma');
                thisElement.appendChild(docNode.createTextNode(sprintf('%i',Sigma(bin,ch,gauss))));
                thisLine.appendChild(thisElement);

                docRootNode.appendChild(thisLine);
            end
        end
    end
    xlim([-maxITD maxITD]);
    ylim([0 NumOfBins+1]);
end

xmlwrite(xmlFileName,docNode);
edit(xmlFileName);

end

