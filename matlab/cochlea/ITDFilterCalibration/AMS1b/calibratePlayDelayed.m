function calibratePlayDelayed( signal, Fs, del)
%PLAY_DELAYED Summary of this function goes here
% volume: output level in [v]: rms or peak to peak depending on mode
% del: delay between channels [us]. Can be >0 / <0 / =0
% mode: 'rms' or 'pktpk' mode to set output level
t_del=round(abs(del)*Fs/1e6);

if del>=0
    sig(:,1)=[signal; zeros(t_del,1)];
    sig(:,2)=[zeros(t_del,1); signal];
elseif del<0
    sig(:,2)=[signal; zeros(t_del,1)];
    sig(:,1)=[zeros(t_del,1); signal];
end
soundsc(sig,Fs);

end