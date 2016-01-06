function data = load_sintel_results(dataType, iSeq, iFrame, method)
%%
if ischar(iSeq) 
    if ~isempty(str2num(iSeq))
        iSeq = str2num(iSeq);        
    else
        % input sequence name as a string
        seqName = iSeq;
    end
end

if ischar(iFrame)
    iFrame = str2num(iFrame);
end

%%%%%%%%%%%% load data
dataDir = fullfile('/data/vision/dqsun/data', dataType);
resultDir = fullfile('/data/vision/dqsun/sintel_results', method);
    
if ~exist(dataDir, 'file')
    % windows machine
    dataDir = fullfile('F:\data\flow\sintel', dataType);
    resultDir = fullfile('F:\result\flow\sintel', method);
    
    if ~exist(dataDir, 'file')
        % laptop
        dataDir = fullfile('C:\Users\dqsun\Documents\data\sintel', dataType);
        resultDir = fullfile('C:\Users\dqsun\Documents\results\flow\sintel', method);
%         dataDir = fullfile('C:\Users\dqsun\Dropbox\CVPR2013DS_Data\data_sintel_training\images');
%         resultDir = fullfile('C:\Users\dqsun\Documents\results\flow\sintel', method);
    end
end

if ~exist('seqName', 'var')
    % input sequence number
    seqNames = dir(dataDir);
    seqNames = seqNames(3:end);
    
    if iSeq > length(seqNames)
        return;
    end    
    seqName = seqNames(iSeq).name;
end

fnDir = fullfile(dataDir, seqName);
fns = dir(fnDir);
fns = fns(3:end);

if iFrame > length(fns)-1
    data = [];        
    return;
end

fn1 = fullfile(fnDir, fns(iFrame).name);
data.im1 = imread(fn1);
fn = fullfile(fnDir, fns(iFrame+1).name);
data.im2 = imread(fn);

fdir = fullfile(resultDir, 'flo', dataType, seqNames(iSeq).name);
fn   = fullfile(fdir, ['flow' fn1(end-7:end-3) 'flo']);
if ~exist(fn, 'file')
    fn   = fullfile(fdir, ['frame_' fn1(end-7:end-3) 'flo']);
    if ~exist(fn, 'file')
        fprintf('%s not computed\n', fn);
        % compute
        data = [];
        return;
    end
end;
data.uv = readFlowFile(fn);

fdir = fullfile(resultDir, 'png', dataType, seqNames(iSeq).name);

fn = fullfile(fdir, ['flow_edge' fn1(end-7:end)]);
if exist(fn, 'file');
    data.flowEdge = imread(fn);
end

fn = fullfile(fdir, ['flow_occ' fn1(end-7:end)]);
if exist(fn, 'file');
    data.occ = imread(fn);
end
    
fn = fullfile(fdir, ['flow_seg' fn1(end-7:end-3) 'mat']);
if exist(fn, 'file');
    s = load(fn, 'seg');
    data.seg = s.seg;
end

%% test code
if false
%%    
    dataType = 'training/clean';
    iSeq = 1;
    iFrame = 1;
    method = 'classic+nl-fast2';
    dataR = load_sintel_results(dataType, iSeq, iFrame, method);
%%    
end